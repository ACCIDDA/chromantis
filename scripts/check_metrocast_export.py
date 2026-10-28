"""Exercise current-input export using development checkpoints; never publish."""
import json
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from export_metrocast_current import inference_episode
from score_metrocast_confirmation import prepare_archive, replay_episode
from chromantis.dataset.build import load
from chromantis.experiment.planner import collect
from chromantis.experiment.training import evaluate
from chromantis.metrocast import write_samples
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=['all', 'fullseason', 'california', 'utah'], default='all')
    args = parser.parse_args()
    torch.set_num_threads(1)
    root = Path('output/metrocast/export-diagnostic')
    results = []
    for kind, experiment, target in [
        ('fullseason', 'metrocast-full-season-memory-r057', 'Flu ED visits pct'),
        ('california', 'metrocast-california-pilot-r065', 'Flu hosp admits'),
        ('utah', 'metrocast-utah-proposed-fullseason-r074', 'Flu ED visits pct'),
    ]:
        if args.kind != 'all' and args.kind != kind:
            continue
        folder = Path('data/experiments') / experiment
        record = next(r for r in collect(folder)
                      if r['status'] == 'complete' and r['seed'] == 42
                      and (r['name'] == 'mlp12_logit_80epochs_none_lag0'
                           if kind == 'utah' else r['name'].startswith('direct')))
        scenario = Scenario.from_string(record['scenario'])
        problem = Problem.load(f'problems/metrocast-current-{kind}.json')
        episode = inference_episode(load(problem.panel), problem, scenario)
        if kind == 'fullseason':
            archive = prepare_archive(pd.read_csv('data/metrocast/source/time-series.csv'))
            metadata = pd.read_csv('data/metrocast/locations.csv').set_index('location')
            episode = replay_episode(episode, archive, metadata)
        run = folder / record['attempt']
        manifest = json.loads((run / 'manifest.json').read_text())
        assert len(manifest['folds']) == 1
        checkpoint = run / f"eval_{manifest['folds'][0]}" / 'model.pt'
        model = load_model(torch.load(checkpoint, map_location='cpu', weights_only=False))
        destination = root / kind
        destination.mkdir(parents=True, exist_ok=True)
        torch.manual_seed(1042)
        evaluate(model, [episode], 128, 'cpu', destination, keep_samples=True)
        with np.load(destination / 'forecasts.npz') as cache:
            assert not cache['mask'].any(), 'Diagnostic must not score future outcomes'
            draws = cache['samples'][0, :, :, 0, :]
        tasks = json.loads(Path('data/metrocast/source/tasks.json').read_text())
        task = next(t for t in tasks['rounds'][-1]['model_tasks']
                    if target in (t['task_ids']['target'].get('optional') or []))
        eligible = set(task['task_ids']['location']['optional'])
        indices = [i for i, loc in enumerate(episode['locations'])
                   if loc in eligible and loc != 'nyc']
        locations = [episode['locations'][i] for i in indices]
        draws = draws[:, :, indices]
        full = write_samples(draws, locations, '2026-10-24',
                             destination / 'diagnostic-trajectories.parquet', target=target)
        short = write_samples(draws[:, :4], locations, '2026-10-24',
                              destination / 'diagnostic-four-week.parquet', target=target)
        keys = ['output_type_id', 'target_end_date', 'location']
        subset = full[full['target_end_date'].isin(short['target_end_date'])]
        pd.testing.assert_frame_equal(subset.sort_values(keys).reset_index(drop=True),
                                      short.sort_values(keys).reset_index(drop=True))
        assert len(full.columns) == 7 and 'horizon' not in full
        assert full.groupby(['location', 'output_type_id']).size().eq(34).all()
        assert full['target_end_date'].max().isoformat() == '2027-06-12'
        chosen = np.random.default_rng(42).choice(len(draws), 100, replace=False)
        expected = draws[chosen].reshape(-1).astype(float)
        if target == 'Flu ED visits pct':
            expected *= 100
        np.testing.assert_array_equal(full['value'].to_numpy(), expected)
        saved = pd.read_parquet(destination / 'diagnostic-trajectories.parquet')
        np.testing.assert_array_equal(saved['value'].to_numpy(), full['value'].to_numpy())
        results.append(dict(
            kind=kind, development_checkpoint=str(checkpoint),
            scenario=record['scenario'], rows=len(full), locations=len(locations),
            weeks=34, paths=100, last_target='2027-06-12',
            future_labels_scored=False, production_model=False, published=False,
            missing_eligible_locations=sorted(eligible - set(locations)),
            input_history_cells=int(episode['available'].sum()),
            checks='Intact paths, same four-week subset, native units, Parquet round trip',
        ))
        if kind == 'utah':
            assert set(locations) == set(episode['locations']) and len(locations) == 14
            results[-1]['source'] = json.loads(Path('data/metrocast-utah-proposed/manifest.json').read_text())
            results[-1]['submission_ready'] = False
        print(json.dumps(results[-1]), flush=True)
    filename = 'checks.json' if args.kind == 'all' else f'{args.kind}-checks.json'
    (root / filename).write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
