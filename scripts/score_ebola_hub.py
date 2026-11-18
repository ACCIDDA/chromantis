"""Score every BDBV Hub submission for `wk inc confirmed cases` against one target-data release.

Every model file on the local hub clone (all rounds, every forecast_date kept apart) is scored on
each location-week it covers that is in the release: WIS from 23 sample quantiles (2 x mean pinball
loss, as the hub's quantile levels 0.01 ... 0.99), on counts and on log(1 + counts), lower is better;
50% and 90% central-interval coverage; median. Each row says whether the week was a nowcast for that
round (it ended on or before the round's last data week, reference date minus 7 days) or a forecast,
and how many weeks old it is in the scoring release (lag 0 = the release's newest week, still far
from complete).

    .venv/bin/python scripts/score_ebola_hub.py            # latest release -> data/ebola/hub-scores-<release>.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HUB = Path('../hubs/BDBV-Modeling-Hub')
Q = np.array([.01, .025] + list(np.round(np.arange(.05, .951, .05), 2)) + [.975, .99])


def main():
    t = pd.read_csv(HUB / 'target-data/time-series.csv')
    release = sys.argv[1] if len(sys.argv) > 1 else t.as_of.max()
    truth = t[t.as_of == release].set_index(['location', 'target_end_date']).observation
    newest = pd.Timestamp(t[t.as_of == release].target_end_date.max())
    rows = []
    for f in sorted((HUB / 'model-output').glob('*/*.csv')):
        d = pd.read_csv(f, dtype={'forecast_date': str, 'location': str})
        d = d[(d.target == 'wk inc confirmed cases') & (d.output_type == 'sample')]
        if d.empty:
            continue
        d['target_end_date'] = pd.to_datetime(d.target_end_date, format='mixed', dayfirst=True).dt.strftime('%Y-%m-%d')
        ref = f.name[:10]
        last_data = pd.Timestamp(ref) - pd.Timedelta(days=7)
        for (fd, loc, week), g in d.groupby(['forecast_date', 'location', 'target_end_date']):
            if (loc, week) not in truth.index:
                continue
            y, s = truth[(loc, week)], g.value.to_numpy(float)
            q = np.quantile(s, Q)
            wis = lambda yy, qq: 2 * np.mean(np.maximum(Q * (yy - qq), (Q - 1) * (yy - qq)))
            rows.append(dict(model=f.parent.name, reference_date=ref, forecast_date=fd, location=loc, week=week,
                             role='nowcast' if pd.Timestamp(week) <= last_data else 'forecast',
                             weeks_after_last_data=(pd.Timestamp(week) - last_data).days // 7,
                             lag_in_release=(newest - pd.Timestamp(week)).days // 7, observed=y,
                             median=np.median(s), wis=wis(y, q), wis_log=wis(np.log1p(y), np.log1p(q)),
                             in50=q[Q == .25][0] <= y <= q[Q == .75][0], in90=q[Q == .05][0] <= y <= q[Q == .95][0]))
    out = Path(f'data/ebola/hub-scores-{release}.csv')
    pd.DataFrame(rows).to_csv(out, index=False)
    print(out, len(rows), 'rows')


if __name__ == '__main__':
    main()
