"""Does training with artificial nowcast noise (ebola_noise.py) help when the newest inputs are uncertain?

One task = one fold of problems/ebola-multi-outbreak.json (West Africa Jan-Jun 2015, Kivu Mar-Aug
2019, BDBV Jun, Aug and Sep 2026) x one submitted recipe x one seed x one training noise strength.
The model is trained on every week before the fold starts (final values, labels 1-4 weeks ahead,
noise on the five newest input weeks at the given strength), then forecasts every origin in the
fold twice: from the final values (clean inputs) and from 50 noisy copies of them at strength 1
(noisy inputs, the same draws for every model). 50 samples per origin; WIS from 23 quantiles
against final values, natural and log(1 + x) scale, lower is better. Also the response of the
outbreak-total forecast to the newest input week across the 50 noisy copies (log-log slope,
1 = follows it one for one).

    .venv/bin/python scripts/ebola_noise_backtest.py --task 0 --out DIR --device cuda
"""
import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, 'scripts')
from chromantis.dataset.cv import masked
from chromantis.dataset.episodes import calendar, episodes
from chromantis.experiment import training
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from ebola_noise import InputNoise
from ebola_project import RECIPES

FOLDS = ['wa-2015h1', 'kivu-2019mid', 'bdbv-jun', 'bdbv-aug', 'bdbv-sep']
SEEDS = [42, 43]
STRENGTHS = [0., .5, 1.]
TASKS = list(itertools.product(FOLDS, RECIPES, SEEDS, STRENGTHS))
DRAWS = 50
Q = np.array([.01, .025] + list(np.arange(.05, .951, .05)) + [.975, .99])


def wis(samples, y):
    """samples [S, ...], y [...] -> WIS [...]"""
    q = np.quantile(samples, Q, axis=0)
    d = y[None] - q
    return 2 * np.maximum(Q.reshape(-1, *[1] * y.ndim) * d, (Q.reshape(-1, *[1] * y.ndim) - 1) * d).mean(0)


def sample(model, batch):
    t = lambda k: torch.as_tensor(np.stack([e[k] for e in batch]))
    with torch.no_grad():
        out = model(values=t('values'), available=t('available'),
                    calendar=torch.as_tensor(calendar([e['context_dates'][-1] for e in batch])),
                    covariates=t('covariates') if 'covariates' in batch[0] else None, members=1,
                    locations=list(batch[0]['locations'])).numpy()
    return np.maximum(out[0, :, :, 0, :], 0)   # [members=1, batch, horizons, channels, locations] -> [batch, horizons, locations]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--task', type=int, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--device', default='cuda')
    args = ap.parse_args()
    fold, recipe, seed, strength = TASKS[args.task]
    problem, scenario = Problem.load('problems/ebola-multi-outbreak.json'), Scenario.from_string(RECIPES[recipe])
    with np.load(problem.panel) as d:
        panel = {k: d[k] for k in d.files}
    dates = panel['dates'].astype(str)
    meta = pd.read_csv(problem.locations).set_index('location')
    names = problem.input_names(scenario.input_set), problem.covariate_names(scenario.covariate_set)
    keep = problem.training_weeks(dates, fold)
    train = [e for e in episodes(masked(panel, keep), problem, names[0], scenario.lookback, 'scheduled_final', names[1],
                                 horizons=problem.model_horizons(scenario)) if e['context_dates'][-1] in set(dates[keep])]
    first, last = problem.periods[fold]
    origins = [e for e in episodes(panel, problem, names[0], scenario.lookback, 'scheduled_final', names[1],
                                   horizons=problem.horizons) if first <= e['context_dates'][-1] <= last]
    torch.manual_seed(seed)
    noise = InputNoise(problem, strength) if strength else None
    model, _ = training.fit_models(train, None, train, problem, scenario, seed, torch.device(args.device),
                                   problem.populations(train[0]['locations']), augmenter=noise)
    model = model.cpu().eval()
    test_noise = InputNoise(problem, 1.)
    locations = list(origins[0]['locations'])
    rows, slopes = [], []
    for e in origins:
        rng = np.random.default_rng(int(e['context_dates'][-1].replace('-', '')))   # same noisy inputs for every model
        noisy = [test_noise.draw(e, rng) for _ in range(DRAWS)]
        y, ok = e['target_values'][:, 0, :], e['target_available'][:, 0, :]
        top = [c for c in locations if meta.level[c] == 'top' and ok[:, locations.index(c)].any()][0]
        for inputs, batch in (('clean', [e] * DRAWS), ('noisy', noisy)):
            s = sample(model, batch)
            for scale, f in (('natural', lambda x: x), ('log', np.log1p)):
                w = wis(f(s), f(y))
                for h, l in zip(*np.where(ok)):
                    rows.append((fold, recipe, seed, strength, inputs, e['context_dates'][-1], locations[l],
                                 meta.level[locations[l]], h + 1, scale, w[h, l]))
            if inputs == 'noisy':
                i = locations.index(top)
                x = np.log1p(np.array([b['values'][-1, 0, i] for b in batch]))
                for h in range(s.shape[1]):
                    slopes.append((fold, recipe, seed, strength, e['context_dates'][-1], h + 1,
                                   np.polyfit(x, np.log1p(s[:, h, i]), 1)[0]))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tag = f'{fold}-{recipe}-s{seed}-n{strength}'
    pd.DataFrame(rows, columns=['fold', 'recipe', 'seed', 'train_noise', 'inputs', 'origin', 'location', 'level', 'horizon',
                                'scale', 'wis']).to_csv(out / f'scores-{tag}.csv', index=False)
    pd.DataFrame(slopes, columns=['fold', 'recipe', 'seed', 'train_noise', 'origin', 'horizon', 'slope']).to_csv(
        out / f'slopes-{tag}.csv', index=False)
    print(tag, len(origins), 'origins done', flush=True)


if __name__ == '__main__':
    main()
