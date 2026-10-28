"""Combine a release's operational forecasts and write the Hub quantile file, with its checks.

Recipes are combined with `evaluation.ensembles.combine` (equal weight per recipe, equal
weight per seed within a recipe, the release's rule) for the targets each recipe was
trained to predict. Checks against the local Hub clone: reference date in the current
round, quantile grid, units, ordering, horizon dates, no duplicate tasks. ED proportions
above the Hub's `max_prop_ed_visits` (0.25) are capped and each cap is recorded.
Writes `<reference>-ACCIDDA-<model_abbr>.csv` and a JSON record of the sources, hashes and
release; nothing is published.

When the Hub accepts Parquet (`hub-config/admin.json`), the same table is also written as
`<reference>-ACCIDDA-<model_abbr>.parquet` with the hubverse column types (dates, int32
horizon, string output_type_id, double value): the file to submit; the CSV stays the
working copy read by the plots and records.

`samples=True` adds `SAMPLES` sampled trajectories per location (`trajectories`), one
sample id per location shared by every horizon and target, as the RSV Hub accepts.

History: scripts/export_b6.py (2026-10-07), unchanged in what it computes.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

from chromantis.evaluation.ensembles import combine, trained_channels
from chromantis.evaluation.quantiles import LEVELS
from chromantis.experiment.provenance import sha256
from chromantis.problem import Problem

from .hubs import HUBS

SAMPLES = 200  # RSV Hub tasks.json: min = max samples per task


def trajectories(recipes, n, rng):
    """n trajectories [n, horizon, channel, location] with equal weight per recipe and per seed.

    Recipes {'quantiles' [quantile, horizon, channel, location] (mixture over its seeds),
    'samples' [seed, member, horizon, channel, location] or None}. A sampling recipe contributes
    whole draws, equally from each seed (one network draw = one trajectory over horizons and
    targets); at each location they are taken at evenly spaced ranks of the draws' summed
    per-horizon, per-target ranks, so a few draws per seed still span that seed's spread. A direct-quantile recipe has no joint draws: it gives stratified
    marginal values from its seed-mixture quantiles (levels (k + .5) / count, linear between the
    Hub levels, clipped to 0.01-0.99), ordered at each location by the ranks of trajectories
    drawn without replacement from the sampling recipes' draws (Schaake shuffle), so they
    inherit the sampling recipes' dependence across horizons and targets."""
    blocks, pending = [], []
    for recipe, k in zip(recipes, map(len, np.array_split(np.arange(n), len(recipes)))):
        if recipe['samples'] is not None:
            for seed, m in enumerate(map(len, np.array_split(np.arange(k), len(recipe['samples'])))):
                draws = recipe['samples'][seed]
                score = draws.argsort(0).argsort(0).sum((1, 2))
                pick = score.argsort(0)[((np.arange(m) + .5) / m * len(draws)).astype(int)]
                blocks.append(np.take_along_axis(draws, pick[:, None, None, :], 0))
        else:
            u = np.clip((np.arange(k) + .5) / k, LEVELS[0], LEVELS[-1])
            pending.append(np.apply_along_axis(lambda v: np.interp(u, LEVELS, v), 0, recipe['quantiles']))
    if not blocks:
        raise ValueError('Trajectories need at least one sampling recipe')
    template = np.concatenate(blocks)
    for values in pending:
        m = len(values)
        order = np.stack([rng.choice(len(template), m, replace=False) for _ in range(template.shape[-1])], -1)
        ranks = np.take_along_axis(template, order[:, None, None, :], 0).argsort(0).argsort(0)
        blocks.append(np.take_along_axis(np.sort(values, 0), ranks, 0))
    return np.concatenate(blocks)


def export(release, members, hub, out, samples=False):
    """`members` {recipe: [operational forecast folders]} from `forecast.forecast_release`."""
    if samples and release.get('recipe_targets'):
        raise ValueError('Target-routed releases support marginal quantiles, not joint sample trajectories')
    if not re.fullmatch(r'[A-Za-z0-9_+]{1,16}', release['model_abbr']):
        raise ValueError('Invalid model abbreviation')
    if release['rule'] not in ('vincent', 'mixture'):
        raise ValueError('Unknown ensemble rule')
    hub, out = Path(hub), Path(out)
    problem = Problem.load(release['problem'])
    recipes, sources, first = [], [], None
    panel_hashes, issues = set(), set()
    for name, folders in members.items():
        values, draws, scenarios, seeds = [], [], set(), []
        for folder in map(Path, folders):
            meta = json.loads((folder / 'operational-manifest.json').read_text())
            scenarios.add(meta['scenario'])
            seeds.append(meta['seed'])
            panel_hashes.add(meta['operational_dataset_sha256'])
            issues.add(meta['issuance'])
            with np.load(folder / 'forecasts.npz') as f:
                data = dict(f)
            if first is None:
                first = data
            for key in ('context_end', 'target_dates', 'locations', 'quantile_levels'):
                if not np.array_equal(data[key], first[key]):
                    raise ValueError(f'Misaligned operational {key}')
            if data['mask'].any() or data['quantiles'].shape[1] != 1:
                raise ValueError('Expected one issuance with unknown future labels')
            values.append(data['quantiles'])
            draws.append(data['samples'] if 'samples' in data else None)
            sources.append(dict(recipe=name, directory=str(folder), checkpoint_sha256=meta['checkpoint_sha256'],
                                forecast_sha256=sha256(folder / 'forecasts.npz')))
        if len(scenarios) != 1 or len(set(seeds)) != len(seeds):
            raise ValueError(f'{name}: inconsistent recipe or duplicate seed')
        if len({d is None for d in draws}) != 1:
            raise ValueError(f'{name}: some seeds have samples and some do not')
        channels = trained_channels(scenarios.pop(), problem)
        routing = release.get('recipe_targets', {})
        if set(routing) - set(members):
            raise ValueError('Target routing names an unknown recipe')
        if name in routing:
            requested = routing[name]
            available = {problem.target_signals[c].hub_target: c for c in channels}
            if not requested or len(set(requested)) != len(requested) or set(requested) - set(available):
                raise ValueError(f'{name}: target routing must select distinct targets learned by this recipe')
            channels = [available[target] for target in requested]
        recipes.append(dict(name=name, channels=channels, values=np.stack(values),
                            samples=None if draws[0] is None else np.stack(draws)))
    if len(panel_hashes) != 1 or len(issues) != 1 or not np.array_equal(first['quantile_levels'], LEVELS):
        raise ValueError('Inconsistent operational snapshot, issuance or quantile grid')
    reference = date.fromisoformat(str(first['context_end'][0])) + timedelta(days=7)
    tasks = json.loads((hub / 'hub-config/tasks.json').read_text())['rounds'][0]['model_tasks']
    locations = pd.read_csv(hub / 'auxiliary-data/locations.csv', dtype={'location': str})
    mapping = dict(zip(locations.abbreviation, locations.location))
    allowed = lambda spec: (spec.get('required') or []) + (spec.get('optional') or [])
    maximums = HUBS[release['hub']]['maximums']
    rows, adjustments, exported = [], [], {}
    for channel, signal in enumerate(problem.target_signals):
        target = signal.hub_target
        if not target or signal.hub != release['hub']:
            continue
        if not any(channel in r['channels'] for r in recipes):
            continue
        task, = [t for t in tasks if target in allowed(t['task_ids']['target'])]
        if reference.isoformat() not in allowed(task['task_ids']['reference_date']):
            raise ValueError('Reference date not in current Hub tasks')
        if not np.array_equal(task['output_type']['quantile']['output_type_id']['required'], LEVELS):
            raise ValueError('Current Hub quantile grid changed')
        q = combine(recipes, channel, release['rule'])[:, 0]
        if signal.unit == 'count':
            q = np.floor(q + .5)
        if not np.isfinite(q).all() or (q < 0).any() or (np.diff(q, axis=0) < 0).any() \
                or (signal.unit == 'proportion' and (q > 1).any()):
            raise ValueError('Invalid quantile values, units or ordering')
        maximum = maximums.get(target)
        if maximum is not None:
            for qi, h, li in np.argwhere(q > maximum):
                adjustments.append(dict(target=target, horizon=int(h), location=str(first['locations'][li]),
                                        quantile=float(LEVELS[qi]), original=float(q[qi, h, li]), exported=maximum,
                                        reason=f'Hub maximum={maximum}'))
            q = np.minimum(q, maximum)
        exported[channel] = (target, signal.unit, maximum, task)
        for h, day in enumerate(first['target_dates'][0]):
            if str(day) != (reference + timedelta(weeks=h)).isoformat() or h not in allowed(task['task_ids']['horizon']):
                raise ValueError('Invalid horizon/date alignment')
            for li, loc in enumerate(first['locations']):
                fips = mapping[str(loc)]
                if fips not in allowed(task['task_ids']['location']):
                    continue
                for qi, level in enumerate(LEVELS):
                    rows.append(dict(reference_date=reference.isoformat(), target=target, horizon=h,
                                     target_end_date=str(day), location=fips, output_type='quantile',
                                     output_type_id=level,
                                     value=int(q[qi, h, li]) if signal.unit == 'count' else float(q[qi, h, li])))
    design = None
    if samples:
        if release['rule'] != 'mixture' or any(sorted(r['channels']) != sorted(exported) for r in recipes):
            raise ValueError('Trajectories need a mixture whose recipes all predict every exported target')
        rng = np.random.default_rng(int(sha256(Path(release['problem']))[:8], 16))
        channels = range(recipes[0]['values'].shape[-2])
        paths = trajectories([dict(quantiles=np.stack([combine([r], c, 'mixture')[:, 0] if c in exported else
                                                       np.zeros_like(combine([r], next(iter(exported)), 'mixture')[:, 0])
                                                       for c in channels], -2),
                                   samples=None if r['samples'] is None else r['samples'][:, 0]) for r in recipes], SAMPLES, rng)
        for channel, (target, unit, maximum, task) in exported.items():
            if 'sample' not in task['output_type']:
                raise ValueError(f'{target}: the Hub takes no samples')
            v = paths[:, :, channel]
            v = np.floor(v + .5) if unit == 'count' else np.clip(v, 0, 1 if maximum is None else maximum)
            if not np.isfinite(v).all() or (v < 0).any():
                raise ValueError('Invalid sample values')
            for k in range(SAMPLES):
                for h, day in enumerate(first['target_dates'][0]):
                    for li, loc in enumerate(first['locations']):
                        if mapping[str(loc)] in allowed(task['task_ids']['location']):
                            rows.append(dict(reference_date=reference.isoformat(), target=target, horizon=h,
                                             target_end_date=str(day), location=mapping[str(loc)], output_type='sample',
                                             output_type_id=f'{loc}_{k}', value=int(v[k, h, li]) if unit == 'count' else float(v[k, h, li])))
        design = dict(samples_per_location=SAMPLES, recipes={r['name']: 'own draws' if r['samples'] is not None else
                      'stratified marginals from quantiles, Schaake-ordered by the sampling recipes' for r in recipes},
                      sample_id='<location abbreviation>_<k>, shared by every horizon and target of a location')
    table = pd.DataFrame(rows)
    if table.empty or table.drop(columns='value').duplicated().any():
        raise ValueError('Empty or duplicate Hub tasks')
    out.mkdir(parents=True, exist_ok=True)
    path = out / f'{reference}-ACCIDDA-{release["model_abbr"]}.csv'
    table.to_csv(path, index=False)
    record = dict(release=release, sources=sources, adjustments=adjustments, rows=len(table), issuance=next(iter(issues)),
                  operational_panel_sha256=next(iter(panel_hashes)), hub_tasks_sha256=sha256(hub / 'hub-config/tasks.json'),
                  output_sha256=sha256(path), problem=problem.reference, problem_sha256=problem.hash,
                  definition=dict(note=release['description']), trajectories=design)
    if 'parquet' in json.loads((hub / 'hub-config/admin.json').read_text()).get('file_format', []):
        import pyarrow as pa, pyarrow.parquet as pq
        typed = table.assign(reference_date=pd.to_datetime(table.reference_date).dt.date,
                             target_end_date=pd.to_datetime(table.target_end_date).dt.date,
                             horizon=table.horizon.astype('int32'), output_type_id=table.output_type_id.astype(str),
                             value=table.value.astype('float64'))
        schema = pa.schema([('reference_date', pa.date32()), ('target', pa.string()), ('horizon', pa.int32()),
                            ('target_end_date', pa.date32()), ('location', pa.string()), ('output_type', pa.string()),
                            ('output_type_id', pa.string()), ('value', pa.float64())])
        pq.write_table(pa.Table.from_pandas(typed[schema.names], schema=schema, preserve_index=False), path.with_suffix('.parquet'))
        record['parquet_sha256'] = sha256(path.with_suffix('.parquet'))
    path.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
    return path
