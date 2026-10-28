"""Export local review artifacts from separately fitted current-season models."""
import argparse
from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from chromantis.dataset.build import load
from chromantis.dataset.episodes import episodes
from chromantis.experiment.planner import collect
from chromantis.experiment.provenance import sha256
from chromantis.experiment.training import evaluate
from chromantis.metrocast import write_samples
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from score_metrocast_confirmation import prepare_archive, replay_episode

REFERENCE = '2026-10-24'
ROOT = Path('experiments/metrocast-20261019')


def inference_episode(panel, problem, scenario, reference=REFERENCE):
    """Pad missing current weeks, never fabricate observations or future labels."""
    panel = dict(panel)
    context = date.fromisoformat(reference)-timedelta(days=7)
    dates = list(map(str, panel['dates']))
    count = max(0, (context-date.fromisoformat(dates[-1])).days//7)
    if count:
        panel['dates'] = np.array(dates+[
            (date.fromisoformat(dates[-1])+timedelta(weeks=i)).isoformat()
            for i in range(1, count+1)])
        for key in ('targets', 'covariates', 'covariates_national'):
            x = panel[key]
            panel[key] = np.concatenate([x, np.full((count, *x.shape[1:]), np.nan, dtype=x.dtype)])
    result = [e for e in episodes(panel, problem, problem.input_names(scenario.input_set),
                                  scenario.lookback, 'scheduled_final',
                                  problem.covariate_names(scenario.covariate_set),
                                  horizons=problem.horizons, require_labels=False)
              if e['context_dates'][-1] == context.isoformat()]
    assert len(result) == 1
    episode = result[0]
    assert episode['target_dates'][0] == reference
    assert not episode['target_available'].any(), 'Future outcomes unexpectedly visible'
    return episode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--experiment', required=True)
    args = parser.parse_args()
    tree = json.loads((ROOT/'tree.json').read_text())
    kind = next((k for k, v in tree.get('current_refits', {}).items() if v == args.experiment), None)
    assert kind is not None, 'Export requires a separately planned current-season refit'
    frozen = json.loads((ROOT/f'current-{kind}-selection.json').read_text())
    assert frozen['experiment'] == args.experiment
    if kind == 'utah':
        source_selection = json.loads((ROOT/'utah-frozen-selection.json').read_text())
        assert sha256('data/metrocast-utah-proposed/manifest.json') == source_selection['proposed_manifest_sha256']
    folder = Path('data/experiments')/args.experiment
    records = collect(folder)
    assert records and all(r['status'] == 'complete' for r in records)
    groups = defaultdict(list)
    for record in records:
        assert record['scenario'] == frozen['candidates'][record['name']]
        groups[record['name']].append(record)
    archive = None if kind in {'california', 'utah'} else prepare_archive(pd.read_csv('data/metrocast/source/time-series.csv'))
    metadata = None if archive is None else pd.read_csv('data/metrocast/locations.csv').set_index('location')
    tasks = json.loads(Path('data/metrocast/source/tasks.json').read_text())
    target = 'Flu hosp admits' if kind == 'california' else 'Flu ED visits pct'
    task = next(t for t in tasks['rounds'][-1]['model_tasks'] if target in (t['task_ids']['target'].get('optional') or []))
    eligible = set(task['task_ids']['location']['optional'])
    torch.set_num_threads(1)
    for name, members in groups.items():
        assert {r['seed'] for r in members} == {42,43,44,45,46} and len(members) == 5
        destination = Path('output/metrocast/current-season')/args.experiment/name
        destination.mkdir(parents=True, exist_ok=True)
        samples, provenance = [], []
        expected_dates = expected_locations = None
        for record in sorted(members, key=lambda r: r['seed']):
            run = folder/record['attempt']
            manifest = json.loads((run/'manifest.json').read_text())
            assert manifest['folds'] == ['2026-2027']
            problem = Problem.load(manifest['problem'])
            if kind == 'utah':
                assert Path(problem.panel) == Path('data/metrocast-utah-proposed/panel.npz')
            scenario = Scenario.from_string(record['scenario'])
            panel = load(problem.panel)
            episode = inference_episode(panel, problem, scenario)
            if archive is not None:
                episode = replay_episode(episode, archive, metadata)
            locations = list(episode['locations'])
            dates = list(episode['target_dates'])
            if expected_dates is not None:
                assert dates == expected_dates and locations == expected_locations
            expected_dates, expected_locations = dates, locations
            checkpoint = run/'eval_2026-2027/model.pt'
            model = load_model(torch.load(checkpoint, map_location='cpu', weights_only=False))
            torch.manual_seed(record['seed']+1000)
            cache = destination/f"s{record['seed']}"
            cache.mkdir(exist_ok=True)
            evaluate(model, [episode], 128, 'cpu', cache, keep_samples=True)
            del model
            with np.load(cache/'forecasts.npz') as f:
                assert not f['mask'].any()
                draws = f['samples'][0, :, :, 0, :]
                # Exactly twenty whole trajectories from each seed: uniform five-seed mixture.
                ids = np.random.default_rng(record['seed']+2000).choice(len(draws), 20, replace=False)
                samples.append(draws[ids])
            provenance.append(dict(seed=record['seed'], checkpoint=str(checkpoint),
                                   checkpoint_sha256=sha256(checkpoint), panel_sha256=sha256(problem.panel),
                                   scenario=record['scenario'], training_fold='2026-2027 excluded',
                                   observed_history_cells=int(episode['available'].sum())))
        draws = np.concatenate(samples)
        # NYC remains excluded until its historical ILI/current influenza labeling is reconciled.
        included = [i for i, loc in enumerate(expected_locations) if loc in eligible and loc != 'nyc']
        locations = [expected_locations[i] for i in included]
        draws = draws[:, :, included]
        write_samples(draws, locations, REFERENCE, destination/'trajectories.parquet', target=target)
        if draws.shape[1] > 4:
            write_samples(draws[:, :4], locations, REFERENCE, destination/'four-week-samples.parquet', target=target)
        record = dict(
            reference_date=REFERENCE, target=target, horizons=len(expected_dates), target_dates=expected_dates,
            locations=locations, missing_eligible_locations=sorted(eligible-set(locations)),
            mixture='100 intact trajectories; exactly20 per seed; common sample IDs across weeks and locations',
            inputs='Frozen revised published California admission sums, retrieved before issuance deadline' if kind == 'california'
            else 'Hub archive dates strictly before Wednesday2026-10-21; no revised fill; missing latest context week remains missing',
            labels='Published partial admission sums over nonmissing age groups' if kind == 'california' else 'Future local flu ED proportions',
            training='2024-07-06 through 2026-07-25' if kind == 'california' else '2022-23 through 2025-26; no2026-27 training labels',
            selection='Development-only frozen selection; reserved-season confirmation scores not consulted',
            exclusions='NYC ILI/influenza inconsistency unresolved; Utah missing jurisdiction histories not imputed',
            published=False, checkpoints=provenance,
            tasks_sha256=sha256('data/metrocast/source/tasks.json'))
        if archive is not None:
            record['archive_sha256'] = sha256('data/metrocast/source/time-series.csv')
        if kind == 'utah':
            record.update(
                inputs='Frozen proposed weekly Utah PR587 source, retrieved before deadline; revised history only, no archived availability claim',
                exclusions='Separate provisional Utah artifact; statewide overlaps districts and the main-panel Utah series. Do not concatenate files without resolving overlap.',
                provisional_source=json.loads(Path('data/metrocast-utah-proposed/manifest.json').read_text()),
                provisional_manifest_sha256=sha256('data/metrocast-utah-proposed/manifest.json'),
                submission_ready=False)
        (destination/'export-manifest.json').write_text(json.dumps(record, indent=2)+'\n')
        print(destination, flush=True)


if __name__ == '__main__':
    main()
