"""California flu hospital admissions panel for the MetroCast 'Flu hosp admits' target.

History (rewritten 2026-11-11): the first version summed CDPH dashboard age groups, which
suppresses small cells and runs ~10% below the Hub target. Labels now come from the sources
that match the Hub definition:
  1. private cdphmodeling/flu_metrocast_california_data historical file (Oct 2022 - Oct 2024),
  2. the latest release in its versioned file (Nov 2024 - Sep 2026),
  3. Hub target-data/latest-data.csv (Jul 2026 onward), which wins where it overlaps.
The statewide series is the Hub's value where it exists and the sum of the six regions
before (the Hub statewide differs from the regional sum by up to 14 admissions).
Covariates come from the public CDPH Respiratory Virus Dashboard (from July 2024 only).
"""
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path('data/metrocast-california')
SOURCE = ROOT/'source'
HISTORICAL = SOURCE/'historical_flu_data_share_2026_09_24.csv'
VERSIONED = SOURCE/'versioned_flu_data_share_2026_09_24.parquet'
HUB = SOURCE/'hub-latest-data.csv'
DASHBOARD = SOURCE/'ca-rv-dashboard.csv'
REGIONS = ['bay-area', 'central-california', 'greater-sierra-sacramento', 'los-angeles', 'rural-north', 'southern-california']
LOCATIONS = sorted(REGIONS+['california'])


def slug(x):
    return re.sub('[^a-z0-9]+', '-', x.lower())


def main():
    hist = pd.read_csv(HISTORICAL).assign(location=lambda d: d.location.map(slug), date=lambda d: d.weekending_date.astype(str))
    ver = pd.read_parquet(VERSIONED).assign(location=lambda d: d.location.map(slug), date=lambda d: d.weekending_date.astype(str))
    latest_release = ver.version_date.astype(str).max()
    ver = ver[ver.version_date.astype(str) == latest_release]
    hub = pd.read_csv(HUB)
    hub = hub[hub.target == 'Flu hosp admits'].rename(columns=dict(target_end_date='date', observation='flu_admits'))
    assert hist.date.max() < ver.date.min()
    regional = pd.concat([hist[['date', 'location', 'flu_admits']], ver[['date', 'location', 'flu_admits']]])
    assert not regional.duplicated(['date', 'location']).any() and set(regional.location) == set(REGIONS)
    table = regional.pivot(index='date', columns='location', values='flu_admits')
    table['california'] = table[REGIONS].sum(axis=1, min_count=len(REGIONS))
    hub_table = hub.pivot(index='date', columns='location', values='flu_admits')
    dates = pd.date_range(min(table.index), max(hub_table.index), freq='W-SAT').strftime('%Y-%m-%d')
    table = table.reindex(index=dates, columns=LOCATIONS)
    hub_table = hub_table.reindex(index=dates, columns=LOCATIONS)
    changed = (hub_table.notna() & table.notna() & (hub_table != table)).to_numpy().sum()
    table = hub_table.combine_first(table)
    values = table.to_numpy(np.float32)
    assert (values[np.isfinite(values)] >= 0).all()

    raw = pd.read_csv(DASHBOARD)
    allages = raw[raw.AGE_GRP.eq('All Ages')].assign(date=lambda d: pd.to_datetime(d.WEEKENDING).dt.strftime('%Y-%m-%d'),
                                                    location=lambda d: d.RPHO_REGION.map(slug))
    def grid(column):  # duplicated location/weeks: mean of the published values
        return allages.groupby(['date', 'location'])[column].mean().unstack().reindex(index=dates, columns=LOCATIONS)
    tp = grid('FLU_TP').to_numpy(np.float32)
    ed = grid('FLU_ED_VISITS').mean(axis=1).to_numpy(np.float32)
    state = values[:, LOCATIONS.index('california')]
    covariates = np.stack([tp, np.repeat(state[:, None], len(LOCATIONS), 1), np.repeat(ed[:, None], len(LOCATIONS), 1)], -1)
    covariate_names = ['ca_flu_test_positivity', 'ca_statewide_flu_admissions', 'ca_statewide_flu_ed_visits']

    np.savez_compressed(ROOT/'panel.npz', dates=pd.to_datetime(dates).to_numpy(dtype='datetime64[D]'), locations=np.array(LOCATIONS),
        target_names=np.array(['metrocast_ca_flu_admissions']), targets=values[..., None],
        covariates=covariates, covariate_names=np.array(covariate_names),
        covariates_national=np.empty((len(dates), 0), np.float32), covariate_national_names=np.array([], dtype='U1'),
        truth_day=np.array(str(hub.date.max())))
    pd.read_csv('data/metrocast/source/locations.csv').set_index('location').loc[LOCATIONS].reset_index().to_csv(ROOT/'locations.csv', index=False)
    with np.load('data/processed/historical_ili.npz') as f:
        ca = [str(v).upper() for v in f['locations']].index('CA')
        np.savez_compressed(ROOT/'historical_ili.npz', dates=f['dates'], locations=np.array(LOCATIONS),
                            values=np.repeat(f['values'][:, ca:ca+1], len(LOCATIONS), axis=1))
    manifest = dict(
        sources={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (HISTORICAL, VERSIONED, HUB, DASHBOARD)},
        versioned_release_used=latest_release, first=dates[0], last=dates[-1], target='Flu hosp admits', unit='count',
        labels='Private historical file through 2024-10-26, latest private release through its last week, Hub target data from 2026-07-11 (Hub wins on overlap). Statewide = Hub value where available, else sum of the six regions.',
        hub_overrides_of_private_values=int(changed),
        covariates='From CDPH dashboard, July 2024 onward, missing before. ca_flu_test_positivity: All Ages FLU_TP per location (percent). ca_statewide_flu_admissions: the california label repeated. ca_statewide_flu_ed_visits: All Ages FLU_ED_VISITS (statewide only) repeated.',
        historical_pretraining='2010-11 through 2021-22 California state ILI repeated at all seven locations (pseudo-counts after fit-only Q95 scaling).',
        overlap='California statewide total overlaps six constituent regions; equal location scoring counts both levels.')
    (ROOT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('dates', dates[0], dates[-1], len(dates), 'observed share', float(np.isfinite(values).mean().round(3)), 'hub overrides', changed)


if __name__ == '__main__':
    main()
