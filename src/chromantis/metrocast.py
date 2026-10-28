"""MetroCast sample output: preserve whole trajectories and convert proportions once."""
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def write_samples(samples, locations, reference_date, destination, seed=42, target='Flu ED visits pct'):
    """Write [draw, week, location] native-unit draws as 100 intact weekly paths.

    The caller supplies joint model draws, not independently sampled marginal
    quantiles. With more than 100 draws, one subset is used across all horizons
    and locations. Jurisdiction eligibility is checked against the pinned Hub.
    Flu-ED proportions convert to percentages; admission counts stay unchanged.
    """
    reference = date.fromisoformat(str(reference_date))
    if reference.weekday() != 5:
        raise ValueError('MetroCast reference_date must be a Saturday')
    x = np.asarray(samples)
    locations = list(map(str, locations))
    if x.ndim != 3 or x.shape[0] < 100 or x.shape[1] < 4 or x.shape[2] != len(locations):
        raise ValueError('Expected at least 100 draws, at least four weeks, and one axis matching locations')
    weeks = x.shape[1]
    if len(locations) != len(set(locations)):
        raise ValueError('Duplicate locations')
    if target not in {'Flu ED visits pct', 'Flu hosp admits'}:
        raise ValueError('Unsupported MetroCast target')
    if not np.isfinite(x).all() or (x < 0).any():
        raise ValueError('Model output must be finite and nonnegative')
    if target == 'Flu ED visits pct' and (x > 1).any():
        raise ValueError('Flu-ED model output must be proportions in [0,1]')
    import json
    config = json.loads(Path('data/metrocast/source/tasks.json').read_text())
    task = next(t for t in config['rounds'][-1]['model_tasks']
                if target in (t['task_ids']['target'].get('optional') or []))
    eligible = set(task['task_ids']['location'].get('optional') or [])
    if set(locations) - eligible:
        raise ValueError(f'Unknown MetroCast {target} locations: {sorted(set(locations) - eligible)}')
    if reference.isoformat() not in task['task_ids']['reference_date']['optional']:
        raise ValueError('Reference date is outside the pinned MetroCast season')
    if any((reference + timedelta(weeks=h)).isoformat() not in
           task['task_ids']['target_end_date']['optional'] for h in range(weeks)):
        raise ValueError('A target date is outside the pinned MetroCast season')
    ids = np.random.default_rng(seed).choice(len(x), 100, replace=False)
    x = x[ids]
    n = len(locations)
    output = pd.DataFrame(dict(
        reference_date=[reference] * (100 * weeks * n),
        target=target,
        target_end_date=np.tile(np.repeat([reference + timedelta(weeks=h) for h in range(weeks)], n), 100),
        location=np.tile(locations, 100 * weeks),
        output_type='sample',
        output_type_id=np.repeat(np.array([f'S{i}' for i in range(1, 101)]), weeks * n),
        value=x.reshape(-1).astype(float) * (100 if target == 'Flu ED visits pct' else 1),
    ))
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.to_parquet(destination, index=False)
    return output
