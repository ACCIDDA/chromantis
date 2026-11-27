"""Amended 28 Nov FluSight file: state-by-state choice between masked A and the median of the other Hub models.

Evidence per state (scratch evidence-20261125.csv, panel data/operational-20261125/processed/panel-indicators.npz on
Longleaf, reports as of 25 Nov 2026): newest-week growth of flu ED share, NHSN flu admissions x 1.05 (median later
revision of a first report), NWSS wastewater index, ILINet and clinical-lab positivity (the last two through 14 Nov;
a one-week drop below 0.6 is treated as an incomplete report). A signal is rising if growth > 1.05.
Only states where masked A's week-3 median is below its week-0 median are changed:
  share of rising signals > 0.6 -> median of the other Hub models (quantile by quantile);
  0.4 <= share <= 0.6           -> 50/50 average of masked A and that median, quantile by quantile;
  share < 0.4                   -> masked A unchanged.
The same choice applies to both weekly targets of a state; the peak targets are unchanged.
Then (user request: no forecast where we are the lowest): any location whose median, for either weekly target at any
horizon 0-3, is below 90% of the other models' medians (bottom 10%, FluSight-baseline included) moves one step,
masked A -> 50/50 -> peer median, repeated until none is left.
"""
import glob, sys
import numpy as np, pandas as pd
dec_csv = sys.argv[1]
H = 'production/hubs/FluSight-forecast-hub'
O = 'production/output/2026-11-25'
ab = pd.read_csv(f'{H}/auxiliary-data/locations.csv', dtype=str).set_index('abbreviation').location
t = pd.read_csv(dec_csv, index_col=0)
t['share'] = t.rising / t.n
t['choice'] = 'masked A'
t.loc[t.ours_falls & (t.share > 0.6), 'choice'] = 'peer median'
t.loc[t.ours_falls & (t.share >= 0.4) & (t.share <= 0.6), 'choice'] = '50/50'
ours = pd.read_csv(f'{O}/combined-masked-a-20261122/2026-11-28-ACCIDDA-Chromantis.csv', dtype={'location': str, 'output_type_id': str})
weekly = ours.target.isin(['wk inc flu hosp', 'wk inc flu prop ed visits'])
peers = []
for f in glob.glob(f'{H}/model-output/*/2026-11-28-*.csv') + glob.glob(f'{H}/model-output/*/2026-11-28-*.parquet'):
    m = f.split('/')[-2]
    if m in ('ACCIDDA-Chromantis', 'FluSight-baseline', 'FluSight-ensemble'): continue
    d = pd.read_parquet(f) if f.endswith('parquet') else pd.read_csv(f, dtype={'location': str, 'output_type_id': str})
    d = d[d.target.isin(['wk inc flu hosp', 'wk inc flu prop ed visits']) & (d.output_type == 'quantile') & d.horizon.between(0, 3)].copy()
    d['location'] = d.location.astype(str); d['level'] = d.output_type_id.astype(float).round(3); d['model'] = m
    n = d.groupby(['location', 'target', 'horizon'])['level'].transform('nunique')
    peers.append(d[n == 23][['model', 'location', 'target', 'horizon', 'level', 'value']])
peers = pd.concat(peers)
pm = peers.groupby(['location', 'target', 'horizon', 'level']).agg(peer=('value', 'median'), models=('model', 'nunique'))
w = ours[weekly].copy(); w['level'] = w.output_type_id.astype(float).round(3)
w = w.join(pm, on=['location', 'target', 'horizon', 'level'])
w0 = w.copy()
ab_inv = {v: k for k, v in ab.items()}
b = pd.read_csv(glob.glob(f'{H}/model-output/FluSight-baseline/2026-11-28-*.csv')[0], dtype={'location': str, 'output_type_id': str})
b = b[b.output_type == 'quantile']
base = b[(b.output_type_id.astype(float).round(3) == 0.5) & b.horizon.between(0, 3) & b.target.str.startswith('wk inc')]
med = pd.concat([peers[peers.level == 0.5], base])[['location', 'target', 'horizon', 'value']].rename(columns={'value': 'pv'})
def build(choice):
    w = w0.copy()
    w['choice'] = w.location.map({ab[s]: c for s, c in choice.items() if s in ab}).fillna('masked A')
    assert w.loc[w.choice != 'masked A', 'peer'].notna().all()
    new = np.select([w.choice == 'peer median', w.choice == '50/50'], [w.peer, 0.5 * (w.value + w.peer)], w.value)
    w['value'] = np.where(w.target == 'wk inc flu hosp', np.round(new), new)
    return w.sort_values(['location', 'target', 'horizon', 'level'])
choice = t.choice.copy()
step = {'masked A': '50/50', '50/50': 'peer median'}
for it in range(3):
    w = build(choice)
    m = w[w.level == 0.5][['location', 'target', 'horizon', 'value']]
    x = med.merge(m, on=['location', 'target', 'horizon'])
    pct = (x.pv < x.value).groupby([x.location, x.target, x.horizon]).mean()
    low = sorted({ab_inv[l] for (l, _, _) in pct[pct < 0.10].index if l in ab_inv})
    low = [s for s in low if choice.get(s) != 'peer median']
    print('iteration', it, 'bottom-10% locations:', low)
    if not low: break
    for s in low: choice[s] = step[choice.get(s, 'masked A')]
t['choice'] = choice
assert (w.groupby(['location', 'target', 'horizon']).value.diff().dropna() >= 0).all(), 'quantiles not ordered'
out = pd.concat([w[ours.columns], ours[~weekly]])
assert len(out) == len(ours)
out.to_csv(f'{O}/amended/2026-11-28-ACCIDDA-Chromantis.csv', index=False)
print(t.choice.value_counts().to_dict())
print('models in the peer median (min/median), hosp:', pm.xs('wk inc flu hosp', level=1).models.min(), pm.xs('wk inc flu hosp', level=1).models.median(),
      '| ED:', pm.xs('wk inc flu prop ed visits', level=1).models.min(), pm.xs('wk inc flu prop ed visits', level=1).models.median())
print({c: sorted(s for s, v in t.choice.items() if v == c) for c in ('peer median', '50/50')})
