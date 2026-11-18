"""Score California 'Flu hosp admits' fits held out by season (leave one season out).

Rewritten 2026-11-11 for the four-season panel (private CDPH files + Hub data); the earlier
version scored one 2025-26 fold and resampled seed mixtures. Here: WIS of each fit's saved
quantiles against revised labels, location mean per held-out season, then the mean over
seeds and over seasons. Band labels count weeks after the last data week from 0; the Hub's
horizons -1..3 are weeks 0-4.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from chromantis.evaluation.standard import quantile_scores
from chromantis.experiment.planner import collect

BANDS = [('hub -1..3 (0-4)', 0, 5), ('5-12', 5, 13), ('13-25', 13, 26), ('0-33', 0, 34)]


def main():
    p = argparse.ArgumentParser(); p.add_argument('-e', '--experiment', required=True); a = p.parse_args()
    root = Path('data/experiments')/a.experiment
    rows = []
    for r in collect(root):
        if r['status'] != 'complete':
            continue
        for folder in sorted((root/r['attempt']).glob('eval_*')):
            with np.load(folder/'forecasts.npz') as f:
                q = f['quantiles'][:, :, :, 0, :]; y = f['truth'][:, :, 0, :]; mask = f['mask'][:, :, 0, :].astype(bool); levels = f['quantile_levels']
            wis = quantile_scores(q.reshape(len(levels), -1).T, y.reshape(-1), levels).wis.to_numpy().reshape(y.shape)
            for band, start, stop in BANDS:
                seen = mask[:, start:stop]; n = seen.sum((0, 1))
                loc = np.where(seen, wis[:, start:stop], 0).sum((0, 1))/np.maximum(n, 1)
                rows.append(dict(name=r['name'], scenario=r['scenario'], seed=r['seed'], held_out_season=folder.name[5:],
                                 band=band, wis=float(loc[n > 0].mean()), cells=int(n.sum())))
    seeds = pd.DataFrame(rows)
    seeds.to_csv(root/'california-season-scores.csv', index=False)
    by_season = seeds.groupby(['name', 'band', 'held_out_season']).wis.mean().unstack()
    summary = by_season.assign(mean_over_seasons=by_season.mean(axis=1),
                               seeds=seeds.groupby(['name', 'band']).seed.nunique()).reset_index()
    summary.to_csv(root/'california-summary.csv', index=False)
    hub = summary[summary.band == 'hub -1..3 (0-4)'].sort_values('mean_over_seasons')
    print('Mean WIS (admissions, location mean, lower is better), weeks matching Hub horizons -1..3, per held-out season:')
    print(hub.drop(columns='band').round(1).to_string(index=False))


if __name__ == '__main__':
    main()
