"""What differs between the Hubs we submit to: local clone, target files, peers, limits.

Each Hub's target data is read as (location, date, value), the latest reported values:
FluSight keeps one CSV per target; the RSV Hub one `time-series.parquet` with every
`as_of` vintage, of which the newest row per location and week is kept.
"""
from io import BytesIO
from pathlib import Path

import pandas as pd

HUBS = {
    'flusight': dict(
        clone='production/hubs/FluSight-forecast-hub',
        targets={'wk inc flu hosp': ('target-data/target-hospital-admissions.csv', 'Weekly flu admissions'),
                 'wk inc flu prop ed visits': ('target-data/target-ed-visits-prop.csv', 'Flu share of ED visits')},
        peers=['Google_SAI-FluEns', 'OHT_JHU-nbxd', 'CMU-TimeSeries', 'UGA_flucast-INFLAenza', 'UMass-flusion', 'NAU-vulPES'],
        maximums={'wk inc flu prop ed visits': .25}),  # FluSight validations.yml max_prop_ed_visits
    'rsv': dict(
        clone='production/hubs/rsv-forecast-hub',
        targets={'wk inc rsv hosp': ('target-data/time-series.parquet', 'Weekly RSV admissions'),
                 'wk inc rsv prop ed visits': ('target-data/time-series.parquet', 'RSV share of ED visits')},
        peers=['Google_SAI-RSVEns', 'RSVHub-ensemble', 'CFA-PyRenew_HE', 'UGA_flucast-INFLAenza', 'UM-DeepOutbreak', 'CEPH-Rtrend_rsv'],
        maximums={}),
}
TARGETS = {target: hub for hub, spec in HUBS.items() for target in spec['targets']}


def hub_of(targets):
    """The one Hub whose targets these are."""
    hubs = {TARGETS[t] for t in targets if t in TARGETS}
    if len(hubs) != 1:
        raise ValueError(f'Targets {sorted(set(targets))} do not belong to exactly one Hub')
    return hubs.pop()


def clone(hub_path, targets):
    """`--hub` if given, else the Hub's local clone."""
    return Path(hub_path) if hub_path else Path(HUBS[hub_of(targets)]['clone'])


def truth(read, target):
    """Latest reported values (location, date, value) of `target`; `read(path)` returns the file bytes."""
    path = HUBS[TARGETS[target]]['targets'][target][0]
    raw = read(path)
    if path.endswith('.parquet'):
        d = pd.read_parquet(BytesIO(raw))
        d = d[d.target == target].sort_values('as_of').drop_duplicates(['location', 'target_end_date'], keep='last')
        d = d.rename(columns={'target_end_date': 'date', 'observation': 'value'})
    else:
        d = pd.read_csv(BytesIO(raw), dtype={'location': str})
    d['date'] = pd.to_datetime(d.date)
    return d[['location', 'date', 'value']].reset_index(drop=True)
