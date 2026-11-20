import fcntl,json,sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0,'scripts')
import metrocast_tree as t
from chromantis.model.scenario import Scenario
with (t.ROOT/'tree.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    state=t.load_state()
    source=json.loads((t.ROOT/'round-057-full-season-memory.json').read_text())
    candidates={}; parents={}
    for key,value in source['candidates'].items():
        name=key+'_lag1'
        candidates[name]=replace(Scenario.from_string(value),training_target_lag=1).scenario_string
        parents[name]=dict(parent_experiment='metrocast-full-season-memory-r057',parent_scenario=value,changes={'training_target_lag':1},reason='Test one-week missing target history during fitting and inner validation for full-season trajectories. Future labels and evaluation inputs unchanged; hypothesis transferred from archived county development benchmark, not assumed to match all main-panel releases.')
    print(t.plan(state,candidates,parents,[42,43,44,45],stage='full-season-delay',problem='problems/metrocast-flu-full-season.json',protocol=dict(inputs='Latest revised local histories with latest target-history week hidden during fitting and inner validation; existing state covariate release treatment unchanged.',labels='Future local flu ED proportions, unchanged; ILI/state ED pretraining as specified by scenario.',evaluation_inputs='Latest revised histories for 2024-25 long-horizon evaluation; this alone is not an operational ensemble benchmark.',selection='Four early-season 2024-25 origins, horizon bands through 33 and intact joint-path energy. No 2025-26 selection.')),flush=True)
    source=json.loads((t.ROOT/'round-059-county-delay.json').read_text())
    value=source['candidates']['county_initial_12week_none_lag1']; base=Scenario.from_string(value)
    changes=[('history24',dict(lookback=24)),('history36',dict(lookback=36)),('width64',dict(width=64)),('width256',dict(width=256)),('epochs80',dict(epochs=80)),('epochs320',dict(epochs=320)),('members128',dict(members=128)),('lag2',dict(training_target_lag=2))]
    candidates={}; parents={}
    for key,change in changes:
        candidates[key]=replace(base,**change).scenario_string
        parents[key]=dict(parent_experiment='metrocast-county-delay-r059',parent_scenario=value,changes=change,reason='One-factor branches from 12-week shared-weight model trained with latest target week hidden. Select only on archived 2024-25 county ensemble comparison.')
    print(t.plan(state,candidates,parents,[42,43,44,45],stage='county-delay-refine',problem='problems/metrocast-county-benchmark.json',protocol=dict(inputs='Revised 2022-23/2023-24 county histories; latest target week hidden during fitting and inner validation, or two weeks for lag2. No state covariates.',labels='Unchanged future county flu ED proportions.',evaluation_inputs='Strictly archived histories available by Wednesday for March 1-May 10 2025 reference dates; no revised fill.',selection='Same 190 tasks and nine quantiles versus epiENGAGE-ensemble_mean in five Texas counties; no 2025-26 selection.')),flush=True)
