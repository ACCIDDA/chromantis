"""Nowcast vs growth error of research fits on the 2026-27 reports (19 November 2026).

Same decomposition as scripts/live_nowcast_decomposition.py (which handles submitted releases), for all-season
fits of planner experiments (production-problem fits, `eval_2026-2027`). For each fit and each Wednesday
report, the fit's own saved trees are reapplied to that report (as production does) to get its corrected
newest week c; the fit's deployed-view median m_h (forecasts.npz) and the latest Hub target data y give, in
log(1 + x):
    total_h = log m_h - log y_h = [log c - log y_last] (nowcast) + [(log m_h - log c) - (log y_h - log y_last)] (growth)
US: the newest week is the sum over states/DC of the corrected values; growth uses the US median row.
Seeds are averaged in log space. One row per recipe, report and horizon; printed summary over reports.
    PYTHONPATH=src .venv/bin/python scripts/live_decomposition_fits.py --hub rsv -e rsv-cov-gate02 rsv-cov-final --recipes A4c0.national
"""
import argparse
import csv
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.dataset.build import load, for_hub, context_end
from chromantis.dataset.episodes import episodes
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem

PANEL = {'covid': 'data/processed/panel-coverage.npz', 'rsv': 'data/processed/panel-coverage-rsv.npz'}
TARGET = {'covid': 'wk inc covid hosp', 'rsv': 'wk inc rsv hosp'}
ISSUANCES = ['2026-10-14', '2026-10-21', '2026-10-28', '2026-11-04']


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--hub', choices=list(PANEL), required=True)
    a.add_argument('-e', '--experiment', nargs='+', required=True)
    a.add_argument('--recipes', nargs='+', required=True)
    a.add_argument('--out', default='output/live-decomposition')
    args = a.parse_args()
    problem = Problem.load(f'problems/us-{args.hub}-production-coverage.json')
    panel = for_hub(load(PANEL[args.hub]), args.hub)
    fips = pd.read_csv('data/metadata/locations.csv', dtype=str)
    to_fips = dict(zip(fips.abbreviation, fips.location))
    t = pd.read_parquet(f'data/hub-target/{args.hub}-time-series.parquet')
    t = t[(t.target == TARGET[args.hub]) & (t.as_of == t.as_of.max())]
    truth = {(r.location, pd.Timestamp(r.target_end_date).strftime('%Y-%m-%d')): r.observation for r in t.itertuples()}
    cache, rows = {}, []
    for e in args.experiment:
        for r in csv.DictReader(open(Path('data/experiments') / e / 'runs.csv')):
            if r['name'] not in args.recipes or r['status'] != 'complete':
                continue
            fit = Path('data/experiments') / e / r['attempt'] / 'eval_2026-2027'
            scenario = Scenario.from_string(r['scenario'])
            view = 'raw' if scenario.forecast_view == 'raw' else 'corrected'
            z = np.load(fit / ('' if view == 'raw' else view) / 'forecasts.npz')
            key = (scenario.input_set, scenario.covariate_set, scenario.lookback)
            if key not in cache:
                cache[key] = {x['issuance']: x for x in episodes(panel, problem, problem.input_names(scenario.input_set), scenario.lookback,
                              'reported', problem.covariate_names(scenario.covariate_set), horizons=problem.horizons, require_labels=False)}
            with (fit / 'nowcaster.pkl').open('rb') as f:
                trees = pickle.load(f)
            k_in = problem.target_input_indices(scenario.input_set)[0]
            k_out = list(z['target_names']).index(f'nhsn_{args.hub}_admissions')
            mid = list(np.round(z['quantile_levels'], 3)).index(0.5)
            locs = [to_fips[l] for l in map(str, panel['locations'])]
            zlocs = [to_fips[l] for l in z['locations']]
            for issuance in ISSUANCES:
                ep = cache[key][issuance]
                newest = context_end(issuance)
                corrected = (trees.apply(ep) if view == 'corrected' else ep)['values'][-1, k_in]
                reported = ep['values'][-1, k_in]
                i = list(z['context_end']).index(newest)
                st = [j for j, l in enumerate(locs) if l != 'US']
                ytrue = np.array([truth.get((locs[j], newest), np.nan) for j in st])
                c_sum, r_sum, y_sum = np.nansum(corrected[st]), np.nansum(reported[st]), np.nansum(ytrue)
                for h in range(4):
                    d = z['target_dates'][i][h]
                    us = zlocs.index('US')
                    m_us = z['quantiles'][mid, i, h, k_out, us]
                    rows.append(dict(recipe=r['name'], seed=r['seed'], issuance=issuance, horizon=h,
                                     report_shortfall=np.log(r_sum / y_sum), tree_correction=np.log(c_sum / r_sum),
                                     nowcast_error=np.log(c_sum / y_sum),
                                     growth_error=np.log(m_us / c_sum) - np.log(truth.get(('US', d), np.nan) / y_sum),
                                     total_error=np.log(m_us / truth.get(('US', d), np.nan))))
    d = pd.DataFrame(rows)
    s = d.groupby(['recipe', 'horizon'])[['report_shortfall', 'tree_correction', 'nowcast_error', 'growth_error', 'total_error']].mean()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    d.to_csv(out / f'{args.hub}-fits-rows.csv', index=False); s.to_csv(out / f'{args.hub}-fits-summary.csv')
    print(f'{args.hub}: US admissions, mean over reports {ISSUANCES[0]}..{ISSUANCES[-1]} and seeds of log ratios '
          f'(truth = Hub target data as of {t.as_of.max()}); positive = above truth')
    print((100 * (np.exp(s) - 1)).round(1).astype(str).add('%').to_string())


if __name__ == '__main__':
    main()
