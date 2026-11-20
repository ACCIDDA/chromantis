"""Gradient-boosted quantile regression (GBQR) flu member, paired with fitted network runs (flu search, 20 Nov 2026).

Why: the best FluSight models of 2024-25 and 2025-26 are mostly ensembles of structurally different models; the
core of UMass-flusion (and close to CMU-TimeSeries) is a quantile regression pooled over locations on lagged,
transformed admissions. Our submitted mixture has three similar networks. This member gives a different learner
for mixtures, trained and evaluated on exactly the same tasks as a paired network run.

For each completed run of RECIPE in EXPERIMENT and each held-out season (fold) of that run:
  training rows  every (origin, location, horizon) of the fold's training seasons on finalized histories
                 (`scheduled_final` episodes, the same fold masking as the network); with --bag, a bootstrap of
                 origins seeded by the run's seed
  features       log(1 + admissions per 100k) of the newest week and its 1/2/4-week changes, 4-week mean change,
                 distance below the lookback maximum, ED share on the logit scale with the same changes, the US
                 total's level and 1/2-week changes, annual phase and weeks from Christmas, log population, horizon
  labels         change of the transformed value from the newest week to the target week (finalized values)
  model          sklearn HistGradientBoostingRegressor(loss='quantile') per Hub quantile level and target
  inputs         the held-out season's Wednesday reports at the FluSight deadline, newest weeks corrected by the
                 paired run's own saved correction trees (`nowcaster.pkl`), i.e. the paired run's corrected view
Writes run folders data/experiments/OUT/gbqr/s<seed>/attempt-001/eval_<season>/corrected/forecasts.npz: the paired
run's file with its quantiles replaced, so tasks, truth and masks are identical. Score with evaluation.ensembles
(groups listing these run folders), alone or mixed with network recipes.

    PYTHONPATH=src .venv/bin/python scripts/flu_gbqr.py EXPERIMENT RECIPE OUT [--bag] [--workers 8]
"""
import argparse
import csv
import json
import pickle
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

LEVELS = np.array([.01, .025, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9, .95, .975, .99])


def transform(values, unit, pop):
    """Admissions -> log(1 + per-100k rate); ED proportion -> logit."""
    if unit == 'count':
        return np.log1p(np.maximum(values, 0) / pop * 1e5)
    p = np.clip(values, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def inverse(z, unit, pop):
    if unit == 'count':
        return np.maximum(np.expm1(z) * pop / 1e5, 0)
    return 1 / (1 + np.exp(-z))


def features(e, pops, us_index):
    """Rows [location, feature] for channels 0 (admissions) and 1 (ED) of one episode, and the newest transformed values."""
    from chromantis.dataset.episodes import calendar
    v, ok = e['values'], e['available']
    out, newest = [], []
    for c, unit in enumerate(e['input_units'][:2]):
        z = np.where(ok[:, c], transform(v[:, c], unit, pops[None]), np.nan)  # [lookback, L]
        last = z[-1]
        lag = lambda k: z[-1 - k]
        cols = [last, last - lag(1), last - lag(2), last - lag(4), lag(1) - lag(2),
                np.nanmean(z[-4:], 0) - np.nanmean(z[-8:-4], 0), np.nanmax(z, 0) - last]
        if c == 0:
            us = z[:, us_index]
            cols += [np.full_like(last, us[-1]), np.full_like(last, us[-1] - us[-2]), np.full_like(last, us[-1] - us[-3])]
        out += cols
        newest.append(last)
    cal = calendar([e['context_dates'][-1]])[0]
    out += [np.full_like(newest[0], x) for x in cal] + [np.log(pops)]
    with np.errstate(all='ignore'):
        return np.stack(out, 1), newest


def rows(eps, pops, us_index, units, horizons):
    X, Y = [], [[], []]
    for e in eps:
        f, newest = features(e, pops, us_index)
        for i, h in enumerate(horizons):
            X.append(np.c_[f, np.full(len(f), h)])
            for c in (0, 1):
                y = np.where(e['target_available'][i, c], transform(e['target_values'][i, c], units[c], pops), np.nan) - newest[c]
                Y[c].append(y)
    return np.concatenate(X), [np.concatenate(y) for y in Y]


def fit_fold(task):
    fold_dir, out_dir, bag, seed = task
    import sys
    sys.path.insert(0, 'src')
    from chromantis.dataset import cv
    from chromantis.dataset.build import load
    from chromantis.model.scenario import Scenario
    from chromantis.problem import Problem
    meta = json.loads((fold_dir / 'manifest.json').read_text())
    problem, held_out = Problem.load(meta['problem']), meta['held_out_season']
    paired = Scenario.from_string(meta['scenario'])
    panel = load(meta['dataset'])
    # Same inputs as the paired run's corrector expects (its covariates feed the coverage columns).
    scen = Scenario.from_string(f'input_set={paired.input_set},covariate_set={paired.covariate_set},lookback={max(paired.lookback, 8)}')
    locations = [str(l) for l in panel['locations']]
    pops = np.array([problem.populations(locations)[l] for l in locations])
    us_index = locations.index('US')
    train = cv.fold(panel, problem, scen, held_out, inputs='scheduled_final').train
    rng = np.random.default_rng(seed + 777)
    if bag:
        train = [train[i] for i in rng.integers(len(train), size=len(train))]
    units = train[0]['target_units']
    horizons = list(problem.horizons)
    X, Y = rows(train, pops, us_index, units, horizons)
    score = cv.score_episodes(panel, problem, scen, held_out, 'flusight')
    with (fold_dir / 'nowcaster.pkl').open('rb') as f:
        corrector = pickle.load(f)
    score = corrector.apply_batch(score)
    paired_file = fold_dir / 'corrected' / 'forecasts.npz'
    data = dict(np.load(paired_file))
    index = {d: i for i, d in enumerate(data['context_end'])}
    q = data['quantiles'].astype(np.float64).copy()  # [levels, issuance, horizon, target, location]
    for c in (0, 1):
        ok = np.isfinite(Y[c]) & np.isfinite(X[:, 0 if c == 0 else 10])
        preds = []
        for level in LEVELS:
            m = HistGradientBoostingRegressor(loss='quantile', quantile=level, max_iter=200, learning_rate=.05,
                                              max_leaf_nodes=15, min_samples_leaf=40, random_state=seed)
            m.fit(X[ok], Y[c][ok])
            preds.append(m)
        for e in score:
            i = index.get(e['context_dates'][-1])
            if i is None:
                continue
            f, newest = features(e, pops, us_index)
            for k, h in enumerate(horizons):
                x = np.c_[f, np.full(len(f), h)]
                d = np.sort(np.stack([m.predict(x) for m in preds]), axis=0)  # [levels, L]
                base = np.where(np.isfinite(newest[c]), newest[c], np.nan)
                value = inverse(base[None] + d, units[c], pops[None])
                fill = np.isfinite(value)
                q[:, i, k, c][fill] = value[fill]
    q[:, :, :, 0] = np.floor(q[:, :, :, 0] + .5)
    data['quantiles'] = q.astype(np.float32)
    target = out_dir / f'eval_{held_out}' / 'corrected'
    target.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(target / 'forecasts.npz', **data)
    shutil.copy(fold_dir / 'manifest.json', out_dir / f'eval_{held_out}' / 'manifest.json')
    return str(target)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('experiment')
    ap.add_argument('recipe')
    ap.add_argument('out')
    ap.add_argument('--bag', action='store_true')
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--tag', default='gbqr')
    a = ap.parse_args()
    root = Path('data/experiments') / a.experiment
    runs = [r for r in csv.DictReader(open(root / 'runs.csv')) if r['name'] == a.recipe and r['status'] == 'complete']
    tasks, made = [], []
    for r in runs:
        run = root / r['attempt']
        out = Path('data/experiments') / a.out / a.tag / f's{r["seed"]}' / 'attempt-001'
        out.mkdir(parents=True, exist_ok=True)
        manifest = json.loads((run / 'manifest.json').read_text())
        manifest.update(gbqr=dict(paired_run=str(run), bag=a.bag, definition=__doc__))
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
        made.append(str(out))
        for season in manifest['folds']:
            tasks.append((run / f'eval_{season}', out, a.bag, int(r['seed'])))
    with ProcessPoolExecutor(a.workers) as pool:
        for t in pool.map(fit_fold, tasks):
            print('wrote', t, flush=True)
    (Path('data/experiments') / a.out / f'{a.tag}-runs.json').write_text(json.dumps(made, indent=1))


if __name__ == '__main__':
    main()
