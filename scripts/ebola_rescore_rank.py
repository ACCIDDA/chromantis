"""Rank the five-window rescoring: natural-scale WIS per window, relative to the tree model.

Per recipe and window: mean WIS over seeds (natural scale, locations). Ranking score: geometric
mean over windows of (recipe WIS / gradient-boosted tree model WIS), so the large West Africa
counts do not dominate. Lower is better; 1.0 = the tree model. The tree model is the yardstick
(not the root reference recipe) because its scores exist before any Chromantis run finishes; the
root reference recipe is planned last. Only recipes with every window and at least `--seeds`
complete seeds are ranked.

    .venv/bin/python scripts/ebola_rescore_rank.py [--gbdt data/ebola/gbdt-multi/scores-raw.csv]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.experiment.planner import collect

EXPERIMENT = Path('data/experiments/ebola-rescore-multi')
STUDY = Path('experiments/ebola-20261026/rescore-multi.json')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=3)
    parser.add_argument('--gbdt', default='data/ebola/gbdt-multi/scores-raw.csv')
    parser.add_argument('--top', type=int, default=20)
    args = parser.parse_args()
    study = json.loads(STUDY.read_text())
    rows = []
    for r in collect(EXPERIMENT):
        path = EXPERIMENT / r['attempt'] / 'scores-raw.csv' if r['status'] == 'complete' else None
        if path is None or not path.exists():
            continue
        s = pd.read_csv(path)
        s = s[(s.history == 'raw') & (s.scale == 'natural') & (s.geography == 'locations')]
        rows += [dict(name=r['name'], seed=r['seed'], window=x.season, wis=x.mean_wis, cov90=x.covered_90) for x in s.itertuples()]
    d = pd.DataFrame(rows)
    seeds = d.groupby('name').seed.nunique()
    wide = d.groupby(['name', 'window']).wis.mean().unstack()
    wide = wide[(seeds.reindex(wide.index) >= args.seeds)].dropna()
    g = pd.read_csv(args.gbdt)
    yard = 'tree_model (gradient boosting)'
    wide.loc[yard] = g[g.scale == 'natural'].set_index('season').mean_wis.reindex(wide.columns)
    relative = wide / wide.loc[yard]
    out = wide.assign(geomean_relative=np.exp(np.log(relative).mean(1)),
                      cov90=d.groupby('name').cov90.mean().reindex(wide.index),
                      group=['top150' if n.startswith('top') else 'random50' if n.startswith('random') else n for n in wide.index],
                      search_score=[study['search_rank'].get(n) for n in wide.index]).sort_values('geomean_relative')
    out.round(3).to_csv(Path('experiments/ebola-20261026') / 'rescore-multi-rank.csv')
    print(f'{len(wide)} recipes complete with {args.seeds}+ seeds in every window')
    print(out.head(args.top).round(3).to_string())
    if 'root_reference' in out.index:
        print('\nroot reference:', out.loc['root_reference', 'geomean_relative'].round(3))
    print('\nMedian relative score by group:', out.groupby('group').geomean_relative.median().round(3).to_dict())
    print('Rank correlation, search score vs five-window score:',
          round(out.dropna(subset=['search_score'])[['search_score', 'geomean_relative']].corr('spearman').iloc[0, 1], 3))


if __name__ == '__main__':
    main()
