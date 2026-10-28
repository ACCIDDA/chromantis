"""Score completed ED experiments separately by learned targets, with shared scorer."""
import argparse,json,hashlib
from pathlib import Path
from chromantis.experiment.planner import ranking_runs
from chromantis.evaluation.ranking import rank
from chromantis.model.scenario import Scenario
p=argparse.ArgumentParser();p.add_argument('-e',required=True);p.add_argument('--allow-incomplete',action='store_true');p.add_argument('--no-report',action='store_true');a=p.parse_args()
f=Path('data/experiments')/a.e
settings=json.loads((f/'experiment.json').read_text())
from chromantis.problem import Problem
if Problem.load(settings['problem']).production:
    print('Production fits have no held-out scores; inspect planner status for completion.')
    raise SystemExit(0)
runs,_=ranking_runs(f,a.allow_incomplete)
groups={}
for r in runs:groups.setdefault(Scenario.from_string(r['config_id']).loss_weights,[]).append(r)
for label,rows in groups.items():
 key=hashlib.sha256(json.dumps(sorted(str(r['path']) for r in rows)).encode()).hexdigest()[:12]
 dest=f/f'ranking-{label}-{key}'
 rank(rows,settings['frozen'],dest);print(dest,flush=True)
