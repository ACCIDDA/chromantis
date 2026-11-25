"""Write a draft release manifest from flu-search release fits (run in the Longleaf campaign folder).

    .venv/bin/python scripts/flu_search_release.py NAME OUT.json EXPERIMENT:RECIPE=LABEL [...] --description TEXT
        [--hub rsv --problem problems/us-rsv-production-coverage.json]   (COVID/RSV search, 25 Nov 2026)
Each member: every completed seed of RECIPE in EXPERIMENT (production problem, held-out fold 2026-2027), with the
SHA-256 of its model.pt, as production/releases/*.json expect. Checkpoints stay in the campaign folder (absolute paths).
"""
import argparse, csv, json
from pathlib import Path
from chromantis.experiment.provenance import sha256

ap = argparse.ArgumentParser()
ap.add_argument('name'); ap.add_argument('out'); ap.add_argument('members', nargs='+')
ap.add_argument('--description', required=True)
ap.add_argument('--hub', default='flusight')
ap.add_argument('--problem', default='problems/us-flu-production.json')
a = ap.parse_args()
recipes = {}
for m in a.members:
    left, label = m.split('=')
    exps, recipe = left.rsplit(':', 1)
    rows = []
    for exp in exps.split('+'):
        root = Path('data/experiments') / exp
        rows += [(int(r['seed']), root / r['attempt'] / 'eval_2026-2027') for r in csv.DictReader(open(root / 'runs.csv'))
                 if r['name'] == recipe and r['status'] == 'complete']
    rows = sorted(dict(rows).items())
    recipes[label] = [dict(checkpoint=str(p.resolve()), sha256=sha256(p / 'model.pt')) for _, p in rows]
    print(label, len(rows), 'seeds', rows[0][0], '-', rows[-1][0])
json.dump(dict(name=a.name, model_abbr='Chromantis', hub=a.hub, problem=a.problem, rule='mixture',
               view='corrected', description=a.description, recipes=recipes), open(a.out, 'w'), indent=1)
print('wrote', a.out)
