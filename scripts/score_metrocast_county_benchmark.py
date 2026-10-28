"""Match county forecasts to the actual MetroCast ensemble, using the common WIS math."""
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
from chromantis.experiment.training import evaluate
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from metrocast_seed_mixture import has_samples, score_mixtures

ROOT = Path('data/metrocast-county-2024')
KEY = ['reference_date', 'target_end_date', 'location', 'horizon']
LEVELS = np.array([.025, .05, .1, .25, .5, .75, .9, .95, .975])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-e', '--experiment', required=True)
    p.add_argument('--device', default='cpu')
    p.add_argument('--mixtures', action='store_true', help='Score equal-weight intact-draw seed mixtures with archived inputs')
    p.add_argument('--wait', action='store_true', help='Wait up to one hour for the planned fits')
    args = p.parse_args()
    torch.set_num_threads(1)
    folder = Path('data/experiments') / args.experiment
    if args.wait:
        deadline = time.monotonic() + 3600
        while True:
            records = collect(folder)
            if records and all(r['status'] == 'complete' for r in records):
                break
            if any(r['status'] == 'failed' for r in records) or time.monotonic() >= deadline:
                raise RuntimeError('Benchmark fits failed or did not finish within one hour')
            time.sleep(30)
    ensemble = pd.concat([pd.read_csv(f) for f in sorted((ROOT / 'source').glob('*-epiENGAGE-ensemble_mean.csv'))])
    ensemble = ensemble[ensemble.target.eq('Flu ED visits pct') & ensemble.horizon.isin(range(4)) &
                        ensemble.output_type.eq('quantile')]
    assert not ensemble.duplicated([*KEY, 'output_type_id']).any()
    ensemble = ensemble.pivot(index=KEY, columns='output_type_id', values='value').reindex(columns=LEVELS)
    assert np.isfinite(ensemble.to_numpy()).all()
    ensemble.columns = [f'ensemble_q{q:g}' for q in LEVELS]
    ensemble = ensemble.reset_index()
    archive = pd.read_csv(ROOT / 'source/time-series.csv')
    archive = archive[archive.target.eq('Flu ED visits pct')].sort_values('as_of')
    context_archive = None
    rows = []
    mixture_entries = []
    for record in collect(folder):
        if record['status'] != 'complete':
            continue
        run = folder / record['attempt']
        manifest = json.loads((run / 'manifest.json').read_text())
        problem = Problem.load(manifest['problem'])
        scenario = Scenario.from_string(record['scenario'])
        assert Path(problem.panel).resolve() in {
            (ROOT / 'panel.npz').resolve(), Path('data/metrocast-county-context/panel.npz').resolve()}
        assert not scenario.geography
        if scenario.covariate_set != 'none':
            assert problem.id == 'metrocast-county-context'
            from metrocast_county_context import archived_context
            if context_archive is None:
                with np.load('data/metrocast-county-context/context-vintages.npz') as f:
                    context_archive = {k: f[k] for k in f.files}
        for season in manifest['folds']:
            assert season == '2024-2025'  # Never use the reserved 2025-26 season here.
            fold = run / f'eval_{season}'
            archived = fold / 'metrocast-archived-inputs'
            if not (archived / 'forecasts.npz').exists() or (args.mixtures and not has_samples(archived / 'forecasts.npz')):
                panel = load(problem.panel)
                eps = score_episodes(panel, problem, scenario, season)
                replay = []
                for e in eps:
                    reference = date.fromisoformat(e['context_dates'][-1]) + timedelta(days=7)
                    cutoff = (reference - timedelta(days=3)).isoformat()
                    if reference.isoformat() not in set(ensemble.reference_date):
                        continue
                    released = archive[archive.as_of <= cutoff].drop_duplicates(['target_end_date', 'location'], keep='last')
                    wide = released.pivot(index='target_end_date', columns='location', values='observation')
                    x = wide.reindex(index=e['context_dates'], columns=e['locations']).to_numpy(np.float32)[:, None, :] / 100
                    if not np.isfinite(x).any():
                        continue
                    e = dict(e, values=np.nan_to_num(x), available=np.isfinite(x), known_final=np.isfinite(x))
                    if scenario.covariate_set != 'none':
                        cov, source_cutoff = archived_context(e, problem.covariate_names(scenario.covariate_set),
                                                             context_archive, cutoff)
                        e['covariates'] = cov
                        e['context_source_cutoff_utc'] = source_cutoff
                    replay.append(e)
                assert replay, 'No archived histories before ensemble deadlines'
                model = load_model(torch.load(fold / 'model.pt', map_location='cpu', weights_only=False)).to(args.device)
                torch.manual_seed(record['seed'])
                archived.mkdir(exist_ok=True)
                evaluate(model, replay, 512, args.device, archived, keep_samples=args.mixtures)
                if scenario.covariate_set != 'none':
                    (archived / 'context-cutoffs.json').write_text(json.dumps([
                        dict(reference_date=(date.fromisoformat(e['context_dates'][-1]) + timedelta(days=7)).isoformat(),
                             source_cutoff_utc=e['context_source_cutoff_utc'])
                        for e in replay], indent=2) + '\n')
                del model
            if args.mixtures:
                mixture_entries.append((record, archived/'forecasts.npz', 'archived'))
            for view, path in [('revised', fold), ('archived', archived)]:
                with np.load(path / 'forecasts.npz') as f:
                    qidx = [int(np.flatnonzero(np.isclose(f['quantile_levels'], q))[0]) for q in LEVELS]
                    q = f['quantiles'][qidx, :, :4, 0, :]
                    n, h, l = q.shape[1:]
                    ref = [(date.fromisoformat(str(v)) + timedelta(days=7)).isoformat() for v in f['context_end']]
                    pred = pd.DataFrame(dict(reference_date=np.repeat(ref, h*l),
                                             target_end_date=np.repeat(f['target_dates'][:, :4].reshape(-1), l),
                                             location=np.tile(f['locations'], n*h),
                                             horizon=np.tile(np.repeat(np.arange(h), l), n),
                                             observed=f['truth'][:, :4, 0, :].reshape(-1),
                                             available=f['mask'][:, :4, 0, :].reshape(-1)))
                    qcols = [f'q{x:g}' for x in LEVELS]
                    pred[qcols] = q.reshape(len(LEVELS), -1).T
                matched = ensemble.merge(pred[pred.available], on=KEY, validate='one_to_one')
                assert len(matched), 'No matching ensemble tasks'
                y = matched.observed.to_numpy()
                ours = quantile_scores(matched[qcols].to_numpy(), y, LEVELS).wis.to_numpy()
                theirs = quantile_scores(matched[[f'ensemble_q{x:g}' for x in LEVELS]].to_numpy()/100, y, LEVELS).wis.to_numpy()
                cells = matched[KEY].assign(model_wis=ours, ensemble_wis=theirs)
                loc = cells.groupby('location')[['model_wis', 'ensemble_wis']].sum()
                rows.append(dict(name=record['name'], scenario=record['scenario'], seed=record['seed'],
                                 evaluation_inputs=view, season=season, tasks=len(cells),
                                 locations=len(loc), ensemble_tasks=len(ensemble),
                                 first_reference=matched.reference_date.min(), last_reference=matched.reference_date.max(),
                                 model_wis_percentage_points=float(ours.mean()*100),
                                 ensemble_wis_percentage_points=float(theirs.mean()*100),
                                 location_mean_wis_ratio=float((loc.model_wis/loc.ensemble_wis).mean()),
                                 pooled_wis_ratio=float(ours.mean()/theirs.mean())))
                cells.to_parquet(path / 'metrocast-ensemble-cells.parquet', index=False)
    output = folder / 'metrocast-ensemble-comparison.csv'
    pd.DataFrame(rows).to_csv(output, index=False)
    if rows:
        d = pd.DataFrame(rows)
        print(d.groupby(['name', 'evaluation_inputs']).agg(
            model_wis=('model_wis_percentage_points', 'mean'),
            ensemble_wis=('ensemble_wis_percentage_points', 'mean'),
            relative_wis=('location_mean_wis_ratio', 'mean'),
            seed_sd=('location_mean_wis_ratio', 'std'), seeds=('seed', 'nunique'),
            tasks=('tasks', 'min')).to_string())
    if args.mixtures:
        score_mixtures(mixture_entries, ensemble, range(42,46), folder, '2022-2023;2023-2024', '2024-2025')
    print(output)


if __name__ == '__main__':
    main()
