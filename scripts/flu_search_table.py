"""Round table of the flu search (experiments/flu-search-20261120), with the verdict of each child against its parent.
Also used by the COVID/RSV search (experiments/covid-rsv-search-20261124): --pathogen covid|rsv --parents '<glob of round files>'.
For RSV the 2023-24 guard has no admissions (NHSN RSV unobserved before Nov 2024), so its guard score is ED share
(column ged, natural WIS x 1e4) and the guard rule compares it relatively (child not worse by more than the margin in %).

Scores: mean WIS of log(1 + flu admissions) over the 50 states and DC, Hub horizons 0-3, October-May reference dates,
each recipe's deployed view; lower is better; averaged over seeds.
  s2425, s2526  main problem (us-flu-short-term-coverage): each season held out in turn, trained on the other seasons
                of 2022-23..2025-26 with finalized labels, evaluated on that season's archived Wednesday reports.
  primary       mean of s2425 and s2526 (seasons equal), the selection score.
  g2324         guard (us-flu-2023-24-prescribed-coverage): 2023-24 held out, trained on 2022-23, 2024-25 and 2025-26,
                evaluated on artificial preliminary 2023-24 reports (2025-26 reporting errors, 3 draws).
  oct           primary restricted to October reference dates (early season), from the planner's ranking.
  us            the same WIS for the national total, seasons equal.  ed  ED-share WIS x 1e4 (2025-26 only), states/DC.
  hub2425/hub2526  pairwise relative WIS against the FluSight Hub models of that season (log scale; 1 = Hub baseline).
Verdict (pre-registered, protocol.json): a child is 'better' than its parent only if its primary is lower by more than
max(2 x standard error of the difference of seed means, 1% of the parent) AND it is lower in both seasons AND its guard
is not worse by more than that margin; 'worse' if higher by more than the margin; otherwise 'level'.

    .venv/bin/python scripts/flu_search_table.py -e flu-s-r01 [-e ...] --guard flu-s-g01 [--guard ...] --out table.csv
"""
import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd

HOSP, ED = 'wk inc flu hosp', 'wk inc flu prop ed visits'


def ranking(experiment):
    dirs = sorted(Path('data/experiments', experiment).glob('ranking-*/headline-season-scores.csv'), key=lambda p: p.stat().st_mtime)
    return dirs[-1].parent if dirs else None


def load(experiments):
    seasons, seeds, ranks, hub = [], [], [], []
    for e in experiments:
        r = ranking(e)
        if r is None:
            continue
        seasons.append(pd.read_csv(r / 'headline-season-scores.csv'))
        seeds.append(pd.read_csv(r / 'headline-seed-scores.csv'))
        ranks.append(pd.read_csv(r / 'headline-rankings.csv'))
        if (r / 'hub-pairwise-scores.csv').exists():
            hub.append(pd.read_csv(r / 'hub-pairwise-scores.csv'))
    cat = lambda x: pd.concat(x) if x else pd.DataFrame()
    return cat(seasons), cat(seeds), cat(ranks), cat(hub)


def sel(t, target=None, scale='log', geography='states_dc'):
    t = t[t.deployed]
    target = target or HOSP
    return t[(t.target == target) & (t.scale == scale) & (t.geography == geography)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--experiment', action='append', required=True)
    ap.add_argument('--guard', action='append', default=[])
    ap.add_argument('--out', type=Path)
    ap.add_argument('--only', nargs='*', help='restrict to these recipe names')
    ap.add_argument('--pathogen', default='flu', choices=('flu', 'covid', 'rsv'))
    ap.add_argument('--parents', default='experiments/flu-search-20261120/round-*.json', help='glob of study files with parents')
    a = ap.parse_args()
    global HOSP, ED
    HOSP, ED = f'wk inc {a.pathogen} hosp', f'wk inc {a.pathogen} prop ed visits'
    seasons, seeds, ranks, hub = load(a.experiment)
    s = sel(seasons).pivot_table(index='name', columns='season', values='mean_wis')
    rows = pd.DataFrame({'s2425': s.get('2024-2025'), 's2526': s.get('2025-2026')})
    rows.insert(0, 'primary', rows.mean(axis=1))
    sd = sel(seeds).groupby('name').score.agg(['std', 'count'])
    rows['sd'], rows['n'] = sd['std'], sd['count']
    if a.guard:
        gs, gseeds, _, _ = load(a.guard)
        if len(gs):
            rows['g2324'] = sel(gs).groupby('name').mean_wis.mean()
            g = sel(gseeds).groupby('name').score.agg(['std', 'count'])
            rows['gsd'], rows['gn'] = g['std'], g['count']
            rows['ged'] = sel(gs, ED, 'natural').groupby('name').mean_wis.mean() * 1e4
    rows['oct'] = sel(ranks).groupby('name').october.mean()
    rows['us'] = sel(seasons, geography='US').groupby('name').mean_wis.mean()
    ed = sel(seasons, ED, 'natural')
    rows['ed'] = ed[ed.season == '2025-2026'].groupby('name').mean_wis.mean() * 1e4
    rows['edm'] = ed.groupby('name').mean_wis.mean() * 1e4  # both seasons, equal
    cov = sel(seasons)
    rows['cov50'] = cov.groupby('name').covered_50.mean()
    rows['cov90'] = cov.groupby('name').covered_90.mean()
    if len(hub):
        h = hub[hub.ours & hub.deployed & (hub.scale == 'log') & (hub.target == HOSP)]
        hp = h.pivot_table(index='name', columns='season', values='relative_wis')
        rows['hub2425'], rows['hub2526'] = hp.get('2024-2025'), hp.get('2025-2026')
    parents = {}
    for f in glob.glob(a.parents):
        parents.update(json.load(open(f)).get('parents', {}))
    rows['parent'] = [parents.get(n, '') for n in rows.index]
    verdict, delta = [], []
    for n, r in rows.iterrows():
        p = r.parent
        if not p or p not in rows.index or pd.isna(r.primary) or pd.isna(rows.at[p, 'primary']):
            verdict.append(''); delta.append(np.nan); continue
        q = rows.loc[p]
        se = np.sqrt(r.sd ** 2 / r.n + q.sd ** 2 / q.n)
        margin = max(2 * se, .01 * q.primary)
        d = q.primary - r.primary
        delta.append(-d / q.primary * 100)
        both = r.s2425 < q.s2425 and r.s2526 < q.s2526
        if 'g2324' in rows and not pd.isna(r.get('g2324')) and not pd.isna(q.get('g2324')):
            guard_ok = r.g2324 - q.g2324 <= margin
        elif 'ged' in rows and not pd.isna(r.get('ged')) and not pd.isna(q.get('ged')):
            guard_ok = (r.ged - q.ged) / q.ged <= margin / q.primary
        else:
            guard_ok = True
        verdict.append('better' if d > margin and both and guard_ok else 'worse' if d < -margin else 'level')
    rows['vs_parent_%'] = delta
    rows['verdict'] = verdict
    rows = rows.sort_values('primary')
    if a.only:
        rows = rows.loc[[n for n in rows.index if n in a.only]]
    if a.out:
        rows.to_csv(a.out, float_format='%.5g')
    pd.set_option('display.width', 250, 'display.max_columns', 40, 'display.max_rows', 400)
    show = [c for c in ('primary', 's2425', 's2526', 'g2324', 'ged', 'oct', 'us', 'ed', 'edm', 'cov50', 'cov90', 'hub2425', 'hub2526',
                        'sd', 'n', 'parent', 'vs_parent_%', 'verdict') if c in rows]
    print(rows[show].round(4).to_string())


if __name__ == '__main__':
    main()
