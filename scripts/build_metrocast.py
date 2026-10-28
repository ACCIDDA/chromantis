"""Build a pinned MetroCast percentage panel, converted once to proportions."""
import json
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    root = Path('data/metrocast')
    source = root / 'source'
    data = pd.read_csv(source / 'latest-data.csv')
    metadata = pd.read_csv(source / 'locations.csv')
    tasks = json.loads((source / 'tasks.json').read_text())['rounds'][-1]['model_tasks'][0]
    eligible = tasks['task_ids']['location']['optional']
    data = data[data.target.eq('Flu ED visits pct') & data.location.isin(eligible)].copy()
    if data.duplicated(['target_end_date', 'location']).any():
        raise ValueError('Duplicate location/week observations')
    if not data.observation.dropna().between(0, 100).all():
        raise ValueError('Source values must be percentages in [0,100]')
    locations = sorted(data.location.unique())
    dates = pd.date_range('2022-07-30', data.target_end_date.max(), freq='W-SAT')
    wide = data.pivot(index='target_end_date', columns='location', values='observation')
    values = wide.reindex(index=dates.strftime('%Y-%m-%d'), columns=locations).to_numpy(np.float32) / 100
    if not pd.to_datetime(data.target_end_date).dt.dayofweek.eq(5).all():
        raise ValueError('Every observation must end on Saturday')
    # Own-state histories are available to each local model at the same weekly cutoff.
    selected = metadata.set_index('location').loc[locations]
    state_names = selected.state.str.lower().str.replace(' ', '-')
    state = wide.reindex(index=dates.strftime('%Y-%m-%d'), columns=list(state_names)).to_numpy(np.float32) / 100
    arrays = dict(
        dates=dates.to_numpy(dtype='datetime64[D]'), locations=np.array(locations),
        target_names=np.array(['metrocast_flu_proportion']),
        targets=values[..., None],
        covariates=state[..., None],
        covariate_names=np.array(['state_flu_proportion']),
        covariates_national=np.empty((len(dates), 0), np.float32),
        covariate_national_names=np.array([], dtype='U1'),
        truth_day=np.array('2026-10-20'),
    )
    np.savez_compressed(root / 'panel.npz', **arrays)
    selected.reset_index().to_csv(root / 'locations.csv', index=False)
    # State ILI is a pretraining source, not a claim of historical local flu observations.
    with np.load('data/processed/historical_ili.npz') as old:
        ids = [str(v).upper() for v in old['locations']]
        hist = np.column_stack([old['values'][:, ids.index(abb)] if abb in ids
                                else np.full(len(old['dates']), np.nan)
                                for abb in selected.state_abb])
        if not np.isfinite(hist).any(axis=0).all():
            raise ValueError('A location lacks a mapped historical state ILI series')
        np.savez_compressed(root / 'historical_ili.npz', values=hist, dates=old['dates'],
                            locations=np.array(locations))
    provenance = dict(
        hub_commit=json.loads((source / 'commit.json').read_text())['sha'],
        locations=locations, missing_locations=sorted(set(eligible) - set(locations)),
        observations=int(np.isfinite(values).sum()), first=str(dates[0].date()),
        last=str(dates[-1].date()), input_units='percentage', panel_units='proportion',
        evaluation_inputs='latest revised history; not a real-time backtest',
        pretraining='2010-2011 through 2021-2022 state ILI broadcast to local jurisdictions, '
                    'scaled using only each training partition; not observed local flu labels',
        nyc='Hub latest-data labels NYC as Flu ED visits pct; older vintage archive calls it ILI. '
            'Keep the pinned hub series, and report NYC separately before submission.',
    )
    (root / 'manifest.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(json.dumps(provenance, indent=2))


if __name__ == '__main__':
    main()
