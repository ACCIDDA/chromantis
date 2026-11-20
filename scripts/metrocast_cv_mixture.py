"""Quantile-average mixtures of the top 4-week CV recipes (2026-10-22).

Uses the forecasts the CV scorer saved (no refitting). Each recipe's forecast is the average of its
seeds' quantiles; a top-k mixture averages those across the k best recipes by cv_log_ratio. Scored
like the CV: per held-out season, WIS relative to the reference recipe's seed-averaged forecast on
common tasks, and on 2025-26 (archived Wednesday inputs) relative to the MetroCast ensemble.
"""
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.evaluation.standard import quantile_scores
from chromantis.experiment.planner import collect
from score_metrocast_confirmation import LEVELS, ensemble_tasks

ROOT = Path('experiments/metrocast-cv-20261021')
KEY = ['fold', 'reference_date', 'location', 'horizon']
QC = [f'q{x:g}' for x in LEVELS]


def frame(path, fold):
    with np.load(path) as f:
        idx = [int(np.flatnonzero(np.isclose(f['quantile_levels'], q))[0]) for q in LEVELS]
        q = f['quantiles'][idx, :, :4, 0, :]
        n, h, l = q.shape[1:]
        refs = [(date.fromisoformat(str(v)) + timedelta(days=7)).isoformat() for v in f['context_end']]
        d = pd.DataFrame(dict(fold=fold, reference_date=np.repeat(refs, h * l), location=np.tile(f['locations'], n * h),
                              horizon=np.tile(np.repeat(np.arange(h), l), n), observed=f['truth'][:, :4, 0, :].reshape(-1),
                              available=f['mask'][:, :4, 0, :].reshape(-1)))
        d[QC] = q.reshape(len(LEVELS), -1).T
    return d[d.available].drop(columns='available')


def recipe(scenario, rounds):
    parts = []
    for name in rounds:
        folder = Path('data/experiments') / name
        for r in collect(folder):
            if r['status'] != 'complete' or r['scenario'] != scenario:
                continue
            run = folder / r['attempt']
            for fold in json.loads((run / 'manifest.json').read_text())['folds']:
                sub = 'cv-archived-wednesday-inputs' if fold == '2025-2026' else 'cv-revised-inputs'
                p = run / f'eval_{fold}' / sub / 'forecasts.npz'
                if p.exists():
                    parts.append(frame(p, fold).assign(seed=r['seed']))
    d = pd.concat(parts).drop_duplicates(KEY + ['seed'])
    return d.groupby(KEY)[QC + ['observed']].mean()


def wis(d):
    return pd.Series(quantile_scores(d[QC].to_numpy(), d.observed.to_numpy(), LEVELS).wis.to_numpy(), index=d.index)


def main():
    state = json.loads((ROOT / 'tree.json').read_text())
    table = pd.read_csv(ROOT / 'cv-ranking.csv')
    table = table[(table.folds == 4) & (table.seeds >= 4)].sort_values('cv_log_ratio')
    top = table.scenario.head(10).tolist()
    forecasts = {s: recipe(s, state['rounds']) for s in top + [state['reference']]}
    common = forecasts[state['reference']].index
    for s in top:
        common = common.intersection(forecasts[s].index)
    ref = wis(forecasts[state['reference']].loc[common])
    ens, _ = ensemble_tasks()
    ens = ens.assign(fold='2025-2026').set_index(KEY)
    rows = []
    for k in (1, 2, 3, 5, 8, 10):
        mix = sum(forecasts[s].loc[common] for s in top[:k]) / k
        w = wis(mix)
        ratio = (w.groupby('fold').sum() / ref.groupby('fold').sum())
        a = mix[mix.index.get_level_values('fold') == '2025-2026']
        m = a.join(ens[[f'ensemble_q{x:g}' for x in LEVELS]], how='inner')
        e = pd.Series(quantile_scores(m[[f'ensemble_q{x:g}' for x in LEVELS]].to_numpy() / 100, m.observed.to_numpy(), LEVELS).wis.to_numpy(), index=m.index)
        wm = wis(m)
        loc = pd.DataFrame(dict(m=wm, e=e)).groupby('location').sum()
        rows.append(dict(top_k=k, cv_ratio=float(np.exp(np.log(ratio).mean())), **{f'ratio_{f}': v for f, v in ratio.items()},
                         ensemble_ratio_location_mean=float((loc.m / loc.e).mean()), ensemble_ratio_pooled=float(wm.sum() / e.sum()),
                         ensemble_tasks=len(m)))
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / 'cv-mixtures.csv', index=False)
    print('Recipes (best first):'); [print(' ', i + 1, s) for i, s in enumerate(top)]
    print(out.round(3).to_string(index=False))


if __name__ == '__main__':
    main()
