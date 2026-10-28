"""Isolate weekly Utah targets proposed in unmerged MetroCast PR 587."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('data/metrocast-utah-proposed')
NAMES = {'Bear River': 'bear-river', 'Central': 'central', 'Davis': 'davis',
         'San Juan': 'san-juan', 'Salt Lake': 'salt-lake', 'Southeast': 'southeast',
         'Southwest': 'southwest', 'Summit': 'summit', 'Tooele': 'tooele',
         'TriCounty': 'tri-county', 'Utah County': 'utah-county',
         'Wasatch': 'wasatch', 'Weber-Morgan': 'weber-morgan', 'utah-state': 'utah'}


def main():
    source = ROOT/'source'
    pull = json.loads((source/'pull-587.json').read_text())
    raw = pd.read_csv(source/'utah-weekly.csv')
    assert raw.signal.eq('pct_ed_visits_influenza').all()
    assert raw.geo_value.eq(raw.region).all()
    # Raw identifiers 4/5 mean San Juan/Salt Lake, opposite the location metadata.
    # The proposed target file correctly maps names; never join these numeric codes.
    raw['location'] = raw.geo_value.str.replace(r'^\d+\s+', '', regex=True).map(NAMES)
    raw['target_end_date'] = pd.to_datetime(raw.time_value).dt.strftime('%Y-%m-%d')
    assert raw.location.notna().all() and raw.location.nunique() == 14
    assert pd.to_datetime(raw.target_end_date).dt.dayofweek.eq(5).all()
    assert not raw.duplicated(['location', 'target_end_date']).any()
    assert np.isfinite(raw.value).all() and raw.value.between(0, 100).all()
    targets = pd.read_csv(source/'latest-data.csv')
    targets = targets[targets.location.isin(NAMES.values())]
    assert targets.target.eq('Flu ED visits pct').all()
    matched = raw.merge(targets, on=['location', 'target_end_date'], validate='one_to_one')
    assert len(matched) == len(raw) == len(targets)
    np.testing.assert_array_equal(matched.value, matched.observation)
    locations = sorted(NAMES.values())
    dates = pd.date_range(raw.target_end_date.min(), raw.target_end_date.max(), freq='W-SAT')
    values = raw.pivot(index='target_end_date', columns='location', values='value').reindex(
        index=dates.strftime('%Y-%m-%d'), columns=locations).to_numpy(np.float32)/100
    assert np.isfinite(values).all()
    np.savez_compressed(ROOT/'panel.npz', dates=dates.to_numpy(dtype='datetime64[D]'),
        locations=np.array(locations), target_names=np.array(['metrocast_flu_proportion']),
        targets=values[..., None], covariates=np.empty((*values.shape, 0), np.float32),
        covariate_names=np.array([], dtype='U1'),
        covariates_national=np.empty((len(dates), 0), np.float32),
        covariate_national_names=np.array([], dtype='U1'), truth_day=np.array('2026-10-20'))
    metadata = pd.read_csv(source/'locations.csv').set_index('location').loc[locations]
    metadata.reset_index().to_csv(ROOT/'locations.csv', index=False)
    raw[['target_end_date', 'location', 'value']].to_csv(ROOT/'verified-weekly-percentages.csv', index=False)
    manifest = dict(
        source_pr='https://github.com/reichlab/flu-metrocast/pull/587',
        source_repository=pull['head']['repo']['full_name'], source_sha=pull['head']['sha'],
        merged_at_capture=pull['merged'], status='Provisional unmerged source; separate from pinned main panel',
        source_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()},
        geography='13 named Utah districts plus statewide; state overlaps district population',
        mapping='Explicit district names, independently equal to every proposed target-data row; numeric raw region 4/5 do not match metadata codes',
        labels='Proposed weekly influenza ED visit percentages divided by 100 exactly once',
        training_seasons=['2022-2023', '2023-2024'], development_season='2024-2025',
        reserved_season='2025-2026; excluded from iterative selection',
        inputs='Single revised weekly source; no historical release-availability or ensemble-performance claim',
        weighting='Equal observed-location weight, including the overlapping statewide series',
        dates=[str(dates[0].date()), str(dates[-1].date())], locations=locations,
        dashboard_averages_used=False, published=False,
    )
    (ROOT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Verified', len(raw), 'weekly rows;', len(locations), 'locations;', len(dates), 'weeks')


if __name__ == '__main__':
    main()
