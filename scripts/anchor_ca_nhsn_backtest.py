"""Backtest: anchor California week -1 on last observed x NHSN growth into week -1 (revised NHSN; optimistic)."""
import numpy as np, pandas as pd
from pathlib import Path
from chromantis.experiment.planner import collect
root = Path('data/experiments/metrocast-ca-r03')
p = np.load('data/metrocast-california/panel.npz'); pdates = list(p['dates'].astype(str)); py = p['targets'][..., 0]
nh = pd.read_csv('scripts/nhsn_ca.csv', index_col=0).nhsn
rows = []
for r in collect(root):
    if r['status'] != 'complete': continue
    for folder in sorted((root/r['attempt']).glob('eval_*')):
        f = np.load(folder/'forecasts.npz')
        q = f['quantiles'][:, :, :5, 0, :]; y = f['truth'][:, :5, 0, :]; m = f['mask'][:, :5, 0, :].astype(bool); lv = f['quantile_levels']
        last = py[[pdates.index(d) for d in f['context_end']]]
        g = np.array([nh.get(t, np.nan) / nh.get(c, np.nan) for c, t in zip(f['context_end'], f['target_dates'][:, 0])])
        g = np.where(np.isfinite(g) & (g > 0), g, 1.0)[:, None]
        med = q[list(np.round(lv, 3)).index(.5), :, 0, :]
        for name, target, alpha in [('as is', last, 0), ('half anchor', last, .5), ('full anchor', last, 1),
                                    ('half anchor x NHSN growth', last * g, .5), ('full anchor x NHSN growth', last * g, 1)]:
            k = np.where((med > 0) & np.isfinite(target), target / np.maximum(med, 1e-9), 1.0) ** alpha
            s = q * k[None, :, None, :]
            w = (2 * ((y <= s) - lv.reshape(-1, 1, 1, 1)) * (s - y)).mean(0)
            h = {f'h{j-1}': float(w[:, j][m[:, j]].mean()) for j in range(5)}
            rows.append(dict(name=r['name'], season=folder.name[5:], rule=name, **h))
d = pd.DataFrame(rows); d['all'] = d[['h-1', 'h0', 'h1', 'h2', 'h3']].mean(1)
pd.set_option('display.width', 200)
order = ['as is', 'half anchor', 'full anchor', 'half anchor x NHSN growth', 'full anchor x NHSN growth']
print('Mean WIS over 18 recipes, 4 held-out seasons, by week (lower is better):'); print(d.groupby('rule')[['h-1', 'h0', 'h1', 'h2', 'h3', 'all']].mean().loc[order].round(1).to_string())
print('\nBy season (all weeks):'); print(d.groupby(['rule', 'season'])['all'].mean().unstack().loc[order].round(1).to_string())
nine = ['wide_cov_tp_state_ed_raw', 'ref_wide', 'wide_path', 'ref_log1p', 'ref_path', 'ref_ili', 'log1p_cov_tp_state', 'cov_tp_growth_drop0.25', 'wide_log1p']
print('\nThe 9 submitted recipes only:'); print(d[d.name.isin(nine)].groupby('rule')[['h-1', 'h0', 'h1', 'h2', 'h3', 'all']].mean().loc[order].round(1).to_string())
