"""Backtest: rescale each held-out forecast so its week -1 median equals the last observed week (factor^alpha)."""
import numpy as np, pandas as pd
from pathlib import Path
from chromantis.experiment.planner import collect
root = Path('data/experiments/metrocast-ca-r03')
p = np.load('data/metrocast-california/panel.npz'); pdates = p['dates'].astype(str); py = p['targets'][..., 0]
def wis(q, y, lv):  # q [23, ...], y [...]
    return (2 * ((y <= q) - lv.reshape(-1, *[1] * y.ndim)) * (q - y)).mean(0)
rows = []
for r in collect(root):
    if r['status'] != 'complete': continue
    for folder in sorted((root/r['attempt']).glob('eval_*')):
        f = np.load(folder/'forecasts.npz')
        q = f['quantiles'][:, :, :5, 0, :]; y = f['truth'][:, :5, 0, :]; m = f['mask'][:, :5, 0, :].astype(bool); lv = f['quantile_levels']
        last = py[[list(pdates).index(d) for d in f['context_end']]]  # [ep, loc]
        med = q[list(np.round(lv, 3)).index(.5), :, 0, :]
        k = np.where((med > 0) & np.isfinite(last), last / np.maximum(med, 1e-9), 1.0)
        for alpha in (0, .5, 1):
            s = q * (k ** alpha)[None, :, None, :]
            w = wis(s, y, lv)
            n = m.sum((0, 1)); loc = np.where(m, w, 0).sum((0, 1)) / np.maximum(n, 1)
            h = [float(np.where(m[:, j], w[:, j], 0).sum() / max(m[:, j].sum(), 1)) for j in range(5)]
            rows.append(dict(name=r['name'], seed=r['seed'], season=folder.name[5:], alpha=alpha, wis=float(loc[n > 0].mean()), **{f'h{j-1}': h[j] for j in range(5)}))
d = pd.DataFrame(rows)
s = d.groupby(['name', 'alpha', 'season']).wis.mean().unstack()
s['mean'] = s.mean(1)
t = s['mean'].unstack('alpha'); t.columns = ['as is', 'half anchor', 'full anchor']
pd.set_option('display.width', 200)
print('Mean WIS, Hub weeks -1..3, mean over 4 held-out seasons (lower is better):'); print(t.sort_values('as is').round(1).to_string())
print('\nAll 18 recipes, mean by horizon:'); print(d.groupby('alpha')[['h-1', 'h0', 'h1', 'h2', 'h3']].mean().round(1).to_string())
print('\nBy season, mean over recipes:'); print(d.groupby(['alpha', 'season']).wis.mean().unstack().round(1).to_string())
