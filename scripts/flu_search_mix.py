"""Write a groups file of seed mixtures for the flu search and print the scoring command (run in the Longleaf campaign folder).

Each member is a recipe name gathered across experiments (round, reseed) from their runs.csv, or a GBQR run list
(scripts/flu_gbqr.py writes data/experiments/OUT/<tag>-runs.json). Every recipe in a group gets equal weight and
the same seeds (the seeds every member has, sorted, at most --max-seeds), as evaluation.ensembles requires.

    .venv/bin/python scripts/flu_search_mix.py NAME --members 'B7=ref.A,ref.B5,ref.B' 'Bq=Bq' \
        --experiments flu-s-r01 flu-s-rs01 --gbqr G=flu-gbqr-r01/gbqr --groups 'B7:B7' 'B7+G:B7,G' [--max-seeds 16]
A member 'B7=ref.A,ref.B5,ref.B' expands to three recipes (labels B7/ref.A, ...); a group 'B7+G:B7,G' lists members.
"""
import argparse
import csv
import json
from pathlib import Path


def runs_of(name, experiments):
    found = {}
    for e in experiments:
        path = Path('data/experiments') / e / 'runs.csv'
        if not path.exists():
            continue
        for r in csv.DictReader(open(path)):
            if r['name'] == name and r['status'] == 'complete' and int(r['seed']) not in found:
                found[int(r['seed'])] = (str(Path('data/experiments') / e / r['attempt']), r['scenario'])
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--members', nargs='+', default=[])
    ap.add_argument('--experiments', nargs='+', required=True)
    ap.add_argument('--gbqr', nargs='*', default=[])
    ap.add_argument('--groups', nargs='+', required=True)
    ap.add_argument('--max-seeds', type=int, default=16)
    ap.add_argument('--study', default='experiments/flu-search-20261120', help='folder that receives mix-NAME.json')
    ap.add_argument('--prefix', default='flu-mix', help='experiment and job name prefix of the scoring')
    ap.add_argument('--seeds', help='restrict to seeds FIRST-LAST, so every group of a block uses the same seeds')
    a = ap.parse_args()
    members = {}
    for m in a.members:
        label, names = m.split('=')
        members[label] = {n: runs_of(n, a.experiments) for n in names.split(',')}
    for g in a.gbqr:
        label, rel = g.split('=')
        out, tag = rel.split('/')
        runs = json.load(open(Path('data/experiments') / out / f'{tag}-runs.json'))
        scen = json.load(open(Path(runs[0]) / 'manifest.json'))['scenario']
        members[label] = {label: {int(Path(r).parent.name[1:]): (r, scen) for r in runs}}
    groups, recipes = {}, {}
    for g in a.groups:
        gname, labels = g.split(':')
        parts = [(label, n, found) for label in labels.split(',') for n, found in members[label].items()]
        seeds = sorted(set.intersection(*(set(found) for _, _, found in parts)))
        if a.seeds:
            lo, hi = map(int, a.seeds.split('-'))
            seeds = [s for s in seeds if lo <= s <= hi]
        seeds = seeds[:a.max_seeds]
        if not seeds:
            raise SystemExit(f'{gname}: no common seeds')
        keys = []
        for label, n, found in parts:
            key = f'{n}@{len(seeds)}s{seeds[0]}'
            recipes[key] = dict(runs=[found[s][0] for s in seeds], scenario=found[seeds[0]][1])
            keys.append(key)
        groups[f'{gname} [{len(seeds)} seeds]'] = keys
    spec = dict(description=f'{Path(a.study).name} mixtures {a.name}', recipes=recipes, groups=groups, rules=['mixture'],
                views=['corrected'], forecast_view='corrected')
    path = Path(a.study) / f'mix-{a.name}.json'
    path.write_text(json.dumps(spec, indent=1) + '\n')
    for k, v in groups.items():
        print(k, '=', v)
    print(f'sbatch --job-name={a.prefix}-{a.name} scripts/covid_tree_mix.sbatch {path} data/experiments/{a.prefix}-{a.name}')


if __name__ == '__main__':
    main()
