"""How did our past BDBV Hub files do? Two figures from the hub clone and score_ebola_hub.py.

national-<release>.png: one panel per round of ACCIDDA-Chromantis, national weekly confirmed cases.
  Our median and 50% / 90% intervals for every week in the file, the counts as known when the file
  was made (the release the round used) and as known now (the scoring release), other teams'
  medians for the same round as thin grey lines.
relative-wis-<release>.png: our mean WIS divided by each other team's, on exactly the location-weeks
  both files cover, weeks at least two weeks old in the scoring release only (younger weeks are still
  far from complete), all rounds pooled; below 1 = we did better. Natural and log(1 + count) scale. Rounds made
  after the scoring release (their file already saw those counts) are left out.

    .venv/bin/python scripts/plot_ebola_performance.py data/ebola/hub-scores-2026-11-15.csv
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HUB = Path('production/hubs/BDBV-Modeling-Hub')
BLUE, BAND, INK, MUTED, GRID, OTHER = '#2a78d6', '#86b6ef', '#0b0b0b', '#52514e', '#e4e3df', '#b8b7b2'
LEVELS = ['country', 'province', 'health zone']


def main():
    scores = Path(sys.argv[1])
    release = scores.stem.split('hub-scores-')[1]
    out = scores.parent / f'performance-{release}'
    out.mkdir(exist_ok=True)
    t = pd.read_csv(HUB / 'target-data/time-series.csv')
    t = t[t.location == 'CD']
    now = t[t.as_of == release].set_index('target_end_date').observation
    ours = sorted((HUB / 'model-output/ACCIDDA-Chromantis').glob('*.csv'))
    runs = [(f, fd) for f in ours for fd in sorted(pd.read_csv(f, usecols=['forecast_date'], dtype=str).forecast_date.unique())]

    fig, axes = plt.subplots(1, len(runs), figsize=(4.2 * len(runs), 4.4), sharey=True)
    for ax, (f, fd) in zip(axes, runs):
        ref = f.name[:10]
        d = pd.read_csv(f, dtype={'forecast_date': str})
        d = d[(d.location == 'CD') & (d.forecast_date == fd)]
        q = d.groupby('target_end_date').value.quantile([.05, .25, .5, .75, .95]).unstack()
        w = pd.to_datetime(q.index)
        for f2 in sorted((HUB / 'model-output').glob(f'*/{ref}-*.csv')):
            if f2.parent.name in ('ACCIDDA-Chromantis', 'BDBVHub-baseline'):
                continue
            o = pd.read_csv(f2, dtype={'forecast_date': str})
            o = o[(o.location == 'CD') & (o.target == 'wk inc confirmed cases') & (o.output_type == 'sample')]
            if len(o):
                o = o[o.forecast_date == o.forecast_date.min()]
                m = o.groupby(pd.to_datetime(o.target_end_date, format='mixed', dayfirst=True)).value.median()
                ax.plot(m.index, m.values, color=OTHER, lw=.9, label='Other teams, median')
        ax.fill_between(w, q[.05], q[.95], color=BAND, alpha=.3, lw=0, label='Ours, 90% interval')
        ax.fill_between(w, q[.25], q[.75], color=BAND, alpha=.55, lw=0, label='Ours, 50% interval')
        ax.plot(w, q[.5], color=BLUE, lw=2, label='Ours, median')
        used = t[t.as_of == t[t.as_of < fd].as_of.max()]   # the release the round was made from
        used = used[used.target_end_date >= '2026-09-12']
        ax.plot(pd.to_datetime(used.target_end_date), used.observation, color=MUTED, lw=1, ls='--', marker='o', ms=3,
                mfc='white', label='Reported when the file was made')
        n = now[now.index >= '2026-09-12']
        ax.plot(pd.to_datetime(n.index), n.values, color=INK, lw=1.4, marker='o', ms=3.5, label=f'Reported in {release} release')
        ax.axvline(pd.Timestamp(ref) - pd.Timedelta(days=7), color=MUTED, lw=.8, ls=':')
        ax.set_title(f'Round {ref}\nforecast_date {fd}, data release {used.as_of.iloc[0]}', loc='left', fontsize=9.5)
        ax.grid(axis='y', color=GRID, lw=.8)
        ax.set_ylim(0, 900)
        ax.tick_params(axis='x', labelrotation=45, labelsize=8, colors=MUTED)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
    axes[0].set_ylabel('DRC confirmed cases per week (symptom onset)', color=MUTED)
    seen = {}
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(l, h)
    fig.legend(list(seen.values()), list(seen), loc='lower center', ncol=6, frameon=False, fontsize=8.5)
    fig.suptitle('ACCIDDA-Chromantis national files vs what was reported (dotted line: last data week of the round; '
                 'weeks left of it are nowcasts, right of it forecasts)', x=.01, ha='left', fontsize=10)
    fig.tight_layout(rect=(0, .07, 1, 1))
    fig.savefig(out / f'national-{release}.png', dpi=150)
    plt.close(fig)

    s = pd.read_csv(scores, dtype={'forecast_date': str})
    s['level'] = s.location.str.count('-').map(dict(enumerate(LEVELS)))
    s = s[(s.forecast_date == s.groupby(['model', 'reference_date']).forecast_date.transform('min')) & (s.lag_in_release >= 2)
          & (s.forecast_date <= release)]   # a round made from the scoring release itself only copies its data
    us = s[s.model == 'ACCIDDA-Chromantis']
    rows = []
    for m, g in s[(s.model != 'ACCIDDA-Chromantis')].groupby('model'):
        j = us.merge(g, on=['reference_date', 'location', 'week'], suffixes=('', '_o'))
        for lev, h in j.groupby('level'):
            rows.append(dict(model=m, level=lev, n=len(h), rounds=h.reference_date.nunique(),
                             natural=h.wis.mean() / h.wis_o.mean(), log=h.wis_log.mean() / h.wis_log_o.mean()))
    r = pd.DataFrame(rows)
    r.round(3).to_csv(out / f'relative-wis-{release}.csv', index=False)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharex=True)
    models = sorted(r.model.unique())
    for ax, lev in zip(axes, LEVELS):
        x = r[r.level == lev].set_index('model')
        for i, m in enumerate(models):
            if m in x.index:
                ax.plot([x.natural[m]], [i], 'o', color=BLUE, ms=7, label='Counts')
                ax.plot([x.log[m]], [i], 'D', color='#eb6834', ms=5, label='log(1 + counts)')
                ax.text(4.3, i, f'{x.n[m]} wk-loc, {x.rounds[m]} rnd', va='center', fontsize=7.5, color=MUTED)
        ax.axvline(1, color=INK, lw=.8)
        ax.set_xscale('log')
        ax.set_xlim(.2, 4)
        ax.set_xticks([.25, .5, 1, 2, 4], ['0.25', '0.5', '1', '2', '4'])
        ax.set_yticks(range(len(models)), models if lev == 'country' else [''] * len(models), fontsize=8.5)
        ax.set_title(lev, loc='left', fontsize=11)
        ax.grid(axis='x', color=GRID, lw=.8)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[:2], l[:2], loc='lower center', ncol=2, frameon=False, fontsize=9)
    fig.suptitle(f'Our mean WIS / other team\'s mean WIS on the same location-weeks (below 1 = ACCIDDA-Chromantis better). '
                 f'Scored against the {release} release,\nweeks ending at least two weeks before it, all rounds pooled '
                 '(nearly all nowcast weeks)', x=.01, ha='left', fontsize=10)
    fig.tight_layout(rect=(0, .07, .97, 1))
    fig.savefig(out / f'relative-wis-{release}.png', dpi=150)
    plt.close(fig)
    print(out)


if __name__ == '__main__':
    main()
