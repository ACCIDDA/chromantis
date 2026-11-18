"""Rank BDBV Hub models per location, on paired forecasts only (from score_ebola_hub.py output).

For each location, every pair of models is compared on exactly the (round, week) cells both files
cover: ratio of their mean WIS. A model's relative WIS at that location is the geometric mean of its
ratios against every other model scored there (pairwise relative skill, as the COVID/FluSight hubs
do), so models covering different rounds are never compared on different weeks. Rank 1 = lowest
relative WIS = best. Natural scale and log(1 + count) scale.

Rows: weeks at least MIN_LAG weeks old in the scoring release (default 5: from lag 5 on, the national count
moves by at most a few percent either way between releases, 9 Oct to 15 Nov 2026; lag 4 still grew 2-11%), each
model's first forecast_date per round, rounds made after the scoring release left out. Mean WIS below
FLOOR (a zone where both files put all mass on zero) is raised to FLOOR so ratios stay finite.

    .venv/bin/python scripts/rank_ebola_locations.py data/ebola/hub-scores-2026-11-15.csv [MIN_LAG]
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

US = 'ACCIDDA-Chromantis'
LEVELS = ['country', 'province', 'health zone']
FLOOR = {'wis': 0.01, 'wis_log': 0.001}
BLUE, INK, MUTED, GRID, OTHER = '#2a78d6', '#0b0b0b', '#52514e', '#e4e3df', '#b8b7b2'


def relative(g, col):
    """Pairwise relative WIS of every model at one location."""
    w = g.pivot_table(index=['reference_date', 'week'], columns='model', values=col)
    models = list(w.columns)
    out = []
    for a in models:
        logr, npair = [], []
        for b in models:
            if a == b:
                continue
            k = w[a].notna() & w[b].notna()
            if k.any():
                logr.append(np.log(max(w.loc[k, a].mean(), FLOOR[col]) / max(w.loc[k, b].mean(), FLOOR[col])))
                npair.append(k.sum())
        if logr:
            out.append(dict(model=a, rel=np.exp(np.mean(logr)), opponents=len(logr), weeks=int(w[a].notna().sum())))
    r = pd.DataFrame(out)
    r['rank'] = r.rel.rank(method='min').astype(int)
    r['n_models'] = len(r)
    return r


def main():
    scores = Path(sys.argv[1])
    min_lag = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    release = scores.stem.split('hub-scores-')[1]
    out = scores.parent / f'performance-{release}' / f'rank-lag{min_lag}'
    out.mkdir(parents=True, exist_ok=True)
    s = pd.read_csv(scores, dtype={'forecast_date': str})
    s = s[(s.forecast_date == s.groupby(['model', 'reference_date']).forecast_date.transform('min'))
          & (s.lag_in_release >= min_lag) & (s.forecast_date <= release)]
    s['level'] = s.location.str.count('-').map(dict(enumerate(LEVELS)))
    s = s[s.location.isin(s[s.model == US].location)]          # locations we submit
    rows = []
    for (lev, loc), g in s.groupby(['level', 'location']):
        for col, scale in [('wis', 'natural'), ('wis_log', 'log')]:
            r = relative(g, col)
            r['level'], r['location'], r['scale'] = lev, loc, scale
            rows.append(r)
    r = pd.concat(rows)
    r.round(4).to_csv(out / f'rank-per-location-{release}.csv', index=False)

    us = r[r.model == US].pivot_table(index=['level', 'location'], columns='scale', values=['rank', 'n_models', 'rel'])
    print(f'weeks ending on or before {s.week.max()} (lag >= {min_lag}); rows per round:',
          s[s.model == US].groupby('reference_date').week.unique().map(list).to_dict())
    print('ACCIDDA-Chromantis rank per location (1 = best), paired relative WIS:')
    for lev in LEVELS:
        u = r[(r.model == US) & (r.level == lev)]
        for scale in ['natural', 'log']:
            v = u[u.scale == scale]
            print(f'  {lev:12s} {scale:7s} {len(v):3d} locations: ranked 1st in {(v["rank"] == 1).sum()}, '
                  f'top half in {(v["rank"] <= np.ceil(v.n_models / 2)).sum()}, '
                  f'median rank {v["rank"].median():.0f} of median {v.n_models.median():.0f} models, '
                  f'geometric-mean relative WIS {np.exp(np.log(v.rel).mean()):.2f}')
    mean_rank = r.groupby(['level', 'scale', 'model']).agg(locations=('rank', 'size'), mean_rank=('rank', 'mean'),
                                                           mean_pct=('rank', lambda x: 0),
                                                           gm_rel=('rel', lambda x: np.exp(np.log(x).mean())))
    r['pct'] = (r['rank'] - 1) / (r.n_models - 1).clip(lower=1)        # 0 = best, 1 = worst at that location
    mean_rank['mean_pct'] = r.groupby(['level', 'scale', 'model']).pct.mean()
    mean_rank = mean_rank.round(3).sort_values(['level', 'scale', 'gm_rel'])
    mean_rank.to_csv(out / f'rank-by-model-{release}.csv')
    print(mean_rank.to_string())

    # one row per location: every model's relative WIS (grey), ours in blue, our rank on the right
    for scale in ['natural', 'log']:
        v = r[r.scale == scale]
        order = (v[v.model == US].assign(o=lambda d: d.level.map(LEVELS.index))
                 .sort_values(['o', 'rel'])[['level', 'location', 'rank', 'n_models']].reset_index(drop=True))
        fig, ax = plt.subplots(figsize=(7.5, 0.17 * len(order) + 1.4))
        for i, row in order.iterrows():
            g = v[v.location == row.location]
            ax.scatter(g[g.model != US].rel, [i] * (len(g) - 1), s=10, color=OTHER, lw=0, zorder=2)
            ax.scatter(g[g.model == US].rel, [i], s=22, color=BLUE, lw=0, zorder=3)
            ax.text(1.01, i, f'{row["rank"]}/{row.n_models}', transform=ax.get_yaxis_transform(), va='center',
                    fontsize=6, color=MUTED)
        for k, lev in enumerate(LEVELS[:-1]):
            ax.axhline(order.index[order.level == lev].max() + 0.5, color=MUTED, lw=0.6)
        ax.axvline(1, color=MUTED, lw=0.8, ls=':')
        ax.set_xscale('log')
        ax.set_yticks(range(len(order)), order.location, fontsize=6, color=INK)
        ax.set_ylim(len(order) - 0.5, -0.5)
        ax.grid(axis='x', color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for sp in ['top', 'right', 'left']:
            ax.spines[sp].set_visible(False)
        ax.tick_params(axis='y', length=0)
        ax.set_xlabel(f'Pairwise relative WIS at that location ({scale} scale), lower is better', fontsize=8)
        ax.set_title(f'Rank per location against the {release} release (blue = ACCIDDA-Chromantis, grey = other '
                     f'teams;\nright = our rank / models scored there). Paired weeks only, weeks at least two weeks '
                     f'old, rounds made before the release.', loc='left', fontsize=8)
        fig.tight_layout()
        fig.savefig(out / f'rank-per-location-{scale}-{release}.png', dpi=150)
        plt.close(fig)
    print(out)


if __name__ == '__main__':
    main()
