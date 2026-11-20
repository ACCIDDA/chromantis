"""Hub submission file for one current-season refit (2026-10-21).

Each seed's model (trained on every complete season, 2026-27 excluded) forecasts from the
latest published week before the reference date; 20 whole trajectories per seed form the
100 samples. Sample IDs S1..S100 are shared across weeks and locations because every location
comes from the same joint model draw (allowed by the Hub README). Values are percentages.
"""
import argparse, json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from chromantis.dataset.build import load
from chromantis.experiment.planner import collect
from chromantis.experiment.training import evaluate
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from export_metrocast_current import inference_episode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--experiment', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--reference', default='2026-10-24')
    ap.add_argument('--tasks', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--weeks', type=int, default=4)
    # 2026-10-28: weekly reruns of the frozen fits read that week's panel, not the fit-time one.
    ap.add_argument('--panel', help='Operational panel replacing the problem panel')
    a = ap.parse_args()
    folder = Path('data/experiments') / a.experiment
    members = sorted([r for r in collect(folder) if r['name'] == a.name and r['status'] == 'complete'],
                     key=lambda r: r['seed'])
    assert len(members) == 5, f'{len(members)} complete seeds'
    task = next(t for t in json.loads(Path(a.tasks).read_text())['rounds'][-1]['model_tasks']
                if 'Flu ED visits pct' in (t['task_ids']['target'].get('optional') or []))
    eligible = set(task['task_ids']['location']['optional'])
    torch.set_num_threads(4)
    draws, info = [], []
    for r in members:
        run = folder / r['attempt']
        problem = Problem.load(json.loads((run / 'manifest.json').read_text())['problem'])
        scenario = Scenario.from_string(r['scenario'])
        episode = inference_episode(load(a.panel or problem.panel), problem, scenario, a.reference)
        model = load_model(torch.load(run / 'eval_2026-2027/model.pt', map_location='cpu', weights_only=False))
        torch.manual_seed(r['seed'] + 1000)
        cache = Path(a.out).parent / 'cache' / f"s{r['seed']}"
        cache.mkdir(parents=True, exist_ok=True)
        evaluate(model, [episode], 128, 'cpu', cache, keep_samples=True)
        with np.load(cache / 'forecasts.npz') as f:
            d = f['samples'][0, :, :a.weeks, 0, :]
        draws.append(d[np.random.default_rng(r['seed'] + 2000).choice(len(d), 20, replace=False)])
        locations = [str(x) for x in episode['locations']]
        last = {loc: str(np.array(episode['context_dates'])[episode['available'][:, 0, i]][-1])
                for i, loc in enumerate(locations) if episode['available'][:, 0, i].any()}
        info.append(dict(seed=r['seed'], scenario=r['scenario'], panel=str(a.panel or problem.panel)))
    x = np.concatenate(draws)                       # [100, weeks, locations], proportions
    keep = [i for i, loc in enumerate(locations) if loc in eligible]
    ref = date.fromisoformat(a.reference)
    rows = []
    for i in keep:
        for w in range(a.weeks):
            for s in range(100):
                rows.append((a.reference, 'Flu ED visits pct', (ref + timedelta(weeks=w)).isoformat(), locations[i],
                             'sample', f'S{s + 1}', float(x[s, w, i]) * 100))
    out = pd.DataFrame(rows, columns=['reference_date', 'target', 'target_end_date', 'location', 'output_type',
                                      'output_type_id', 'value'])
    for c in ('reference_date', 'target_end_date'):   # the Hub schema requires Parquet dates
        out[c] = pd.to_datetime(out[c]).dt.date
    assert np.isfinite(out.value).all() and (out.value >= 0).all() and (out.value <= 100).all()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(a.out, index=False)
    summary = out.groupby(['location', 'target_end_date']).value.median().unstack()
    summary.insert(0, 'last_observed_week', [last.get(l) for l in summary.index])
    summary.to_csv(Path(a.out).with_suffix('.medians.csv'))
    (Path(a.out).with_suffix('.json')).write_text(json.dumps(dict(
        experiment=a.experiment, name=a.name, reference_date=a.reference, members=info,
        locations=len(keep), missing_eligible=sorted(eligible - {locations[i] for i in keep})), indent=1) + '\n')
    print(a.out, len(keep), 'locations; missing', sorted(eligible - {locations[i] for i in keep}))


if __name__ == '__main__':
    main()
