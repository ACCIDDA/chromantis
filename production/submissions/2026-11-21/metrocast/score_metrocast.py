"""Score every MetroCast model's submitted files against the Hub's latest target data, both targets.

Usage: python score_metrocast.py HUB_DIR OUT_PREFIX REF [REF ...]
WIS = mean over the 23 Hub quantile levels of 2 x pinball loss, from the 100 sample trajectories
turned into those 23 empirical quantiles. Only weeks already observed are scored; ED horizons 0-3,
California admissions -1..3. Pairwise relative WIS follows FluSight: theta_m = geometric mean over
other models m' of mean WIS(m)/mean WIS(m') on their common tasks, divided by epiENGAGE-baseline's.
Lower is better; 1 = baseline. Also: bias and interval coverage per horizon, and how much the first
report of a week is revised later (time-series.csv vintages).
"""
import glob
import sys

import numpy as np
import pandas as pd

hub, out, refs = sys.argv[1], sys.argv[2], sys.argv[3:]
Q = np.array([.01, .025, *np.round(np.arange(.05, .96, .05), 2), .975, .99])
BASE, US, ENS = 'epiENGAGE-baseline', 'ACCIDDA-Chromantis', 'epiENGAGE-ensemble_short'
HORIZONS = {'Flu ED visits pct': (0, 3), 'Flu hosp admits': (-1, 3)}
truth = pd.read_csv(f'{hub}/target-data/latest-data.csv').rename(columns={'observation': 'y'})[['target', 'location', 'target_end_date', 'y']]
pd.set_option('display.width', 200)

rows = []
for ref in refs:
    for path in glob.glob(f'{hub}/model-output/*/{ref}-*.parquet') + glob.glob(f'{hub}/model-output/*/{ref}-*.csv'):
        f = pd.read_parquet(path) if path.endswith('.parquet') else pd.read_csv(path)
        f = f[f.output_type == 'sample'].copy()
        f['target_end_date'] = pd.to_datetime(f.target_end_date).dt.strftime('%Y-%m-%d')
        f['horizon'] = (pd.to_datetime(f.target_end_date) - pd.Timestamp(ref)).dt.days // 7
        lo = f.target.map(lambda t: HORIZONS[t][0]); hi = f.target.map(lambda t: HORIZONS[t][1])
        f = f[(f.horizon >= lo) & (f.horizon <= hi)]
        keys = ['target', 'location', 'target_end_date', 'horizon']
        q = f.groupby(keys).value.quantile(Q).rename_axis(keys + ['q']).reset_index().merge(truth, on=keys[:3])
        q['pin'] = 2 * ((q.y <= q.value).astype(float) - q.q) * (q.value - q.y)
        w = q.groupby(keys).agg(wis=('pin', 'mean'), y=('y', 'first')).reset_index()
        qq = q.pivot_table(index=keys, columns='q', values='value').reset_index()
        w = w.merge(qq[keys + [.05, .25, .5, .75, .95]].rename(columns={.05: 'q05', .25: 'q25', .5: 'q50', .75: 'q75', .95: 'q95'}), on=keys)
        rows.append(w.assign(model=path.split('/')[-2], ref=ref))
s = pd.concat(rows)
s.to_csv(f'{out}-scores.csv', index=False)


def pairwise(s):
    w = s.set_index(['model', 'ref', 'location', 'target_end_date', 'horizon']).wis.unstack('model')
    theta = {}
    for m in w.columns:
        r = [1.0] + [w[[m, m2]].dropna()[m].mean() / w[[m, m2]].dropna()[m2].mean() for m2 in w.columns if m2 != m and len(w[[m, m2]].dropna())]
        theta[m] = np.exp(np.mean(np.log(r)))
    theta = pd.Series(theta)
    return (theta / theta[BASE]).sort_values()


def rank(p, m=US):
    return f'{p[m]:.3f} (rank {list(p.index).index(m) + 1} of {len(p)})' if m in p else '-'


for target, t in s.groupby('target'):
    print(f'\n===== {target} =====')
    p = pairwise(t)
    print('All files', sorted(t.ref.unique()), 'pairwise relative WIS (1 = baseline, lower is better):')
    print(pd.DataFrame(dict(rel_wis=p.round(3), tasks=t.groupby('model').size()[p.index])).to_string())
    p.rename('rel_wis').to_csv(f'{out}-pairwise-{target.replace(" ", "_")}.csv')
    print('\nOurs by file:', {r: rank(pairwise(g)) for r, g in t.groupby('ref')})
    print('Ours by horizon:', {h: rank(pairwise(g)) for h, g in t.groupby('horizon')})
    print('Ensemble_short by horizon:', {h: rank(pairwise(g), ENS) for h, g in t.groupby('horizon')})
    print('\nCalibration by horizon (all files): share of observations below the median (0.5 ideal),'
          '\ninside the 50% and 90% intervals (0.5 / 0.9 ideal), median of forecast median / observed (1 ideal):')
    for m in [US, ENS, BASE] + list(p.index[:2]):
        g = t[t.model == m]
        if not len(g):
            continue
        c = g.groupby('horizon').apply(lambda d: pd.Series(dict(
            below_median=(d.y < d.q50).mean(), in50=((d.y >= d.q25) & (d.y <= d.q75)).mean(),
            in90=((d.y >= d.q05) & (d.y <= d.q95)).mean(), median_over_obs=(d.q50 / d.y.clip(lower=1e-9)).median(), n=len(d))), include_groups=False)
        print(f'-- {m}'); print(c.round(2).to_string())

ts = pd.read_csv(f'{hub}/target-data/time-series.csv')
ts = ts[ts.as_of >= '2026-10-01']
first = ts.sort_values('as_of').groupby(['target', 'location', 'target_end_date']).first().reset_index()
first = first[first.as_of.astype(str) > first.target_end_date.astype(str)]
last = ts.sort_values('as_of').groupby(['target', 'location', 'target_end_date']).observation.last().rename('latest')
r = first.merge(last.reset_index(), on=['target', 'location', 'target_end_date'])
r = r[(r.target_end_date >= '2026-10-10') & (r.as_of != r.groupby(['target', 'location', 'target_end_date']).as_of.transform('max'))]
r['ratio'] = r.latest / r.observation.where(r.observation > 0)
print('\nRevision of the first report of each week, 2026-27 (latest / first; >1 = revised up):')
print(r.groupby(['target', 'target_end_date']).ratio.describe(percentiles=[.1, .5, .9])[['count', '10%', '50%', '90%']].round(3).to_string())
