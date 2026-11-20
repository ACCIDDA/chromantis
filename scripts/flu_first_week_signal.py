"""Is the newest reported week's revision predictable at forecast time? (flu search, 20 Nov 2026)

For each Wednesday issuance w of 2024-25 and 2025-26 and each state/DC, the target is the
log revision of the newest reported week t: log((value 12 weeks later + f) / (report at w + f)),
f = 5% of the state's season max (as the correction trees). Candidate predictors available at w:
  cov   log(hospitals reporting week t / median of weeks t-5..t-3), Delphi hosprep (from Dec 2024)
  rev1  last week's observed first revision: log(report at w of week t-1 / report at w-1 of week t-1)
  rev3  mean of the last three observed first revisions (weeks t-1, t-2, t-3, each between its 1st and 2nd report)
  past  the same state's mean first-week total revision over the previous 8 matured issuances
        (log(value 12 weeks later / first report)), only issuances whose 12-week value is known at w
Prints correlations and the share of variance explained by least-squares fits on the other season.
    PYTHONPATH=src .venv/bin/python scripts/flu_first_week_signal.py
"""
import numpy as np
from chromantis.dataset.build import load

p = load('data/processed/panel-coverage.npz')
names = list(map(str, p['target_names'])); k = names.index('nhsn_flu_admissions')
cn = list(map(str, p['covariate_names'])); h = cn.index('hosprep_flu')
dates = p['dates'].astype(str); iss = p['issuance_dates'].astype(str)
A = p['asof_targets'][..., k]            # [issuance, week, location]
C = p['asof_covariates'][..., h]
L = A.shape[-1]
def season(d):
    y, m = int(d[:4]), int(d[5:7]); return f'{y}-{y+1}' if m >= 8 else f'{y-1}-{y}'
def newest(w):  # index of newest reported week at issuance w
    ok = np.where(np.isfinite(A[w]).any(-1))[0]; return ok.max() if len(ok) else -1
rows = []
for w in range(4, len(iss)):
    t = newest(w)
    if t < 8 or season(dates[t]) not in ('2024-2025', '2025-2026'): continue
    wm = np.searchsorted(iss, str(np.datetime64(dates[t]) + np.timedelta64(12 * 7 + 4, 'D')))
    if wm >= len(iss): continue
    smax = np.nanmax(A[wm, t - 30:t + 1], axis=0); f = np.maximum(.05 * smax, 1)
    lg = lambda a, b: np.log((a + f) / (b + f))
    y = lg(A[wm, t], A[w, t])
    with np.errstate(all='ignore'):
        cov = np.log(C[w, t] / np.nanmedian(C[w, t - 5:t - 2], axis=0))
    r = [lg(A[w - j, t - 1 - j], A[w - j - 1, t - 1 - j]) for j in range(3)]  # week t-1-j: report at w-j vs w-j-1
    rev1 = r[0]; rev3 = np.nanmean(np.stack(r), 0)
    past = []
    for j in range(13, 21):  # issuances whose newest week has matured (12 weeks) by w
        wj = w - j; tj = newest(wj); wmj = np.searchsorted(iss, str(np.datetime64(dates[tj]) + np.timedelta64(12 * 7 + 4, 'D')))
        if wmj <= w: past.append(lg(A[wmj, tj], A[wj, tj]))
    past = np.nanmean(np.stack(past), 0) if past else np.full(L, np.nan)
    for l in range(L):
        rows.append((season(dates[t]), dates[t], l, y[l], cov[l], rev1[l], rev3[l], past[l], A[w, t, l]))
import pandas as pd
d = pd.DataFrame(rows, columns=['season', 'week', 'loc', 'y', 'cov', 'rev1', 'rev3', 'past', 'report'])
d = d[np.isfinite(d.y) & (d.report >= 5)]
print(f'{len(d)} state-weeks (newest week >= 5 admissions); y = log(value 12 weeks later / first report)')
print(d.groupby('season').y.describe().round(3))
for s, g in d.groupby('season'):
    print(f'\n== {s}: correlation with y (pairwise complete)')
    for c in ['cov', 'rev1', 'rev3', 'past']:
        ok = g[[c, 'y']].dropna(); print(f'  {c:5s} n={len(ok):5d} r={ok.corr().iloc[0, 1]:+.3f}')
# Out-of-season R2: fit on one season, score on the other (rows with all predictors present).
def r2(train, test, cols):
    tr = train.dropna(subset=cols); te = test.dropna(subset=cols)
    X = np.c_[np.ones(len(tr)), tr[cols]]; b = np.linalg.lstsq(X, tr.y, rcond=None)[0]
    pred = np.c_[np.ones(len(te)), te[cols]] @ b
    base = te.y - tr.y.mean()
    return 1 - ((te.y - pred) ** 2).mean() / (base ** 2).mean(), len(te)
print('\nOut-of-season R2 of a linear fit (train one season, test the other; rows where cov exists):')
for cols in (['cov'], ['rev1'], ['rev3'], ['past'], ['cov', 'rev3'], ['cov', 'rev3', 'past'], ['rev3', 'past']):
    sub = d.dropna(subset=['cov'])
    a = r2(sub[sub.season == '2025-2026'], sub[sub.season == '2024-2025'], cols)
    b = r2(sub[sub.season == '2024-2025'], sub[sub.season == '2025-2026'], cols)
    print(f'  {"+".join(cols):16s} test 2024-25 R2={a[0]:+.3f} (n={a[1]})   test 2025-26 R2={b[0]:+.3f} (n={b[1]})')
