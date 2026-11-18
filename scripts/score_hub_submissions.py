"""Score our submitted FluSight, COVID or RSV files, and local alternatives, against every Hub model.

    .venv/bin/python scripts/score_hub_submissions.py flu|covid|rsv [NAME=RELEASE ...]

Truth: the Hub clone's latest target data (refresh the clone first). Forecasts: quantiles,
horizons 0-3, states and DC (no US, no Puerto Rico), every reference date from our first
submission to the latest. Scores: WIS of log(1 + admissions), WIS of admissions, WIS of ED
share; WIS = 2 x mean pinball loss over the 23 quantiles. Pairwise relative WIS (Cramer et
al.): geometric mean over opponents of the mean-WIS ratio on shared tasks, divided by the
baseline's; lower is better. Each NAME=RELEASE reads production/output/<issuance>/<RELEASE>/
(issuance = reference date - 3 days) and is ranked alone among the Hub models, with our
submitted files removed (a local alternative for the weeks it exists).
Written 18 November 2026; replaces the one-off scratch scripts used 12 November.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

HUBS = {'covid': ('production/hubs/covid19-forecast-hub', 'CovidHub', '2026-11-07'),
        'rsv': ('production/hubs/rsv-forecast-hub', 'RSVHub', '2026-10-17'),
        'flu': ('production/hubs/FluSight-forecast-hub', 'FluSight', '2026-10-10')}
pathogen = sys.argv[1]
hub, prefix, first = HUBS[pathogen]
first = os.environ.get('FIRST', first)  # score from this reference date on
local = dict(a.split('=') for a in sys.argv[2:])
OURS, BASE, ENS = 'ACCIDDA-Chromantis', f'{prefix}-baseline', f'{prefix}-ensemble'
HOSP, ED = f'wk inc {pathogen} hosp', f'wk inc {pathogen} prop ed visits'
ts = f'{hub}/target-data/time-series'  # FluSight publishes CSV, the CDC Hubs Parquet
t = pd.read_parquet(ts + '.parquet') if os.path.exists(ts + '.parquet') else pd.read_csv(ts + '.csv', dtype={'location': str})
asof = t.as_of.max()
truth = t[t.as_of == asof][['location', 'target', 'target_end_date', 'observation']].copy()
truth['target_end_date'] = pd.to_datetime(truth.target_end_date)
print(f'{pathogen}: truth as of {asof}, weeks through {truth.target_end_date.max().date()}')


def score(model, f, ref):
    f = f[(f.output_type == 'quantile') & (pd.to_numeric(f.horizon, errors='coerce') >= 0)].copy()  # drops peak rows
    f['location'] = f.location.astype(str)
    f.loc[f.location != 'US', 'location'] = f.location.str.zfill(2)
    f['q'] = f.output_type_id.astype(float)
    f['target_end_date'] = pd.to_datetime(f.target_end_date)
    f = f[f.location != '72'].merge(truth, on=['location', 'target', 'target_end_date'])
    out = []
    for (loc, target, h), g in f.groupby(['location', 'target', 'horizon']):
        g = g.sort_values('q')
        v, y, q = g.value.values.astype(float), float(g.observation.iloc[0]), g.q.values
        if len(q) != 23:
            continue
        k = dict(model=model, ref=ref, loc=loc, h=int(h), y=y, med=v[11])
        wis = lambda a, b: np.mean(2 * (((b <= a) - q) * (a - b)))
        if target == HOSP:
            out += [dict(k, score='log_adm', wis=wis(np.log1p(v), np.log1p(y))), dict(k, score='adm', wis=wis(v, y))]
        elif target == ED:
            out.append(dict(k, score='ed', wis=wis(v, y)))
    return out


def read(p):
    return pd.read_parquet(p) if p.endswith('.parquet') else pd.read_csv(p, dtype={'location': str})


rows = []
for model in sorted(os.listdir(f'{hub}/model-output')):
    for p in sorted(glob.glob(f'{hub}/model-output/{model}/20*')):
        ref = os.path.basename(p)[:10]
        if ref >= first:
            rows += score(model, read(p), ref)
refs = {r['ref'] for r in rows if r['model'] == OURS}
for name, rel in local.items():  # local replays also cover weeks we did not submit
    for ref in sorted({r['ref'] for r in rows}):
        iss = (pd.Timestamp(ref) - pd.Timedelta(days=3)).strftime('%Y-%m-%d')
        p = f'production/output/{iss}/{rel}/{ref}-ACCIDDA-Chromantis.csv'
        if os.path.exists(p):
            rows += score(name, read(p), ref)
            refs.add(ref)
refs = sorted(refs)
r = pd.DataFrame(rows)
r = r[r.ref.isin(refs)]
st = r[r['loc'] != 'US']


def pairwise(s):
    w = s.pivot_table(index=['ref', 'loc', 'h'], columns='model', values='wis')
    th = {}
    for i in w.columns:
        rr = []
        for j in w.columns.drop(i):
            m = w[[i, j]].dropna().values
            if len(m) and m[:, 1].mean() > 0:
                rr.append(m[:, 0].mean() / m[:, 1].mean())
        th[i] = np.exp(np.mean(np.log(rr)))
    return pd.Series(th) / th[BASE], w.notna().sum()


def ranked(s, me):
    """Relative WIS, rank and model count of `me`, the other local versions removed."""
    keep = [m for m in s.model.unique() if m == me or (m not in local and (me == OURS or m != OURS))]
    th, n = pairwise(s[s.model.isin(keep)])
    return th[me], int((th < th[me]).sum()) + 1, len(th), th.get(ENS, np.nan), n[me]


print(f'\nAll observed tasks of reference dates {refs[0]} to {refs[-1]}, horizons 0-3, states/DC. '
      'Pairwise relative WIS (baseline 1, lower is better), rank among Hub models:')
tab = []
for me in [OURS, *local]:
    row = {'model': me}
    for sc in ['log_adm', 'adm', 'ed']:
        v, k, n, e, tasks = ranked(st[st.score == sc], me)
        row[sc] = f'{v:.3f} ({k}/{n})'
        row[f'{ENS} {sc}'] = round(e, 3)
    a = st[(st.model == me) & (st.score == 'adm')]
    row['tasks'] = len(a)
    row['median/obs'] = round(a.med.sum() / a.y.sum(), 3)
    tab.append(row)
print(pd.DataFrame(tab).to_string(index=False))

print('\nPer reference date (all its observed horizons), states/DC: our relative WIS and rank that week')
for sc in ['log_adm', 'adm', 'ed']:
    line = []
    for ref in refs:
        s = st[(st.score == sc) & (st.ref == ref) & ~st.model.isin(local)]
        if (s.model == OURS).any():
            v, k, n, e, _ = ranked(s, OURS)
            line.append(f'{ref}: {v:.2f} ({k}/{n}; ens {e:.2f})')
    print(f'  {sc:8s}', ' | '.join(line))

o = st[(st.model == OURS) & (st.score == 'log_adm')].set_index(['ref', 'loc', 'h']).wis
b = st[(st.model == BASE) & (st.score == 'log_adm')].set_index(['ref', 'loc', 'h']).wis
j = pd.concat([o.rename('o'), b.rename('b')], axis=1).dropna().groupby(['ref', 'h']).sum()
print('\nOur mean log-admission WIS / baseline, states/DC, by reference date x horizon:')
print((j.o / j.b).unstack().round(2).to_string())

us = r[(r['loc'] == 'US') & (r.score == 'adm') & (r.h == 0) & r.model.isin([OURS, ENS, *local])]
print('\nUS admissions, horizon 0: median vs latest observed')
print(us.pivot_table(index='ref', columns='model', values='med').round(0).join(
    us.groupby('ref').y.first().rename('observed')).to_string())
