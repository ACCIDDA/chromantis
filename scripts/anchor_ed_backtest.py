"""Backtest on the ED 4-week winner r010_c08 (CV, 4 held-out seasons): scale each forecast by (last observed / week-0 median)^alpha."""
import numpy as np, pandas as pd, glob
p = np.load('data/metrocast-20261021/panel.npz'); pdates = p['dates'].astype(str); py = p['targets'][..., 0]
plocs = list(p['locations'])
rows = []
for path in sorted(glob.glob('data/experiments/metrocast-cv-r010/mlp-all-scheduled_final-f13f267ac7c3/s*/attempt-001/eval_*/forecasts.npz')):
    f = np.load(path); q = f['quantiles'][:, :, :, 0, :]; y = f['truth'][:, :, 0, :]; m = f['mask'][:, :, 0, :].astype(bool); lv = f['quantile_levels']
    li = [plocs.index(l) for l in f['locations']]
    last = py[[list(pdates).index(d) for d in f['context_end']]][:, li]
    t0 = py[[list(pdates).index(d) for d in f['target_dates'][:, 0]]][:, li]
    if not rows: print('unit check: truth h0 vs panel', np.nanmedian(y[:, 0] / t0))
    med = q[list(np.round(lv, 3)).index(.5), :, 0, :]
    k = np.where((med > 0) & np.isfinite(last) & (last > 0), last / np.maximum(med, 1e-12), 1.0)
    growth = np.where(np.isfinite(last) & (last > 0), med / np.maximum(last, 1e-12), np.nan)
    for alpha in (0, .25, .5):
        s = q * (k ** alpha)[None, :, None, :]
        w = (2 * ((y <= s) - lv.reshape(-1, 1, 1, 1)) * (s - y)).mean(0)
        for j in range(4):
            rows.append(dict(seed=path.split('/')[-3], season=path.split('/')[-2][5:], alpha=alpha, h=j, wis=float(w[:, j][m[:, j]].mean())))
d = pd.DataFrame(rows)
pd.set_option('display.width', 200)
base = d[d.alpha == 0].groupby(['season', 'h']).wis.mean()
for a in (.25, .5):
    print(f'alpha={a}: WIS / unanchored, by season (rows) and week (cols); <1 = anchoring helps')
    print((d[d.alpha == a].groupby(['season', 'h']).wis.mean() / base).unstack().round(3).to_string())
print('overall ratio', {a: round(d[d.alpha == a].wis.mean() / d[d.alpha == 0].wis.mean(), 3) for a in (.25, .5)})
