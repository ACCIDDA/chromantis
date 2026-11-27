"""Per-state growth of every flu signal in the newest week, as reported by 25 November 2026."""
import numpy as np, pandas as pd
from chromantis.dataset.build import load
p = load('data/operational-20261125/processed/panel-indicators.npz')
d = list(pd.to_datetime(p['dates']).strftime('%Y-%m-%d')); L = list(p['locations'])
tn, cn = list(p['target_names']), list(p['covariate_names'])
T, C = p['asof_targets'][-1], p['asof_covariates'][-1]
A, E = T[..., tn.index('nhsn_flu_admissions')], T[..., tn.index('nssp_flu_proportion')]
Hr = C[..., cn.index('hosprep_flu')]
sig = {'wastewater': C[..., cn.index('nwss_flu_wval_like')], 'ilinet': C[..., cn.index('ilinet_ili')],
       'lab_pos': C[..., cn.index('clinical_lab_flu_pct_positive')]}
i21, i14 = d.index('2026-11-21'), d.index('2026-11-14')
def growth(x):
    """Latest finite week over the week before; None if the latest week is not 14 or 21 Nov."""
    f = np.where(np.isfinite(x))[0]
    if len(f) < 2 or f[-1] < i14 or f[-2] != f[-1] - 1 or x[f[-2]] <= 0: return np.nan, ''
    return x[f[-1]] / x[f[-2]], d[f[-1]][5:]
rows = []
for j, s in enumerate(L):
    r = {'state': s, 'ed': E[i21, j] / E[i14, j],
         'adm_per_hospital': (A[i21, j] / Hr[i21, j]) / (A[i14, j] / Hr[i14, j]),
         'adm_raw': A[i21, j] / A[i14, j], 'reporting': Hr[i21, j] / Hr[i14, j]}
    for k, x in sig.items():
        r[k], r[k + '_week'] = growth(x[:, j])
    rows.append(r)
pd.DataFrame(rows).to_csv('output/evidence-20261125.csv', index=False)
# Check of the per-hospital correction: first report x (later coverage / first coverage) against the later value.
for k in range(-5, -1):
    Ak, Hk = p['asof_targets'][k][..., 0], p['asof_covariates'][k][..., cn.index('hosprep_flu')]
    n = np.where(np.isfinite(Ak[:, L.index('US')]))[0][-1]
    first, later = Ak[n], A[n]
    est = first * Hr[n] / Hk[n]
    ok = np.isfinite(first) & np.isfinite(later) & (later > 20)
    print(d[n], 'median later/first', round(np.median(later[ok] / first[ok]), 3), '| median later/(first x coverage ratio)', round(np.median(later[ok] / est[ok]), 3))
print(len(rows))
