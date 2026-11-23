"""Copy of a built panel with Google Trends flu-search covariates appended as state covariates (flu search, 23 Nov 2026).

Reads scripts/pull_google_trends.py's CSVs (weekly search interest 0-100 per state, scaled to the state's maximum over the
pull window). That scale uses every week of the window, including later seasons, so the stored covariate is scale-free:
gt_<term> = log(max(v, 1) / max(median of v over the previous 52 weeks, 1)), the week's search interest relative to the
state's own trailing year (at least 6 earlier weeks, else missing). Trends is not revised after the week ends and is
available the next day, so every as-of array equals the truth up to each issuance's context end (no report-time archive).

    python scripts/add_google_trends.py data/processed/panel-coverage.npz data/raw/google_trends \
        data/processed/panel-coverage-gt.npz
"""
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.dataset.build import HUBS, load, save, visible_weeks

TERMS = ('flu_topic', 'flu_symptoms', 'tamiflu')


def ratio(series):
    v = series.clip(lower=1).astype(float)
    base = v.shift(1).rolling(52, min_periods=6).median().clip(lower=1)
    return np.log(v / base)


def main(panel_path, trends_dir, out_path):
    arrays = load(panel_path)
    dates = pd.to_datetime([str(d) for d in arrays['dates']]).strftime('%Y-%m-%d')
    locations = [str(l) for l in arrays['locations']]
    truth = np.full((len(dates), len(locations), len(TERMS)), np.nan, np.float32)
    for k, term in enumerate(TERMS):
        t = pd.read_csv(Path(trends_dir) / f'{term}.csv')
        t = t[~t.partial.astype(bool)]
        for j, loc in enumerate(locations):
            s = t[t.location == loc].set_index('date').value.sort_index()
            if s.empty:
                raise ValueError(f'no {term} for {loc}')
            truth[:, j, k] = ratio(s).reindex(dates).to_numpy()
    visible = visible_weeks(arrays['dates'], arrays['issuance_dates'])
    asof = np.where(visible[:, :, None, None], truth[None], np.nan).astype(np.float32)
    names = [f'gt_{t}' for t in TERMS]
    out = dict(arrays, covariate_names=np.array([*map(str, arrays['covariate_names']), *names]),
               covariates=np.concatenate([arrays['covariates'], truth], axis=2),
               asof_covariates=np.concatenate([arrays['asof_covariates'], asof], axis=3))
    for hub in HUBS[1:]:
        if f'hub_{hub}_asof_covariates' in arrays:
            rows = arrays[f'hub_{hub}_issuances']
            out[f'hub_{hub}_asof_covariates'] = np.concatenate([arrays[f'hub_{hub}_asof_covariates'], asof[rows]], axis=3)
    metadata = json.loads(str(arrays['metadata']))
    metadata.setdefault('extended', []).append(dict(sources=names, on=date.today().isoformat(), how=__doc__.split('\n\n')[0]))
    out['metadata'] = np.array(json.dumps(metadata))
    save(out, out_path)
    print(out_path, 'covariates', len(out['covariate_names']), 'finite share per term',
          np.isfinite(truth).mean(axis=(0, 1)).round(3))


if __name__ == '__main__':
    main(*sys.argv[1:])
