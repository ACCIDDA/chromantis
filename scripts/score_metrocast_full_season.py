"""Development-only long-horizon WIS and joint-path energy, using the common scorer."""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
import torch

from chromantis.dataset.build import load
from chromantis.dataset.cv import score_episodes
from chromantis.evaluation.standard import quantile_scores
from chromantis.experiment.planner import collect
from chromantis.experiment.training import evaluate, path_scores
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from metrocast_seed_mixture import score_path_mixtures, peak_diagnostics

REFERENCES = {'2024-10-26', '2024-11-02', '2024-11-09', '2024-11-16'}
END = '2025-06-14'


def reference(context):
    return (date.fromisoformat(str(context)) + timedelta(days=7)).isoformat()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-e', '--experiment', required=True)
    p.add_argument('--paths', action='store_true', help='Retain and score 128 intact draws at four early-season origins')
    p.add_argument('--confirmation', action='store_true', help='Score the frozen 2025-26 study, never a development candidate')
    p.add_argument('--wait', action='store_true', help='Wait up to one hour for all planned fits')
    args = p.parse_args()
    season = '2025-2026' if args.confirmation else '2024-2025'
    references = {'2025-10-25', '2025-11-01', '2025-11-08', '2025-11-15'} if args.confirmation else REFERENCES
    end = '2026-06-13' if args.confirmation else END
    training_seasons = '2022-2023;2023-2024;2024-2025' if args.confirmation else '2022-2023;2023-2024'
    if args.confirmation:
        root = Path('experiments/metrocast-20261019')
        tree = json.loads((root/'tree.json').read_text())
        key = 'utah_confirmation' if args.experiment.startswith('metrocast-utah-confirm-') else 'full_season_confirmation'
        assert tree.get(key) == args.experiment, 'Only the registered frozen confirmation study may be scored'
        file = 'utah-frozen-selection.json' if key == 'utah_confirmation' else 'full-season-frozen-selection.json'
        frozen = json.loads((root/file).read_text())
    torch.set_num_threads(1)
    folder = Path('data/experiments') / args.experiment
    if args.wait:
        deadline = time.monotonic() + 3600
        while True:
            records = collect(folder)
            if records and all(r['status'] == 'complete' for r in records):
                break
            if any(r['status'] == 'failed' for r in records) or time.monotonic() >= deadline:
                raise RuntimeError('Full-season fits failed or wait expired')
            time.sleep(30)
    rows = []
    mixture_entries = []
    for record in collect(folder):
        if record['status'] != 'complete':
            continue
        run = folder / record['attempt']
        manifest = json.loads((run / 'manifest.json').read_text())
        assert manifest['folds'] == [season], 'Development and confirmation must remain separate'
        if args.confirmation:
            assert record['scenario'] in frozen['candidates'].values()
        problem = Problem.load(manifest['problem'])
        if args.confirmation and key == 'utah_confirmation':
            assert Path(problem.panel) == Path('data/metrocast-utah-proposed/panel.npz')
        assert problem.horizons == tuple(range(1, 35)), 'Expected 34 future weekly outputs'
        scenario = Scenario.from_string(record['scenario'])
        fold = run / f'eval_{season}'
        with np.load(fold / 'forecasts.npz') as f:
            refs = np.array([reference(x) for x in f['context_end']])
            keep = np.isin(refs, sorted(references))
            assert keep.sum() == 4
            # Separate boolean selection from channel indexing to retain [quantile, origin, week, location].
            q = f['quantiles'][:, keep][:, :, :, 0, :]
            y = f['truth'][keep, :, 0, :]
            mask = f['mask'][keep, :, 0, :].astype(bool)
            target_dates = f['target_dates'][keep].astype(str)
            mask &= (target_dates <= end)[..., None]
            levels = f['quantile_levels']
            assert q.shape == (len(levels), 4, 34, y.shape[-1]) and np.isfinite(q).all()
            assert (q >= 0).all() and (q <= 1).all()
            assert np.all(np.diff(q, axis=0) >= -1e-8)
            wis = quantile_scores(q.reshape(len(levels), -1).T, y.reshape(-1), levels).wis.to_numpy().reshape(y.shape)
            locations = list(f['locations'])
        base = dict(name=record['name'], scenario=record['scenario'], seed=record['seed'],
                    training_seasons=training_seasons, evaluation_season=season,
                    evaluation_inputs='latest revised histories', labels='future local flu ED proportions',
                    reference_dates=';'.join(sorted(references)), final_target_date=end,
                    ensemble_comparison=False)
        for label, start, stop in [('0-3', 0, 4), ('4-12', 4, 13), ('13-25', 13, 26),
                                   ('26-33', 26, 34), ('0-33', 0, 34)]:
            visible = mask[:, start:stop]
            count = visible.sum((0, 1))
            per_location = np.where(visible, wis[:, start:stop], 0).sum((0, 1)) / np.maximum(count, 1)
            rows.append(dict(base, metric='WIS percentage points', horizons=label,
                             value=float(per_location[count > 0].mean() * 100),
                             cells=int(count.sum()), locations=int((count > 0).sum())))
        if args.paths:
            destination = fold / 'early-season-joint-paths'
            cache = destination / 'forecasts.npz'
            if not cache.exists():
                panel = load(problem.panel)
                eps = [e for e in score_episodes(panel, problem, scenario, season)
                       if reference(e['context_dates'][-1]) in references]
                assert len(eps) == 4
                model = load_model(torch.load(fold / 'model.pt', map_location='cpu', weights_only=False))
                torch.manual_seed(record['seed'])
                destination.mkdir(exist_ok=True)
                evaluate(model, eps, 128, 'cpu', destination, keep_samples=True)
                del model
            mixture_entries.append((record, cache))
            with np.load(cache) as f:
                assert [reference(x) for x in f['context_end']] == list(refs[keep])
                samples = f['samples'][:, :, :, 0, :].transpose(1, 0, 2, 3).copy()
                assert samples.shape == (128, 4, 34, len(locations))
                assert np.isfinite(samples).all() and (samples >= 0).all() and (samples <= 1).all()
                assert np.allclose(f['truth'][:, :, 0, :], y)
            energy, _ = path_scores(torch.from_numpy(samples), torch.from_numpy(y),
                                    torch.from_numpy(mask), log_counts=False)
            present = mask.any(axis=1)
            count = present.sum(0)
            per_location = (energy.numpy() * present).sum(0) / np.maximum(count, 1)
            rows.append(dict(base, metric='Path energy percentage points', horizons='0-33',
                             value=float(per_location[count > 0].mean() * 100),
                             cells=int(present.sum()), locations=int((count > 0).sum())))
            rows.extend(dict(base, **row) for row in peak_diagnostics(
                samples.transpose(1, 0, 2, 3), y, mask, target_dates, end))
        print(record['name'], record['seed'], 'scored', flush=True)
    output = folder / ('confirmation-long-horizon.csv' if args.confirmation else 'early-season-long-horizon.csv')
    pd.DataFrame(rows).to_csv(output, index=False)
    if rows:
        print(pd.DataFrame(rows).groupby(['name', 'metric', 'horizons']).value.agg(['mean', 'std', 'count']).to_string())
    if args.paths:
        score_path_mixtures(mixture_entries,range(42,47 if args.confirmation else 46),folder,training_seasons,season,end)
    print(output)


if __name__ == '__main__':
    main()
