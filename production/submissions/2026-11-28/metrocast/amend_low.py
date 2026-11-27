"""Remove MetroCast forecasts in the bottom 10% of the other models (user request, 26 Nov: no forecast where we are lowest).

For each location and target whose median is below 90% of the other models' medians (sample medians; at least 3
models) at any week 0-3 (California: -1..3), step: our trajectories -> 50 ours + 50 pooled -> 100 pooled, repeated
until none is left. Pooled = equal shares of 100 trajectories drawn without replacement from the other teams'
submitted samples (not epiENGAGE-baseline) that cover every one of those weeks (seed 0), after dropping each
team's 2% highest and 2% lowest trajectories at 19 Dec (some teams submit paths up to 100% of ED visits). After week 3 (19 Dec) each
pooled trajectory continues with one of our trajectories, matched by rank at 19 Dec (same rule as splice.py).
Usage: python amend_low.py IN.parquet OUT.parquet
"""
import glob, sys
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
hub = '../../../hubs/flu-metrocast'
rng = np.random.default_rng(0)
ours = pd.read_parquet(sys.argv[1])
for d in (ours,):
    d['target_end_date'] = pd.to_datetime(d.target_end_date).dt.date; d['reference_date'] = pd.to_datetime(d.reference_date).dt.date
END = pd.Timestamp('2026-12-19').date()
WEEKS = {'Flu ED visits pct': [pd.Timestamp(x).date() for x in ('2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')],
         'Flu hosp admits': [pd.Timestamp(x).date() for x in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')]}
peers = {}
for f in glob.glob(f'{hub}/model-output/*/2026-11-28-*.parquet'):
    m = f.split('/')[-2]
    if 'Chromantis' in m: continue
    d = pd.read_parquet(f); d['target_end_date'] = pd.to_datetime(d.target_end_date).dt.date
    peers[m] = d[d.output_type == 'sample']
pmed = pd.concat([d.groupby(['target', 'location', 'target_end_date']).value.median().rename(m) for m, d in peers.items()], axis=1)

def low_keys(f):
    o = f.groupby(['target', 'location', 'target_end_date']).value.median().rename('ours')
    x = pmed.join(o, how='inner')
    x = x[[w in WEEKS[t] for t, _, w in x.index]]
    n = x[pmed.columns].notna().sum(axis=1)
    pct = x[pmed.columns].lt(x.ours, axis=0).sum(axis=1) / n
    return sorted({(t, l) for (t, l, _) in pct[(pct < 0.10) & (n >= 3)].index})

def pooled(target, loc, k):
    """k pooled trajectories over WEEKS[target], as a (k, weeks) array."""
    w = WEEKS[target]; paths = []
    for m, d in peers.items():
        if m == 'epiENGAGE-baseline': continue
        s = d[(d.target == target) & (d.location == loc) & d.target_end_date.isin(w)]
        t = s.pivot_table(index='output_type_id', columns='target_end_date', values='value')
        if t.shape[1] == len(w):
            v = t[w].dropna().values
            lo, hi = np.quantile(v[:, -1], [0.02, 0.98])
            paths.append(v[(v[:, -1] >= lo) & (v[:, -1] <= hi)])   # drop each team's 2% extreme trajectories at week 3
    take = np.array_split(np.arange(k), len(paths))
    return np.vstack([p[rng.choice(len(p), len(i), replace=len(p) < len(i))] for p, i in zip(paths, take)]), len(paths)

def rebuild(f, target, loc, share):
    """Replace a share (0.5 or 1) of the location's trajectories by pooled ones over WEEKS, keeping our tails."""
    a = f[(f.target == target) & (f.location == loc)]
    ids = sorted(a.output_type_id.unique(), key=lambda s: int(s[1:]))
    wide = a.pivot_table(index='output_type_id', columns='target_end_date', values='value').loc[ids]
    k = int(round(share * len(ids)))
    replace = ids if k == len(ids) else list(rng.choice(ids, k, replace=False))
    P, nmod = pooled(target, loc, k)
    w = WEEKS[target]
    # tails: our trajectories ranked at END, given to the pooled paths by their rank at END
    tails = wide.loc[replace].sort_values(END)
    order = np.argsort(P[:, -1])
    for r, i in enumerate(order):
        wide.loc[tails.index[r], w] = P[i]
    out = wide.stack().rename('value').reset_index()
    for c in ('reference_date', 'target', 'location', 'output_type'):
        out[c] = a[c].iloc[0]
    return pd.concat([f[~((f.target == target) & (f.location == loc))], out[f.columns]]), nmod

state, log = {}, []
for it in range(3):
    keys = [k for k in low_keys(ours) if state.get(k, 0) < 2]
    print('iteration', it, 'bottom-10% (target, location):', len(keys))
    if not keys: break
    for k in keys:
        state[k] = state.get(k, 0) + 1
        share = 0.5 if state[k] == 1 else 1.0
        if state[k] == 2:   # second step: from the file before any pooling, 100 pooled
            base = pd.read_parquet(sys.argv[1]); base['target_end_date'] = pd.to_datetime(base.target_end_date).dt.date
            base['reference_date'] = pd.to_datetime(base.reference_date).dt.date
            ours = pd.concat([ours[~((ours.target == k[0]) & (ours.location == k[1]))], base[(base.target == k[0]) & (base.location == k[1])]])
        ours, nmod = rebuild(ours, k[0], k[1], share)
        log.append((it, *k, share, nmod))
left = low_keys(ours)
print('left in bottom 10%:', left)
ours = ours.sort_values(['target', 'location', 'output_type_id', 'target_end_date'])
assert ours.groupby(['target', 'location', 'target_end_date']).output_type_id.nunique().eq(100).all()
pd.DataFrame(log, columns=['iteration', 'target', 'location', 'pooled_share', 'models_pooled']).to_csv('low-amendments.csv', index=False)
prev = pq.read_schema('../../2026-11-21/metrocast/2026-11-21-ACCIDDA-Chromantis.parquet').remove_metadata()
pq.write_table(pa.Table.from_pandas(ours[[f.name for f in prev]], schema=prev, preserve_index=False), sys.argv[2])
fin = pd.DataFrame(log).groupby([1, 2])[3].max().value_counts().to_dict()
print('final pooled share per (target, location):', fin, '| rows', len(ours))
