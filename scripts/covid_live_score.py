"""Score replayed COVID releases on the weeks observed so far, against CovidHub-ensemble.

Usage: .venv/bin/python scripts/covid_live_score.py RELEASE [RELEASE ...]
Each RELEASE is a folder name under production/output/<issuance>/. Scores are WIS of
log(1 + admissions) and natural-scale ED WIS, on the tasks every model covers.
"""
import os
import sys

import numpy as np
import pandas as pd

HUB = 'production/hubs/covid19-forecast-hub'
HOSP, ED = 'wk inc covid hosp', 'wk inc covid prop ed visits'


def wis(q, v, y):
    return np.mean(2 * (((y <= v) - q) * (v - y)))


def main():
    truth = pd.read_parquet(f'{HUB}/target-data/time-series.parquet')
    truth = truth.sort_values('as_of').groupby(['location', 'target', 'target_end_date'], as_index=False).last()
    truth['target_end_date'] = pd.to_datetime(truth.target_end_date)
    print('truth as of', truth.as_of.max())
    rows, level = [], {}
    for name in ['CovidHub-ensemble', *sys.argv[1:]]:
        for issuance in sorted(os.listdir('production/output')):
            folder = f'production/output/{issuance}/{name}'
            files = ([f'{HUB}/model-output/{name}/{f}' for f in sorted(os.listdir(f'{HUB}/model-output/{name}'))]
                     if name == 'CovidHub-ensemble' else
                     [f'{folder}/{f}' for f in os.listdir(folder) if f.endswith('.csv')] if os.path.isdir(folder) else [])
            for path in files:
                f = pd.read_csv(path, dtype={'location': str})
                f = f[(f.output_type == 'quantile') & (f.horizon >= 0)].copy()
                f['q'] = f.output_type_id.astype(float)
                f['target_end_date'] = pd.to_datetime(f.target_end_date)
                ref = str(f.reference_date.iloc[0])
                m = f[(f.q == .5) & (f.target == HOSP) & (f.location != 'US')]
                level[(name, ref)] = m.groupby('horizon').value.sum().to_dict()
                for (loc, target, h), g in f.merge(truth, on=['location', 'target', 'target_end_date']).groupby(['location', 'target', 'horizon']):
                    g = g.sort_values('q')
                    v, y, q = g.value.values.astype(float), float(g.observation.values[0]), g.q.values
                    rows.append(dict(model=name, ref=ref, loc=loc, target=target, h=h, y=y, med=v[len(v) // 2],
                                     wis=wis(q, np.log1p(v), np.log1p(y)) if target == HOSP else wis(q, v, y) * 1e4))
            if name == 'CovidHub-ensemble':
                break
    r = pd.DataFrame(rows)
    key = ['ref', 'loc', 'target', 'h']
    shared = r.groupby(key).model.nunique()
    r = r.merge(shared[shared == r.model.nunique()].reset_index()[key], on=key)
    st = r['loc'] != 'US'
    out = pd.DataFrame({
        'log_adm_states': r[st & (r.target == HOSP)].groupby('model').wis.mean(),
        'log_adm_us': r[~st & (r.target == HOSP)].groupby('model').wis.mean(),
        'ed_states_x1e4': r[st & (r.target == ED)].groupby('model').wis.mean(),
        'ed_us_x1e4': r[~st & (r.target == ED)].groupby('model').wis.mean(),
        'median/observed': r[st & (r.target == HOSP)].groupby('model').med.sum() / r[st & (r.target == HOSP)].groupby('model').y.sum()})
    print(f"{len(r[st & (r.target == HOSP)]) // r.model.nunique()} states/DC admissions tasks per model, "
          f"reference dates {sorted(r.ref.unique())}, horizons {sorted(r.h.unique())}")
    pd.set_option('display.width', 200)
    print(out.sort_values('log_adm_states').round(3).to_string())
    latest = max(ref for _, ref in level)
    print(f'\nstates/DC median admissions by horizon, reference date {latest}')
    print(pd.DataFrame({n: v for (n, ref), v in level.items() if ref == latest}).T.round(0).to_string())


if __name__ == '__main__':
    main()
