"""Score every MetroCast model's past Flu-ED files (horizons 0-3) against the Hub's latest target data.

Usage: python score_past.py HUB_DIR OUT_CSV REF [REF ...]
WIS = mean over the 23 Hub quantile levels of 2 x pinball loss; the 100 sample trajectories are
turned into those 23 empirical quantiles first. Only weeks already observed are scored. Pairwise
relative WIS follows FluSight: theta_m = geometric mean over other models m' of mean WIS(m)/mean
WIS(m') on their common tasks, divided by epiENGAGE-baseline's theta. Lower is better; 1 = baseline.
"""
import glob
import sys

import numpy as np
import pandas as pd

hub, out, refs = sys.argv[1], sys.argv[2], sys.argv[3:]
Q = np.array([.01, .025, *np.round(np.arange(.05, .96, .05), 2), .975, .99])
BASE = 'epiENGAGE-baseline'
truth = pd.read_csv(f'{hub}/target-data/latest-data.csv')
truth = truth[truth.target == 'Flu ED visits pct'].rename(columns={'observation': 'y'})[['location', 'target_end_date', 'y']]

rows = []
for ref in refs:
    for path in glob.glob(f'{hub}/model-output/*/{ref}-*.parquet') + glob.glob(f'{hub}/model-output/*/{ref}-*.csv'):
        model = path.split('/')[-2]
        f = pd.read_parquet(path) if path.endswith('.parquet') else pd.read_csv(path)
        f = f[(f.target == 'Flu ED visits pct') & (f.output_type == 'sample')].copy()
        f['target_end_date'] = pd.to_datetime(f.target_end_date).dt.strftime('%Y-%m-%d')
        f['horizon'] = (pd.to_datetime(f.target_end_date) - pd.Timestamp(ref)).dt.days // 7
        f = f[f.horizon.between(0, 3)]
        q = f.groupby(['location', 'target_end_date', 'horizon']).value.quantile(Q).rename_axis(
            ['location', 'target_end_date', 'horizon', 'q']).reset_index()
        q = q.merge(truth, on=['location', 'target_end_date'])
        q['pin'] = 2 * ((q.y <= q.value).astype(float) - q.q) * (q.value - q.y)
        w = q.groupby(['location', 'target_end_date', 'horizon']).pin.mean().rename('wis').reset_index()
        rows.append(w.assign(model=model, ref=ref))
s = pd.concat(rows)
s.to_csv(out, index=False)


def pairwise(s):
    w = s.set_index(['model', 'ref', 'location', 'target_end_date']).wis.unstack('model')
    theta = {}
    for m in w.columns:
        r = [1.0] + [w[[m, m2]].dropna()[m].mean() / w[[m, m2]].dropna()[m2].mean() for m2 in w.columns if m2 != m and w[[m, m2]].dropna().size]
        theta[m] = np.exp(np.mean(np.log(r)))
    theta = pd.Series(theta)
    return (theta / theta[BASE]).sort_values()


print('Pairwise relative WIS, all rounds', refs, 'horizons 0-3 observed so far (1 = baseline, lower is better)')
p = pairwise(s)
n = s.groupby('model').size()
print(pd.DataFrame(dict(rel_wis=p.round(3), tasks=n[p.index])).to_string())
p.rename('rel_wis').to_csv(out.replace('.csv', '-pairwise.csv'))
print('\nOurs / baseline mean WIS on the same tasks, by round and horizon')
w = s.set_index(['model', 'ref', 'horizon', 'location', 'target_end_date']).wis.unstack('model')[['ACCIDDA-Chromantis', BASE]].dropna()
r = w.groupby(['ref', 'horizon']).mean()
print((r['ACCIDDA-Chromantis'] / r[BASE]).round(2).unstack('horizon').to_string())
