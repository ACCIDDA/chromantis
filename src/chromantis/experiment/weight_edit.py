"""Direct checkpoint edits without gradients or fitting; planner weight-edit.

Studies list manually specified tensor operations and their hypotheses. Scores on
the inspected seasons are exploratory retrospective results, not a fresh test.
"""
import argparse
import copy
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from chromantis.dataset.build import load
from chromantis.dataset import cv
from chromantis.evaluation.standard import raw_wis
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from .fit import ForecastSlice, forecast_labels
from .provenance import save, sha256
from .training import evaluate


def edit(saved, factor):
    """Multiply only the median row of each 23-quantile final readout.

    The decoder constructs intervals as median +/- positive cumulative gaps.
    Leaving its other rows intact preserves those gaps in decoder space; the
    inverse count/proportion transforms can still change their natural widths.
    """
    changed = copy.deepcopy(saved)
    if isinstance(factor, dict):
        return edit_components(changed, factor)
    components = changed.get('components', [changed])
    keys = []
    for i, component in enumerate(components):
        if component['config']['decoder'] != 'quantile':
            raise ValueError('This edit requires the 23-quantile decoder')
        state = component['state_dict']
        for key, tensor in state.items():
            if ('output_heads.' in key and key.endswith(('output.2.weight', 'output.2.bias'))):
                if tensor.shape[0] != 23:
                    raise ValueError(f'Unexpected readout shape: {key}')
                tensor[11].mul_(factor)
                keys.append(f'component {i}: {key}[11]')
    if not keys:
        raise ValueError('No quantile median readout found')
    changed['metadata'] = dict(changed.get('metadata', {}),
                               weight_edit=dict(median_factor=factor, parameters=keys, refit=False))
    return changed


def edit_components(changed, operations):
    """Named, literal tensor edits for the known 12-week, two-target flu MLP."""
    allowed = {'median_scale', 'gap_bias', 'outer_gap_bias', 'lower_gap_bias', 'upper_gap_bias',
               'geographic_scale', 'calendar_scale', 'slope_scale', 'acceleration_scale',
               'horizon_scale', 'horizon_shift_weeks', 'focal_scale', 'tail_direction_removal', 'tail_neurons',
               'level_circuit', 'level_reference', 'source_scale', 'context_scale'}
    if set(operations) - allowed:
        raise ValueError(f'Unknown tensor operation: {set(operations) - allowed}')
    changes = []
    for i, component in enumerate(changed.get('components', [changed])):
        config, state = component['config'], component['state_dict']
        if config['decoder'] != 'quantile':
            raise ValueError('Requires a direct 23-quantile decoder')
        before = {key: value.clone() for key, value in state.items()}
        for key, tensor in state.items():
            if 'output_heads.' in key and key.endswith(('output.2.weight', 'output.2.bias')):
                tensor[11] *= operations.get('median_scale', 1.)
                if key.endswith('bias'):
                    tensor[:11] += operations.get('gap_bias', 0.) + operations.get('lower_gap_bias', 0.)
                    tensor[12:] += operations.get('gap_bias', 0.) + operations.get('upper_gap_bias', 0.)
                    # Leave the 50% interval gaps (rows 6:11 and 12:17) intact.
                    tensor[:6] += operations.get('outer_gap_bias', 0.)
                    tensor[17:] += operations.get('outer_gap_bias', 0.)
                if key.endswith('weight'):
                    outer = list(range(6)) + list(range(17, 23))
                    if 'tail_direction_removal' in operations:
                        # A common nonnegative activation direction whose learned
                        # projections narrow the outer gaps. Remove a fraction of
                        # that projection; retain the median and inner-gap rows.
                        direction = (-tensor[outer].mean(0)).clamp_min(0)
                        direction /= direction.norm().clamp_min(1e-12)
                        projection = (tensor[outer] @ direction).clamp_max(0)
                        tensor[outer] -= operations['tail_direction_removal'] * projection[:, None] * direction[None]
                    if 'tail_neurons' in operations:
                        # Disconnect only the strongest common tail-narrowing
                        # neurons, selected from weights, not evaluation labels.
                        indices = tensor[outer].mean(0).argsort()[:int(operations['tail_neurons'])]
                        for row in outer:
                            tensor[row, indices] = 0
        if any(k in operations for k in ('calendar_scale', 'slope_scale', 'acceleration_scale')):
            if (config['lookback'] != 12 or len(config['input_names']) != 2 or config['covariate_names']
                    or config['signal_features'] != 'none' or not config['annual_calendar']
                    or not config['geography'] or not config['dynamics'] or state['context.0.weight'].shape[1] != 63):
                raise ValueError('Feature-column edit does not match this checkpoint layout')
            state['context.0.weight'][:, 48:51] *= operations.get('calendar_scale', 1.)
            state['context.0.weight'][:, [53, 58]] *= operations.get('slope_scale', 1.)
            state['context.0.weight'][:, [54, 59]] *= operations.get('acceleration_scale', 1.)
        if 'geographic_scale' in operations:
            state['geographic_message.project.weight'] *= operations['geographic_scale']
        if 'horizon_scale' in operations:
            state['horizon.weight'] *= operations['horizon_scale']
        if 'source_scale' in operations:
            state['source.weight'] *= operations['source_scale']
        if 'context_scale' in operations:
            state['context.2.weight'] *= operations['context_scale']
            state['context.2.bias'] *= operations['context_scale']
        if 'horizon_shift_weeks' in operations:
            # The network embeds h/4 with this affine layer. This bias edit is
            # exactly an offset to its learned forecast-time coordinate, with
            # all input dates, prediction labels and reported horizons intact.
            state['horizon.bias'] += state['horizon.weight'][:, 0] * (operations['horizon_shift_weeks'] / 4)
        if 'focal_scale' in operations:
            state['focal.2.weight'] *= operations['focal_scale']
            state['focal.2.bias'] *= operations['focal_scale']
        if 'level_circuit' in operations:
            program_level_circuit(state, config, operations['level_circuit'], operations.get('level_reference', .7))
        for key, value in state.items():
            if not torch.isfinite(value).all():
                raise ValueError(f'Nonfinite edited weights: {key}')
            count = int((value != before[key]).sum())
            if count:
                changes.append(dict(component=i, tensor=key, changed_values=count))
    changed['metadata'] = dict(changed.get('metadata', {}), weight_edit=dict(
        operations=operations, changes=changes, refit=False, gradients=False))
    return changed


def program_level_circuit(state, config, strength, reference):
    """Write a signed current-level path into two units of each existing layer.

    SiLU(x)-SiLU(-x)=x. A paired representation survives LayerNorm as a
    difference, cancelling its mean. The final median gains strength*(x-b)/sd,
    with x the latest normalized target value and b=reference for counts, 0 for
    centered logit ED. No gradient, labels, new layers, or additional parameters.
    A zero-strength candidate measures the damage from repurposing these units.
    """
    if (config['encoder'] != 'mlp' or config['decoder'] != 'quantile' or config['head_sharing'] != 'shared'
            or config['lookback'] != 12 or config['decoder_blocks'] or config['ed_transform'] != 'logit'):
        raise ValueError('Level circuit requires the known flu quantile architecture')
    head = 'output_heads.0.output.'
    # Choose weak outgoing paths using only the original checkpoint weights.
    focal_units = (state['focal.2.weight'].norm(dim=0) * state['focal.0.weight'].norm(dim=1)).argsort()[:2]
    coordinates = state[head + '0.weight'].norm(dim=0).argsort()[:2]
    readout_units = (state[head + '2.weight'].norm(dim=0) * state[head + '0.weight'].norm(dim=1)).argsort()[:2]
    a, b = map(int, focal_units)
    p, q = map(int, coordinates)
    u, v = map(int, readout_units)
    state['focal.0.weight'][[a, b]] = 0
    state['focal.0.bias'][[a, b]] = 0
    state['focal.0.weight'][a, 22] = 1
    state['focal.0.weight'][b, 22] = -1
    state['focal.2.weight'][:, [a, b]] = 0
    state['focal.2.weight'][[p, q]] = 0
    state['focal.2.bias'][[p, q]] = 0
    state['focal.2.weight'][p, a], state['focal.2.weight'][p, b] = 1, -1
    state['focal.2.weight'][q, a], state['focal.2.weight'][q, b] = -1, 1
    state['context.2.weight'][[p, q]] = 0
    state['context.2.bias'][[p, q]] = 0
    state['geographic_message.project.weight'][[p, q]] = 0
    state['horizon.weight'][[p, q]] = 0
    state['horizon.bias'][[p, q]] = 0
    state['source.weight'][:, [p, q]] = 0
    for i, unit in enumerate(config['target_units']):
        if unit == 'count':
            state['source.weight'][i, p] = -reference
            state['source.weight'][i, q] = reference
    state['norm.weight'][[p, q]] = 1
    state['norm.bias'][[p, q]] = 0
    state[head + '0.weight'][[u, v]] = 0
    state[head + '0.bias'][[u, v]] = 0
    state[head + '0.weight'][u, p], state[head + '0.weight'][u, q] = .5, -.5
    state[head + '0.weight'][v, p], state[head + '0.weight'][v, q] = -.5, .5
    state[head + '2.weight'][:, [u, v]] = 0
    state[head + '2.weight'][11, u], state[head + '2.weight'][11, v] = strength, -strength


def candidates(spec):
    return spec.get('candidates', {'original': {}, 'median_times_0.9': {'median_scale': spec['factor']}})


def plan(folder, args):
    problem = Problem.load(args.problem)
    panel_hash = sha256(args.dataset)
    checkpoints = []
    for source in sorted(Path(args.checkpoints).rglob('model.pt')):
        saved = torch.load(source, map_location='cpu', weights_only=False)
        meta = saved['metadata']
        season, trained = meta['held_out_season'], meta['fold']['training_seasons']
        if season not in problem.folds or season in trained:
            raise ValueError(f'Invalid held-out season: {source}')
        if meta['dataset_sha256'] != panel_hash:
            raise ValueError(f'Panel differs from the checkpoint training panel: {source}')
        study = json.loads(Path(args.study).read_text()) if args.study else None
        for ops in study['candidates'].values() if study else [args.factor]:
            edit(saved, ops)  # validate before recording the plan
        checkpoints.append(dict(source=str(source.resolve()), sha256=sha256(source),
                                season=season, seed=meta['seed'], training_seasons=trained,
                                scenario=meta['scenario']))
    if not checkpoints or len({(c['season'], c['seed']) for c in checkpoints}) != len(checkpoints):
        raise ValueError('Expected one checkpoint per season/seed')
    spec = dict(checkpoints=checkpoints, factor=args.factor, dataset=str(Path(args.dataset).resolve()),
                dataset_sha256=panel_hash, problem=str(problem.path.resolve()), problem_sha256=problem.hash,
                evaluation_inputs='reported, with the standard finalized fallback; no correction trees',
                selection='One fixed edit; all seasons are evaluation, no tuning on their scores',
                primary='Equal-season, equal-seed mean state/DC log(1+admissions) WIS; lower is better')
    if args.study:
        study = json.loads(Path(args.study).read_text())
        if study['candidates'].get('original') != {}:
            raise ValueError('Study must include original: {}')
        if any(not name.replace('_', '').replace('.', '').isalnum() for name in study['candidates']):
            raise ValueError('Candidate names must be safe directory names')
        spec.update(candidates=study['candidates'], rationale=study.get('rationale', {}),
                    selection='Manually specified edits screened on already inspected seasons; exploratory, not fresh validation')
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'experiment.json'
    if path.exists() and json.loads(path.read_text()) != spec:
        raise ValueError('Plan changed; use a new experiment name')
    save(path, spec)
    print(f'Planned {len(checkpoints)} paired checkpoint comparisons in {folder}')


def run(folder, spec):
    if sha256(spec['dataset']) != spec['dataset_sha256']:
        raise ValueError('Panel changed since plan')
    problem = Problem.load(spec['problem'])
    if problem.hash != spec['problem_sha256']:
        raise ValueError('Problem changed since plan')
    problem = replace(problem, evaluation_inputs='reported', evaluation_draws=1,
                      evaluation_covariate_errors=False)
    panel = load(spec['dataset'])
    torch.set_num_threads(2)
    for item in spec['checkpoints']:
        source = Path(item['source'])
        if sha256(source) != item['sha256']:
            raise ValueError(f'Checkpoint changed: {source}')
        saved = torch.load(source, map_location='cpu', weights_only=False)
        scenario = Scenario.from_string(item['scenario'])
        eps = forecast_labels(problem, scenario, cv.score_episodes(panel, problem, scenario, item['season']))
        for treatment, operations in candidates(spec).items():
            root = folder / treatment / f"s{item['seed']}"
            out = root / f"eval_{item['season']}"
            if (out / 'complete.json').exists():
                continue
            out.mkdir(parents=True, exist_ok=True)
            candidate = saved if treatment == 'original' else edit(saved, operations)
            model = load_model(candidate)
            if not model.config.get('direct_quantiles'):
                raise ValueError('Expected direct quantiles')
            future = [i for i, h in enumerate(model.config['horizons']) if h > 0]
            model = ForecastSlice(model, future)
            # Check the algebra, including that only the intended rows changed.
            if treatment != 'original':
                torch.save(candidate, out / 'model.pt')
            torch.manual_seed(item['seed'] + 1000)
            evaluate(model, eps, 512, 'cpu', out)
            save(out / 'complete.json', dict(item, treatment=treatment, refit=False))
            save(root / 'manifest.json', dict(problem=spec['problem'], scenario=item['scenario'],
                 folds=sorted(p.name[5:] for p in root.glob('eval_*') if (p / 'complete.json').exists())))
            print(f"Completed {treatment}, seed {item['seed']}, excluded season {item['season']}", flush=True)


def rank(folder, spec):
    if 'candidates' in spec:
        return rank_candidates(folder, spec)
    rows = []
    for treatment in ('original', 'median_times_0.9'):
        for seed in sorted({c['seed'] for c in spec['checkpoints']}):
            root = folder / treatment / f's{seed}'
            expected = {c['season'] for c in spec['checkpoints'] if c['seed'] == seed}
            if not all((root / f'eval_{s}' / 'complete.json').exists() for s in expected):
                raise ValueError('Run all planned comparisons before ranking')
            rows.append(raw_wis(root, None).assign(treatment=treatment, seed=seed))
    scores = pd.concat(rows, ignore_index=True)
    keys = ['seed', 'season', 'target', 'scale', 'geography']
    pair = scores.pivot(index=keys, columns='treatment', values='mean_wis').reset_index()
    support = scores.pivot(index=keys, columns='treatment', values='support_sha256')
    if not (support.original == support['median_times_0.9']).all():
        raise ValueError('Paired scores do not have identical targets and truth')
    pair['percent_change'] = 100 * (pair['median_times_0.9'] / pair.original - 1)
    scores.to_csv(folder / 'scores.csv', index=False)
    pair.to_csv(folder / 'paired-scores.csv', index=False)
    summary = pair.groupby(['season', 'target', 'scale', 'geography'])[['original', 'median_times_0.9']].mean().reset_index()
    summary['percent_change'] = 100 * (summary['median_times_0.9'] / summary.original - 1)
    print(summary.to_string(index=False))
    summary['training_seasons'] = summary.season.map({c['season']: ', '.join(c['training_seasons']) for c in spec['checkpoints']})
    summary['model'] = 'Width-256 direct-quantile flu MLP with neighboring-location exchange; mean of individual seed scores'
    summary['training_inputs'] = 'Admission and ED histories with prescribed 2025-26 reporting errors multiplied by 1.5; no Kinsa'
    summary['training_labels'] = 'Latest panel admissions and ED; also reconstruct the latest four history weeks'
    summary['evaluation_inputs'] = spec['evaluation_inputs']
    summary['edit'] = 'Median readout weights and bias times 0.9; interval-gap rows unchanged; no retraining'
    summary.to_csv(folder / 'summary.csv', index=False)
    # User reviews the graph; no image inspection is needed.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    primary = summary[(summary.target == 'wk inc flu hosp') & (summary.scale == 'log') & (summary.geography == 'states_dc')]
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(primary))
    ax.bar(x - .18, primary.original, .36, label='Original saved weights')
    ax.bar(x + .18, primary['median_times_0.9'], .36, label='Median readout weights and bias × 0.9')
    labels = []
    for season in primary.season:
        trained = next(c['training_seasons'] for c in spec['checkpoints'] if c['season'] == season)
        labels.append('Evaluate ' + season + '\nTrained on ' + ', '.join(trained))
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylabel('State/DC mean log-admission WIS (lower is better)')
    seeds = len({c['seed'] for c in spec['checkpoints']})
    ax.set_title(f'Width-256 quantile flu model; mean of {seeds} seed scores; no retraining')
    ax.legend()
    fig.text(.02, .01, 'Training: artificial reporting errors ×1.5; latest admissions/ED + recent-week reconstruction labels.\n'
             'Evaluation: archived reports with finalized fallback, no correction trees; October–May, horizons 0–3.\n'
             '2025–26 reporting-error patterns were prescribed during training; this is retrospective, not a prospective test.', fontsize=8)
    fig.tight_layout(rect=(0, .13, 1, 1))
    fig.savefig(folder / 'comparison.png', dpi=160)
    plt.close(fig)


def rank_candidates(folder, spec):
    rows = []
    for treatment in candidates(spec):
        for seed in sorted({c['seed'] for c in spec['checkpoints']}):
            root = folder / treatment / f's{seed}'
            expected = {c['season'] for c in spec['checkpoints'] if c['seed'] == seed}
            if not all((root / f'eval_{s}' / 'complete.json').exists() for s in expected):
                raise ValueError(f'Incomplete candidate: {treatment}, seed {seed}')
            rows.append(raw_wis(root, None).assign(treatment=treatment, seed=seed))
    scores = pd.concat(rows, ignore_index=True)
    keys = ['seed', 'season', 'target', 'scale', 'geography']
    reference = scores[scores.treatment == 'original'][keys + ['mean_wis', 'support_sha256']].rename(
        columns={'mean_wis': 'original_wis', 'support_sha256': 'original_support'})
    paired = scores.merge(reference, on=keys, validate='many_to_one')
    if not paired.support_sha256.eq(paired.original_support).all():
        raise ValueError('Different evaluation tasks in paired comparison')
    paired['percent_change'] = 100 * (paired.mean_wis / paired.original_wis - 1)
    paired.to_csv(folder / 'paired-scores.csv', index=False)
    summary = paired.groupby(['treatment', 'season', 'target', 'scale', 'geography'])[
        ['mean_wis', 'original_wis', 'mean_underprediction', 'mean_overprediction', 'covered_50', 'covered_95']].mean().reset_index()
    summary['percent_change'] = 100 * (summary.mean_wis / summary.original_wis - 1)
    summary['training_seasons'] = summary.season.map({c['season']: ', '.join(c['training_seasons']) for c in spec['checkpoints']})
    summary['operations'] = summary.treatment.map({k: json.dumps(v, sort_keys=True) for k, v in candidates(spec).items()})
    summary['model'] = 'Width-256 direct-quantile flu MLP, neighboring-location exchange; mean individual seed scores'
    summary['training_inputs'] = 'Artificial reporting errors x1.5 from prescribed 2025-26 patterns, admissions and ED; no Kinsa'
    summary['training_labels'] = 'Latest future admissions/ED and latest four history weeks for reconstruction'
    summary['evaluation_inputs'] = spec['evaluation_inputs']
    summary['refit'] = False
    summary.to_csv(folder / 'summary.csv', index=False)
    states = summary[summary.geography == 'states_dc']
    leaderboard = []
    for treatment in candidates(spec):
        part = states[states.treatment == treatment]
        row = dict(treatment=treatment)
        for label, target, scale in [('log_admissions', 'wk inc flu hosp', 'log'),
                                     ('admissions', 'wk inc flu hosp', 'natural'),
                                     ('ed', 'wk inc flu prop ed visits', 'natural')]:
            sub = part[(part.target == target) & (part.scale == scale)]
            row[f'{label}_percent_change'] = 100 * (sub.mean_wis.mean() / sub.original_wis.mean() - 1)
            if label == 'log_admissions':
                row['worst_season_percent_change'] = sub.percent_change.max()
                row['seasons_improved'] = int((sub.percent_change < 0).sum())
                for _, r in sub.iterrows():
                    row[r.season] = r.percent_change
        leaderboard.append(row)
    leaders = pd.DataFrame(leaderboard).sort_values('log_admissions_percent_change')
    leaders.to_csv(folder / 'ranking.csv', index=False)
    print(leaders.to_string(index=False), flush=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    seasons = sorted({c['season'] for c in spec['checkpoints']})
    names = leaders[leaders.treatment != 'original'].treatment.head(6).tolist()
    fig, ax = plt.subplots(figsize=(12, 6))
    width = .8 / len(seasons)
    for i, season in enumerate(seasons):
        ax.barh(np.arange(len(names)) + (i - 1) * width,
                leaders.set_index('treatment').loc[names, season], height=width, label='Evaluate ' + season)
    ax.set_yticks(range(len(names)), [n + '\n' + json.dumps(candidates(spec)[n]) for n in names], fontsize=8)
    ax.axvline(0, color='black', linewidth=.7)
    ax.set_xlabel('Change in state/DC log-admission WIS (%); negative is better')
    ax.set_title('Direct weight edits; no retraining; mean of individual seed scores')
    ax.invert_yaxis()
    ax.legend(fontsize=8)
    training = '\n'.join('Evaluate ' + s + ': trained on ' + ', '.join(next(c['training_seasons'] for c in spec['checkpoints'] if c['season'] == s)) for s in seasons)
    fig.text(.02, .01, training + '\nWidth-256 quantile flu model. Artificial reporting errors x1.5; latest-value + reconstruction labels.\n'
             'Evaluation: archived reports with finalized fallback, no correction trees; October–May, horizons 0–3.\n'
             'Prescribed 2025–26 reporting patterns; exploratory selection on inspected seasons.', fontsize=7)
    fig.tight_layout(rect=(0, .24, 1, 1))
    fig.savefig(folder / 'comparison.png', dpi=160)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'run', 'status', 'rank', 'diagnose'])
    parser.add_argument('-e', '--experiment', required=True)
    parser.add_argument('--checkpoints', default='data/seasonal/checkpoints/bes')
    parser.add_argument('--problem', default='problems/us-flu-short-term-prescribed.json')
    parser.add_argument('--dataset', default='data/processed/panel.npz')
    parser.add_argument('--factor', type=float, choices=[.9], default=.9)
    parser.add_argument('--study', help='JSON with manually specified candidate tensor operations')
    args = parser.parse_args(argv)
    folder = Path('data/experiments') / args.experiment
    if args.action == 'plan':
        return plan(folder, args)
    spec = json.loads((folder / 'experiment.json').read_text())
    if args.action == 'run':
        return run(folder, spec)
    if args.action == 'rank':
        return rank(folder, spec)
    if args.action == 'diagnose':
        return diagnose(folder, spec)
    finished = len(list(folder.glob('*/s*/eval_*/complete.json')))
    total = len(candidates(spec)) * len(spec['checkpoints'])
    print(f"{finished}/{total} evaluations complete")
    if finished != total:
        print(f'Resume: .venv/bin/python -m chromantis.experiment.planner weight-edit run -e {args.experiment}')


def diagnose(folder, spec):
    """Describe saved forecast errors; phases use only the evaluation input histories.

    Rising/falling means >20% change in count+1 over the last two input weeks.
    This is a descriptive threshold, not a learned decision rule or a new test set.
    """
    from datetime import date, timedelta
    from chromantis.data.geography import STATE_FIPS
    from chromantis.evaluation.hubs import export, QCOLS
    from chromantis.evaluation.standard import scored, scored_window

    problem = replace(Problem.load(spec['problem']), evaluation_inputs='reported', evaluation_draws=1,
                      evaluation_covariate_errors=False)
    if sha256(spec['dataset']) != spec['dataset_sha256']:
        raise ValueError('Panel changed since plan')
    panel = load(spec['dataset'])
    postal_to_fips = {v: k for k, v in STATE_FIPS.items()} | {'US': 'US'}
    phases = {}
    for season in sorted({c['season'] for c in spec['checkpoints']}):
        item = next(c for c in spec['checkpoints'] if c['season'] == season)
        scenario = Scenario.from_string(item['scenario'])
        eps = cv.score_episodes(panel, problem, scenario, season)
        rows = []
        for e in eps:
            channel = list(e['input_names']).index('nhsn_flu_admissions')
            recent, prior = e['values'][-1, channel], e['values'][-3, channel]
            valid = e['available'][-1, channel] & e['available'][-3, channel]
            growth = np.log1p(recent) - np.log1p(prior)
            phase = np.where(~valid, 'missing recent input',
                             np.where(growth > np.log(1.2), 'rising',
                                      np.where(growth < -np.log(1.2), 'falling', 'roughly flat')))
            reference = (date.fromisoformat(str(e['context_dates'][-1])) + timedelta(weeks=1)).isoformat()
            rows.extend(dict(reference_date=reference, location=postal_to_fips.get(str(loc), str(loc)), phase=str(ph))
                        for loc, ph in zip(e['locations'], phase))
        phases[season] = pd.DataFrame(rows)
    summaries = []
    for treatment in ('original', 'median_times_0.9'):
        for seed in sorted({c['seed'] for c in spec['checkpoints']}):
            root = folder / treatment / f's{seed}'
            _, window = scored_window(root)
            for (season, target), frame in export(root).items():
                if target != 'wk inc flu hosp':
                    continue
                frame = frame[frame.model_original_mask.astype(bool) & window(frame.reference_date)
                              & frame.location.ne('US') & frame.horizon.lt(4)].copy()
                frame = frame.merge(phases[season], on=['reference_date', 'location'], validate='many_to_one')
                metrics = scored(frame[QCOLS].to_numpy(), frame.model_original_truth.to_numpy(), 'log')
                for name in ('wis', 'underprediction', 'overprediction', 'covered_50', 'covered_95'):
                    frame[name] = metrics[name].to_numpy()
                for dimension in ('horizon', 'phase', 'location'):
                    group = frame.groupby(dimension)
                    table = group[['wis', 'underprediction', 'overprediction', 'covered_50', 'covered_95']].mean()
                    table['tasks'] = group.size()
                    summaries.append(table.reset_index().rename(columns={dimension: 'value'}).assign(
                        dimension=dimension, season=season, seed=seed, treatment=treatment))
    details = pd.concat(summaries, ignore_index=True)
    details.to_csv(folder / 'diagnostics-per-seed.csv', index=False)
    summary = details.groupby(['season', 'dimension', 'value', 'treatment'], sort=False)[
        ['wis', 'underprediction', 'overprediction', 'covered_50', 'covered_95', 'tasks']].mean().reset_index()
    summary['training_seasons'] = summary.season.map({c['season']: ', '.join(c['training_seasons']) for c in spec['checkpoints']})
    summary['definition'] = ('Width-256 quantile flu model; artificial training errors x1.5 from prescribed 2025-26 patterns; '
                             'latest admissions/ED and recent-history reconstruction labels; '
                             'evaluation on archived reports with finalized fallback, no correction trees; '
                             'state/DC log-admission WIS, lower better; October-May, horizons 0-3; '
                             'phase from >20% two-week change in input admissions+1; no retraining')
    summary.to_csv(folder / 'diagnostics.csv', index=False)
    print(summary[summary.dimension != 'location'].drop(columns=['definition', 'training_seasons']).to_string(index=False))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    season = sorted(phases)[-1]
    latest = summary[summary.season == season]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.8))
    names = ['falling', 'roughly flat', 'rising']
    for i, (treatment, label) in enumerate((('original', 'Original saved weights'),
                                           ('median_times_0.9', 'Median readout × 0.9'))):
        part = latest[latest.treatment == treatment]
        phase = part[part.dimension == 'phase'].set_index('value').reindex(names)
        axes[0].bar(np.arange(3) + (i - .5) * .36, phase.wis, .36, label=label)
        horizons = part[part.dimension == 'horizon'].sort_values('value')
        axes[1].plot(horizons.value.astype(int), 100 * horizons.covered_95, 'o-', label=label)
    axes[0].set_xticks(range(3), names)
    axes[0].set_ylabel('State/DC log-admission WIS; lower is better')
    axes[0].set_title('Error by recent input trend')
    axes[1].axhline(95, color='gray', linestyle='--', label='Nominal 95% coverage')
    axes[1].set_xticks(range(4))
    axes[1].set_xlabel('Hub horizon')
    axes[1].set_ylabel('Outcomes inside the 95% interval (%)')
    axes[1].set_title('Interval coverage by horizon')
    axes[1].legend(fontsize=8)
    trained = next(c['training_seasons'] for c in spec['checkpoints'] if c['season'] == season)
    fig.suptitle('Width-256 quantile flu model; mean individual seed scores\nTrain ' + ', '.join(trained) + '; evaluate ' + season)
    fig.text(.02, .02, 'Training: artificial admission/ED reporting errors ×1.5, prescribed from 2025–26; latest-value + reconstruction labels.\n'
             'Evaluation: archived reports with finalized fallback, no correction trees; October–May; no retraining.\n'
             'Rising/falling: >20% two-week change in input admissions+1. Descriptive analysis, not a new validation set.', fontsize=8)
    fig.tight_layout(rect=(0, .18, 1, .95))
    fig.savefig(folder / 'diagnostics.png', dpi=160)
    plt.close(fig)
