"""State and regional context for the five historical Texas county targets."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.dataset.build import load
from chromantis.dataset.extract import HHS_REGIONS

ROOT = Path('data/metrocast-county-context')
NAMES = ('state_flu_context', 'region_other_state_flu_mean')


def build():
    source = Path('data/processed/panel.npz')
    panel = load(source)
    base_path = Path('data/metrocast-county-2024/panel.npz')
    base = load(base_path)
    assert set(base['locations']) == {'Austin', 'Dallas', 'El Paso', 'Houston', 'San Antonio'}
    locations = list(panel['locations'])
    channel = list(panel['target_names']).index('nssp_flu_proportion')
    neighbors = [s for s in HHS_REGIONS[6].split() if s != 'TX']
    indices = [locations.index(s) for s in neighbors]

    def context(values):
        region = values[..., indices, channel]
        count = np.isfinite(region).sum(-1)
        mean = np.where(count > 0, np.nansum(region, axis=-1) / np.maximum(count, 1), np.nan)
        return np.stack((values[..., locations.index('TX'), channel], mean), axis=-1)

    date_indices = pd.Index(panel['dates'].astype(str)).get_indexer(base['dates'].astype(str))
    assert (date_indices >= 0).all()
    revised = context(panel['targets'])[date_indices]
    archive = context(panel['asof_targets'])[:, date_indices]
    hub = list(panel['hub_names']).index('flusight')
    cutoffs = panel['issuance_cutoffs_utc'][hub].astype(str)
    assert len(cutoffs) == len(archive)
    for x in (revised, archive):
        assert np.isfinite(x).any() and np.nanmin(x) >= 0 and np.nanmax(x) <= 1
    ROOT.mkdir(exist_ok=True)
    # The target panel and labels remain byte-for-byte equal to the county benchmark.
    base['covariates'] = np.repeat(revised[:, None, :], len(base['locations']), axis=1)
    base['covariate_names'] = np.array(NAMES)
    np.savez_compressed(ROOT / 'panel.npz', **base)
    np.savez_compressed(ROOT / 'context-vintages.npz', dates=base['dates'], cutoffs_utc=cutoffs,
                        names=np.array(NAMES), values=archive)
    digest = hashlib.sha256()
    with source.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    metadata = dict(source=str(source), source_sha256=digest.hexdigest(),
                    source_metadata=json.loads(str(panel['metadata'])),
                    own_state='TX', other_region_states=neighbors,
                    regional_measure='Unweighted mean of observed state flu ED proportions; not a regional population ED rate',
                    training='Revised covariates with the latest history week hidden by the source schedule; labels unchanged',
                    archived_evaluation='Latest source snapshot whose recorded UTC cutoff is no later than MetroCast Wednesday 20:00 America/New_York; missing stays missing')
    (ROOT / 'manifest.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps({k: v for k, v in metadata.items() if k != 'source_metadata'}, indent=2))


def archived_context(episode, names, archive, cutoff):
    """Return [week, covariate, value/mask, county] without any later-value fill."""
    requested = pd.Timestamp(cutoff + ' 20:00', tz='America/New_York').tz_convert('UTC')
    cutoffs = pd.to_datetime(archive['cutoffs_utc'], utc=True)
    eligible = np.flatnonzero(cutoffs <= requested)
    result = np.zeros((len(episode['context_dates']), len(names), 2, len(episode['locations'])), np.float32)
    if not len(eligible):
        return result, None
    row = eligible[np.argmax(cutoffs[eligible].asi8)]
    assert cutoffs[row] <= requested
    dates = pd.Index(archive['dates'].astype(str))
    table = pd.DataFrame(archive['values'][row], index=dates, columns=archive['names'])
    x = table.reindex(index=episode['context_dates'], columns=names).to_numpy(np.float32)
    result[:, :, 0] = np.nan_to_num(x)[..., None]
    result[:, :, 1] = np.isfinite(x)[..., None]
    return result, cutoffs[row].isoformat()


if __name__ == '__main__':
    build()
