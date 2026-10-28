"""Score the autoencoder exploration (experiments/autoenc-20261024): seed mixtures and per-seed means.

For every recipe of the given planner experiments: the equal-weight mixture of its seeds'
predictive distributions (`evaluation.ensembles`, scored like a run), and the per-seed mean
from `planner rank`. Extra groups (`--groups A+B ...`) mix recipes. Prints and writes
`summary.csv`: states/DC log(1 + admissions) WIS (selection score), native admissions WIS,
ED WIS, US log WIS, 90% coverage, per season. Lower WIS is better.

    python scripts/autoenc_score.py -e autoenc-20261024-r01 --out data/experiments/autoenc-20261024-score01
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from chromantis.evaluation.ensembles import main as ensembles
from chromantis.experiment.planner import collect, rank


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--experiments', nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--groups', nargs='*', default=[], help='Recipe mixtures, names joined by +')
    parser.add_argument('--seeds', nargs='+', type=int, default=None)
    args = parser.parse_args()
    root = Path('data/experiments')
    runs, per_seed = {}, []
    for name in args.experiments:
        rows = [r for r in collect(root / name) if r['status'] == 'complete' and (args.seeds is None or r['seed'] in args.seeds)]
        for r in rows:
            runs.setdefault(r['name'], []).append(str(root / name / r['attempt']))
        ranking = rank(root / name, allow_incomplete=True, seeds=args.seeds, report=False)
        per_seed.append(pd.read_csv(ranking / 'headline-rankings.csv'))
    recipes = {name: {'runs': sorted(paths)} for name, paths in runs.items()}
    groups = {name: [name] for name in recipes}
    for group in args.groups:
        members = group.split('+')
        if all(m in recipes for m in members) and len({len(recipes[m]['runs']) for m in members}) == 1:
            groups[group] = members
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'groups.json').write_text(json.dumps(dict(recipes=recipes, groups=groups, rules=['mixture'],
                                                          views=['corrected'], forecast_view='corrected'), indent=1))
    ensembles([str(args.out / 'groups.json'), '--out', str(args.out)])
    table = pd.read_csv(args.out / 'ranking' / 'headline-rankings.csv')
    table = table[table.deployed]
    table['recipe'] = table.name.str.replace(' (mixture)', '', regex=False)
    key = lambda t, s, g: table[(table.target.str.contains(t)) & (table.scale == s) & (table.geography == g)].set_index('recipe')['mean']
    out = pd.DataFrame({'mixture_log_states': key('hosp', 'log', 'states_dc'),
                        'mixture_native_states': key('hosp', 'natural', 'states_dc'),
                        'mixture_ed_states': key('ed', 'natural', 'states_dc'),
                        'mixture_log_us': key('hosp', 'log', 'US')})
    seeds = pd.concat(per_seed)
    seeds = seeds[seeds.deployed & seeds.target.str.contains('hosp') & (seeds.scale == 'log') & (seeds.geography == 'states_dc')]
    # Several experiments may hold seeds of one recipe: pool their per-seed means.
    pooled = seeds.assign(total=seeds['mean'] * seeds['count']).groupby('name')[['total', 'count']].sum()
    out['seed_mean_log_states'] = pooled.total / pooled['count']
    out['seeds'] = pooled['count']
    out['october_log_states'] = table[table.target.str.contains('hosp') & (table.scale == 'log') &
                                      (table.geography == 'states_dc')].set_index('recipe')['october']
    season = pd.read_csv(args.out / 'ranking' / 'headline-season-scores.csv')
    season = season[season.deployed & season.target.str.contains('hosp') & (season.scale == 'log') & (season.geography == 'states_dc')]
    season['recipe'] = season.name.str.replace(' (mixture)', '', regex=False)
    out = out.join(season.pivot(index='recipe', columns='season', values='mean_wis'))
    out = out.join(season.groupby('recipe').covered_90.mean().rename('coverage_90'))
    out = out.sort_values('mixture_log_states')
    out.to_csv(args.out / 'summary.csv')
    pd.set_option('display.width', 250)
    print(out.round(4).to_string())


if __name__ == '__main__':
    main()
