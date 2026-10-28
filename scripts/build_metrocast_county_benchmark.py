"""Reproduce the five-county 2024-25 MetroCast target, not the later HSA target."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

import numpy as np
import pandas as pd

SHA = '36440ff6bfbf1475b60187ec3c038eb72bc0052c'
ROOT = Path('data/metrocast-county-2024')


def main():
    source = ROOT / 'source'
    source.mkdir(parents=True, exist_ok=True)
    base = f'https://raw.githubusercontent.com/reichlab/flu-metrocast/{SHA}/'
    tree = json.load(urllib.request.urlopen(
        f'https://api.github.com/repos/reichlab/flu-metrocast/git/trees/{SHA}?recursive=1'))
    paths = ['target-data/time-series.csv', 'target-data/oracle-output.csv']
    paths += [r['path'] for r in tree['tree']
              if r['path'].startswith('model-output/epiENGAGE-ensemble_mean/') and r['path'].endswith('.csv')]

    def fetch(path):
        dest = source / Path(path).name
        if not dest.exists():
            dest.write_bytes(urllib.request.urlopen(base + path).read())
        return dict(path=path, sha256=hashlib.sha256(dest.read_bytes()).hexdigest())

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        files = list(pool.map(fetch, paths))
    raw = pd.read_csv(source / 'time-series.csv')
    raw = raw[raw.target.eq('Flu ED visits pct')].copy()
    assert not raw.duplicated(['as_of', 'target_end_date', 'location']).any()
    truth = pd.read_csv(source / 'oracle-output.csv')
    truth = truth[truth.target.eq('Flu ED visits pct')]
    assert not truth.duplicated(['target_end_date', 'location']).any()
    assert truth.oracle_value.between(0, 100).all()
    locations = sorted(truth.location.unique())
    assert len(locations) == 5
    dates = pd.date_range('2022-07-30', truth.target_end_date.max(), freq='W-SAT')
    wide = truth.pivot(index='target_end_date', columns='location', values='oracle_value')
    values = wide.reindex(index=dates.strftime('%Y-%m-%d'), columns=locations).to_numpy(np.float32) / 100
    np.savez_compressed(ROOT / 'panel.npz', dates=dates.to_numpy(dtype='datetime64[D]'),
                        locations=np.array(locations), target_names=np.array(['metrocast_flu_proportion']),
                        targets=values[..., None], covariates=np.empty((*values.shape, 0), np.float32),
                        covariate_names=np.array([], dtype='U1'),
                        covariates_national=np.empty((len(dates), 0), np.float32),
                        covariate_national_names=np.array([], dtype='U1'))
    # Population is unused: geography is disabled and every target is a proportion.
    pd.DataFrame(dict(location=locations, population=1)).to_csv(ROOT / 'locations.csv', index=False)
    manifest = dict(commit=SHA, files=files, locations=locations,
                    target='County flu ED proportions, using the historical MetroCast oracle',
                    county_mapping={'Austin': 'Travis', 'Dallas': 'Dallas', 'El Paso': 'El Paso',
                                    'Houston': 'Harris', 'San Antonio': 'Bexar'},
                    population='Unused placeholders; geography must remain disabled',
                    training_seasons=['2022-2023', '2023-2024'], evaluation_season='2024-2025',
                    ensemble='epiENGAGE-ensemble_mean', inputs='Both revised and archived-input evaluation')
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
