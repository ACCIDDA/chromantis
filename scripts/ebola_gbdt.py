"""Simple gradient-boosted-tree forecaster for weekly Ebola cases, scored like Chromantis.

One quantile regression tree ensemble per quantile level (sklearn HistGradientBoosting),
pooled over every location, outbreak and horizon (horizon is a feature). Features are the
recent log counts of the location, its parent (province/country) and the whole outbreak,
seen at the forecast origin; the label is log(1 + count) h weeks later. It uses the same
panel, the same rolling-origin windows and the same finalized inputs as the Chromantis
problem file, and writes the same WIS summary (natural and log scale, over locations).

    .venv/bin/python scripts/ebola_gbdt.py --problem problems/ebola-bdbv-screen.json --out data/ebola/gbdt-screen
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from chromantis.evaluation.quantiles import LEVELS
from chromantis.evaluation.standard import quantile_scores
from chromantis.problem import Problem

LAGS = 8


def features(y, parent, total, level, t):
    """[L, F] features at origin index t from [T, L] finalized histories (NaN = missing)."""
    lag = lambda a, k: np.log1p(a[t - k]) if t - k >= 0 else np.full(a.shape[1], np.nan)
    own = [lag(y, k) for k in range(LAGS)]
    seen = np.nan_to_num(y[:t + 1], nan=0)
    cum = np.log1p(seen.sum(0))
    first = np.where(seen.any(0), t - np.argmax(seen > 0, 0), -1)  # weeks since the first case
    mean2, mean4 = np.nanmean(np.stack(own[:2]), 0), np.nanmean(np.stack(own[:4]), 0)
    return np.column_stack(own + [lag(parent, k) for k in range(4)] + [lag(total, k) for k in range(4)]
                           + [mean2, mean4, own[0] - own[2], mean2 - np.nanmean(np.stack(own[2:6]), 0),
                              cum, first, level])


def rows(panel, weeks, horizons, allowed_label):
    y, parent, total, level = panel
    X, Y, keys = [], [], []
    for t in weeks:
        if t < 1:
            continue
        f = features(y, parent, total, level, t)
        active = np.isfinite(y[t])
        for h in horizons:
            if t + h >= len(y):
                continue
            label = y[t + h] if allowed_label(t + h) else np.full(y.shape[1], np.nan)
            keep = active & np.isfinite(label)
            for i in np.flatnonzero(keep):
                X.append(np.r_[f[i], h])
                Y.append(np.log1p(label[i]))
                keys.append((t, h, i))
    return np.array(X, np.float32), np.array(Y, np.float32), keys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--problem', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--max-iter', type=int, default=300)
    parser.add_argument('--learning-rate', type=float, default=.05)
    parser.add_argument('--min-leaf', type=int, default=40)
    args = parser.parse_args()
    problem = Problem.load(args.problem)
    with np.load(problem.panel) as d:
        dates = d['dates'].astype(str)
        locations = d['locations'].astype(str)
        y, cov = d['targets'][..., 0], d['covariates']
    meta = pd.read_csv(problem.locations).set_index('location').loc[locations]
    level = meta.level.map({'local': 0, 'middle': 1, 'top': 2}).to_numpy(float)
    panel = (y, cov[..., 0], cov[..., 1], np.broadcast_to(level, y.shape[1:]))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary, cells = [], []
    for fold in problem.folds:
        first, last = problem.periods[fold]
        before = np.flatnonzero(dates < first)
        in_window = np.flatnonzero((dates >= first) & (dates <= last))
        # Training labels must also precede the window: nothing from the held-out weeks.
        X, Y, _ = rows(panel, before, problem.horizons, lambda j: dates[j] < first)
        # Score tasks: origins in the window, labels inside the window (as the Chromantis evaluator).
        Xs, Ys, keys = rows(panel, in_window, problem.horizons, lambda j: dates[j] <= last)
        q = np.column_stack([
            HistGradientBoostingRegressor(loss='quantile', quantile=float(a), max_iter=args.max_iter,
                                          learning_rate=args.learning_rate, min_samples_leaf=args.min_leaf,
                                          random_state=0).fit(X, Y).predict(Xs) for a in LEVELS])
        q = np.expm1(np.maximum(np.sort(q, 1), 0))  # non-crossing, non-negative counts
        truth = np.expm1(Ys)
        for scale in ('natural', 'log'):
            tq, ty = (np.log1p(q), np.log1p(truth)) if scale == 'log' else (q, truth)
            s = quantile_scores(tq, ty)
            summary.append(dict(season=fold, scale=scale, geography='locations', mean_wis=s.wis.mean(),
                                tasks=len(s), covered_50=s.covered_50.mean(), covered_90=s.covered_90.mean(),
                                first_reference=dates[in_window[0]], last_reference=dates[in_window[-1]]))
            if scale == 'natural':
                cells.append(pd.DataFrame(dict(season=fold, origin=[dates[k[0]] for k in keys], horizon=[k[1] for k in keys],
                                               location=[locations[k[2]] for k in keys], truth=truth,
                                               wis=s.wis, **{f'q{a:g}': q[:, j] for j, a in enumerate(LEVELS)})))
        print(f'{fold}: {len(X)} training rows, {len(Xs)} score tasks', flush=True)
    summary = pd.DataFrame(summary)
    summary.to_csv(out / 'scores-raw.csv', index=False)
    pd.concat(cells).to_csv(out / 'scores-cells.csv', index=False)
    (out / 'settings.json').write_text(json.dumps(vars(args), indent=2) + '\n')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
