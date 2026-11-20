"""Split the live COVID/RSV forecast error into a nowcast part and a growth part (18 November 2026).

For each 2026-27 Wednesday issuance, the submitted release's saved correction trees are applied to that
Wednesday's reported histories (the hub-deadline vintage stored in the coverage panel), exactly as
production does, giving the model's corrected value of the newest reported week (week ending the
Saturday before the reference date, Hub horizon -1). With y = Hub target data of the latest as_of
(truth so far, still being revised for the newest weeks), m_h the submitted median at horizon h and
c the corrected newest week, in log(1 + x) for each state/DC:

    total_h = log m_h - log y_h
            = [log c - log y_last]                          nowcast error of the newest week
            + [(log m_h - log c) - (log y_h - log y_last)]  growth error (forecast rise vs actual rise)

and the nowcast error itself splits into what the report lacked and what the trees added:
    log c - log y_last = [log r - log y_last] + [log c - log r]      (r = value as reported)

Writes one row per issuance, target, location and horizon, plus a printed summary.
    PYTHONPATH=src .venv/bin/python scripts/live_nowcast_decomposition.py --hub rsv --out output/live-decomposition
"""
import argparse
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.dataset.build import load, for_hub, context_end
from chromantis.dataset.episodes import episodes
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem

ROOT = Path('/hickory/proj/jlessler/projects/tapestry-all')
SETUP = {
    'covid': dict(release='production/releases/covid-gru-four-candidate-20261103.json', campaign='covid-20261030',
                  panel='data/processed/panel-coverage.npz', target='wk inc covid hosp', ed='wk inc covid prop ed visits'),
    'rsv': dict(release='production/releases/rsv-four-20261014.json', campaign='tapestry',
                panel='data/processed/panel-coverage-rsv.npz', target='wk inc rsv hosp', ed='wk inc rsv prop ed visits'),
}
ISSUANCES = ['2026-10-14', '2026-10-21', '2026-10-28', '2026-11-04', '2026-11-11']
STRENGTH = {('rsv', '2026-11-11'): 0.5}  # RSV 14 November file used rsv-four-cs050 (same fits, trees halved)


def corrected_newest(hub, issuance, strength=1.0):
    """Median over every release member of the corrected newest two weeks: {target_index: [L, 2]} and reported."""
    s = SETUP[hub]
    release = json.loads(Path(s['release']).read_text())
    problem = Problem.load(release['problem'])
    panel = for_hub(load(s['panel']), hub)
    out, reported = {}, {}
    for recipe, members in release['recipes'].items():
        for member in members:
            path = ROOT / s['campaign'] / member['checkpoint'].replace('data/production-fits/', 'data/experiments/')
            scenario = Scenario.from_string(json.loads((path / 'manifest.json').read_text())['scenario'])
            eps = episodes(panel, problem, problem.input_names(scenario.input_set), scenario.lookback, 'reported',
                           problem.covariate_names(scenario.covariate_set), horizons=problem.horizons, require_labels=False)
            e = [x for x in eps if x['issuance'] == issuance]
            assert len(e) == 1 and e[0]['context_dates'][-1] == context_end(issuance)
            with (path / 'nowcaster.pkl').open('rb') as f:
                trees = pickle.load(f)
            trees.strength *= strength  # as production's correction_strength
            c = trees.apply(e[0])
            for j, k in enumerate(problem.target_input_indices(scenario.input_set)):
                out.setdefault(j, []).append(c['values'][-2:, k].T)  # [L, 2]: second-newest, newest
                reported.setdefault(j, e[0]['values'][-2:, k].T)
    locations = list(map(str, panel['locations']))
    return {j: np.median(np.stack(v), axis=0) for j, v in out.items()}, reported, locations, problem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hub', choices=list(SETUP), required=True)
    parser.add_argument('--out', default='output/live-decomposition')
    args = parser.parse_args()
    s = SETUP[args.hub]
    fips = pd.read_csv('data/metadata/locations.csv', dtype=str)
    to_fips = dict(zip(fips.abbreviation, fips.location)) | dict(zip(fips.location, fips.location))
    truth = pd.read_parquet(f'data/hub-target/{args.hub}-time-series.parquet')
    truth['target_end_date'] = pd.to_datetime(truth.target_end_date).dt.strftime('%Y-%m-%d')
    truth['as_of'] = pd.to_datetime(truth.as_of).dt.strftime('%Y-%m-%d')
    latest = truth[truth.as_of == truth.as_of.max()].set_index(['target', 'location', 'target_end_date']).observation
    rows = []
    for issuance in ISSUANCES:
        corrected, reported, locations, problem = corrected_newest(args.hub, issuance, STRENGTH.get((args.hub, issuance), 1.0))
        newest = context_end(issuance)
        reference = str(np.datetime64(newest) + np.timedelta64(7, 'D'))
        sub = Path(f'production/submissions/{reference}/{args.hub}/{reference}-ACCIDDA-Chromantis.csv')
        medians = None
        if sub.exists():
            f = pd.read_csv(sub, dtype={'location': str})
            f = f[(f.output_type == 'quantile') & (f.output_type_id.astype(str).isin(['0.5', '0.50']))]
            medians = f.set_index(['target', 'location', 'horizon']).value
        for j, target in enumerate((s['target'], s['ed'])):
            for l, loc in enumerate(locations):
                code = to_fips.get(loc, loc)
                y_last = latest.get((target, code, newest), np.nan)
                r, c = reported[j][l, 1], corrected[j][l, 1]
                for h in range(4):
                    week = str(np.datetime64(reference) + np.timedelta64(7 * h, 'D'))
                    m = medians.get((target, code, h), np.nan) if medians is not None else np.nan
                    rows.append(dict(issuance=issuance, reference_date=reference, target=target, location=code, horizon=h,
                                     reported_newest=r, corrected_newest=c, truth_newest=y_last, median=m,
                                     truth=latest.get((target, code, week), np.nan)))
    d = pd.DataFrame(rows)
    ed = d.target.str.contains('prop')
    scale = np.where(ed, 1000.0, 1.0)  # ED share in per-mille before log1p, so small shares are not flattened
    L = lambda col: np.log1p(d[col] * scale)
    d['report_shortfall'] = L('reported_newest') - L('truth_newest')
    d['tree_correction'] = L('corrected_newest') - L('reported_newest')
    d['nowcast_error'] = L('corrected_newest') - L('truth_newest')
    d['growth_error'] = (L('median') - L('corrected_newest')) - (L('truth') - L('truth_newest'))
    d['total_error'] = L('median') - L('truth')
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    d.to_csv(out / f'{args.hub}-rows.csv', index=False)
    cols = ['report_shortfall', 'tree_correction', 'nowcast_error', 'growth_error', 'total_error']
    keys = ['target', 'issuance', 'horizon']
    # US: the newest-week nowcast is the sum over states/DC (the network forecasts states; the US row of the
    # file is the submitted US median), so nowcast terms come from state sums and growth from the US row.
    adm = d[~ed & (d.location != 'US')].groupby(keys)[['reported_newest', 'corrected_newest', 'truth_newest']].sum(min_count=1)
    us = d[~ed & (d.location == 'US')].set_index(keys)[['median', 'truth']].join(adm)
    us = us.assign(**{c: np.log(us[a]) - np.log(us[b]) for c, a, b in (
        ('report_shortfall', 'reported_newest', 'truth_newest'), ('tree_correction', 'corrected_newest', 'reported_newest'),
        ('nowcast_error', 'corrected_newest', 'truth_newest'), ('total_error', 'median', 'truth'))})
    us['growth_error'] = us.total_error - us.nowcast_error
    states = d[d.location != 'US'].groupby(keys)
    summary = pd.concat({'US admissions (log ratio)': us[cols],
                         'states/DC mean': states[cols].mean(),
                         'states/DC mean |x|': states[cols].agg(lambda x: x.abs().mean())}, axis=1).round(3)
    summary.to_csv(out / f'{args.hub}-summary.csv')
    pd.set_option('display.width', 300, 'display.max_columns', 30)
    print(f'{args.hub}: truth as_of {truth.as_of.max()}; log(1+x) differences, ED share in per-mille; '
          f'positive = above the truth so far')
    for block in summary.columns.levels[0]:
        print(f'\n== {block}'); print(summary[block].dropna(how='all').to_string())


if __name__ == '__main__':
    main()
