"""Score all-season (production-problem) fits on the 2026-27 reports against the latest Hub target data.

The planner scores these fits against the panel truth (finalized as of the panel's truth day). The newest
weeks keep being revised for weeks, so this rescoring uses the Hub's latest `as_of` instead, and reports
the bias of the median as well as WIS. One row per recipe: mean over seeds of states/DC mean WIS of
log(1 + admissions), its US value, and the states/DC mean log(median / truth), for reports from
--first-context to --last-context and Hub horizons 0-3.

With --mix, also scores equal-weight mixtures as a release would issue them (evaluation.ensembles.combine,
rule `mixture`: equal weight per recipe and per seed, seeds common to every member recipe):
    PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate01 covid-cov-gate02 --hub covid \
        --mix "A+B=ref.Bh_wd+T.pN_gru.real"
History: 18 Nov 2026, first version read eval_2026-2027/forecasts.npz, which is the trees-off view; fixed the
same evening (deployed view = eval_2026-2027/corrected/forecasts.npz unless the recipe is forecast_view=raw).
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.evaluation.ensembles import combine

TARGET = {('covid', 'hosp'): 'wk inc covid hosp', ('rsv', 'hosp'): 'wk inc rsv hosp',
          ('covid', 'ed'): 'wk inc covid prop ed visits', ('rsv', 'ed'): 'wk inc rsv prop ed visits'}
CHANNEL = {'hosp': 'nhsn_{}_admissions', 'ed': 'nssp_{}_proportion'}


def wis(q, levels, y):
    """Mean pinball-based WIS over quantile levels; q [..., Q], y [...]."""
    return np.mean(2 * ((y[..., None] <= q) - levels) * (q - y[..., None]), axis=-1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-e', '--experiment', nargs='+', required=True)
    p.add_argument('--hub', choices=['covid', 'rsv'], required=True)
    p.add_argument('--target', choices=['hosp', 'ed'], default='hosp',
                   help='hosp: WIS of log(1 + admissions); ed: WIS of the ED share on its natural scale, x 1e4')
    p.add_argument('--first-context', default='2026-10-10', help='First newest-reported week scored (14 Oct report)')
    p.add_argument('--last-context', default='2026-10-31', help='Last one (4 Nov report); some recipes lack the 11 Nov report')
    p.add_argument('--view', choices=['raw', 'corrected', 'half', 'calibrated'],
                   help='Forecast view; default the one each recipe is deployed in (corrected unless forecast_view=raw)')
    p.add_argument('--mix', nargs='*', default=[], help='LABEL=recipe+recipe+...')
    p.add_argument('--submitted', action='store_true', help='Add the submitted files and score everything on their tasks only')
    a = p.parse_args()
    fips = pd.read_csv('data/metadata/locations.csv', dtype=str)
    to_fips = dict(zip(fips.abbreviation, fips.location))
    t = pd.read_parquet(f'data/hub-target/{a.hub}-time-series.parquet')
    t = t[(t.target == TARGET[a.hub, a.target]) & (t.as_of == t.as_of.max())]
    truth = {(r.location, pd.Timestamp(r.target_end_date).strftime('%Y-%m-%d')): r.observation for r in t.itertuples()}
    forecasts, ctx = {}, None  # name -> {seed: q [Q, issuance, horizon, location]}
    for e in a.experiment:
        root = Path('data/experiments') / e
        for r in csv.DictReader(open(root / 'runs.csv')):
            view = a.view or ('raw' if 'forecast_view=raw' in r['scenario'] else 'corrected')
            f = root / r['attempt'] / 'eval_2026-2027' / ('' if view == 'raw' else view) / 'forecasts.npz'  # top level = trees off
            if r['status'] != 'complete' or not f.exists():
                continue
            z = np.load(f)
            k = list(z['target_names']).index(CHANNEL[a.target].format(a.hub))
            keep = (z['context_end'] >= a.first_context) & (z['context_end'] <= a.last_context)
            if ctx is None:
                ctx = (z['target_dates'][keep], [to_fips[l] for l in z['locations']], z['quantile_levels'])
            elif not np.array_equal(z['target_dates'][keep], ctx[0]):
                continue  # fit lacks some of the reports (e.g. sampled recipes end at the 4 Nov report)
            forecasts.setdefault(r['name'], {})[r['seed']] = z['quantiles'][..., k, :][:, keep]
    dates, locs, lv = ctx
    y = np.array([[[truth.get((loc, d), np.nan) for loc in locs] for d in row] for row in dates])
    states = np.array([loc != 'US' for loc in locs])
    mid = list(np.round(lv, 3)).index(0.5)
    submitted = None
    if a.submitted:
        # The files we actually submitted (production/submissions/<reference date>/<hub>/); every row below is then
        # scored only on the tasks those files cover (reports without a file are masked out).
        submitted = np.full((len(lv), *y.shape), np.nan)
        for i, row in enumerate(dates):
            ref = row[0]  # Hub horizon 0 ends on the reference date
            f = Path(f'production/submissions/{ref}/{a.hub}/{ref}-ACCIDDA-Chromantis.csv')
            if not f.exists():
                y[i] = np.nan
                continue
            s = pd.read_csv(f, dtype={'location': str})
            s = s[(s.output_type == 'quantile') & (s.target == TARGET[a.hub, a.target])]
            s['level'] = s.output_type_id.astype(float).round(3)
            v = s.set_index(['horizon', 'location', 'level']).value
            for h in range(y.shape[1]):
                for j, loc in enumerate(locs):
                    submitted[:, i, h, j] = [v.get((h, loc, round(float(l), 3)), np.nan) for l in lv]
        y[np.isnan(submitted).any(0)] = np.nan

    def score(q):  # q [Q, issuance, horizon, location]
        q = np.moveaxis(q, 0, -1)
        if a.target == 'hosp':
            w = wis(np.log1p(q), lv, np.log1p(y)); bias = np.log1p(q[..., mid]) - np.log1p(y)
        else:
            w = 1e4 * wis(q, lv, y); bias = np.log(q[..., mid] / np.where(y > 0, y, np.nan))  # zero shares: no bias cell
        return dict(states_dc=np.nanmean(w[..., states]), US=np.nanmean(w[..., ~states]),
                    bias_states_dc=np.nanmean(bias[..., states]), bias_US=np.nanmean(bias[..., ~states]))

    rows = [dict(name=n, seed=s, **score(q)) for n, seeds in forecasts.items() for s, q in seeds.items()]
    d = pd.DataFrame(rows).groupby('name').agg(states_dc=('states_dc', 'mean'), sd=('states_dc', 'std'), US=('US', 'mean'),
                                                bias_states_dc=('bias_states_dc', 'mean'), bias_US=('bias_US', 'mean'),
                                                seeds=('seed', 'count')).sort_values('states_dc')
    print(f'{" ".join(a.experiment)}: truth = Hub target data as of {t.as_of.max()}; reports with newest week '
          f'{a.first_context}..{a.last_context}; {"WIS of log(1+admissions)" if a.target == "hosp" else "WIS of ED share x 1e4"}, lower is better; bias = mean log(median/truth), '
          'positive = too high. Recipes: mean over single seeds.')
    print(d.round(4).to_string())
    if a.mix:
        mixes = []
        for spec in a.mix:
            label, members = spec.split('=')
            members = members.split('+')
            seeds = sorted(set.intersection(*[set(forecasts[m]) for m in members]))
            recipes = [dict(channels=[0], values=np.stack([forecasts[m][s] for s in seeds])[..., None, :]) for m in members]
            mixes.append(dict(name=label, members=' + '.join(members), seeds=len(seeds), **score(combine(recipes, 0, 'mixture'))))
        if submitted is not None:
            mixes.append(dict(name='SUBMITTED FILES', members='production/submissions', seeds=0, **score(submitted)))
        m = pd.DataFrame(mixes).set_index('name').sort_values('states_dc')
        print('\nEqual-weight mixtures (per recipe, per seed), scored as one forecast:')
        print(m.round(4).to_string())
        d = pd.concat([d, m])
    d.to_csv(Path('data/experiments') / a.experiment[0] / f'hub-truth-scores-{a.target}-{a.view or "deployed"}.csv')


if __name__ == '__main__':
    main()
