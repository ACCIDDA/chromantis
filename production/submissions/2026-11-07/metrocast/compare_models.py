"""Compare 2026-11-07 forecasts across MetroCast models and past seasons.

Per location: horizon-0 and horizon-3 medians relative to the last observation; for files with
full-season paths, the median over sample paths of the peak (max weekly %) and of the season total
(sum of weekly % from 2026-11-07 to 2027-06-12), and the median peak week. Past seasons: the same
quantities over the same weeks of season (week of 24 October to week of 12 June).
"""
import glob, sys
from pathlib import Path
import numpy as np, pandas as pd

others, latest, out = sys.argv[1:4]
obs = pd.read_csv(latest)
obs = obs[obs.target == 'Flu ED visits pct'].assign(date=lambda d: pd.to_datetime(d.target_end_date))
last = obs.sort_values('date').groupby('location').observation.last()
files = {Path(p).name.split('2026-11-07-')[1].replace('.parquet', ''): p for p in glob.glob(f'{others}/*.parquet')}
files.update({'Chromantis 4-week (submitted)': 'winner/2026-11-07-ACCIDDA-Chromantis.parquet',
              'Chromantis full-season model alone': 'fullseason/2026-11-07-ACCIDDA-Chromantis-fullseason.parquet',
              'Chromantis spliced': 'spliced/2026-11-07-ACCIDDA-Chromantis.parquet'})
rows = []
for name, p in files.items():
    d = pd.read_parquet(p)
    d = d[d.target == 'Flu ED visits pct'] if 'target' in d else d
    d = d.assign(date=pd.to_datetime(d.target_end_date))
    kind = d.output_type.iloc[0]
    weeks = d.date.nunique()
    for loc, g in d.groupby('location'):
        r = dict(model=name, location=loc, output_type=kind, weeks=weeks)
        med = g[g.output_type == kind].groupby('date').value.median() if kind == 'sample' else \
            g[(g.output_type == 'quantile') & np.isclose(g.output_type_id.astype(float), .5)].groupby('date').value.first()
        if loc in last and last[loc] > 0 and len(med) >= 4:
            r['h0_over_last'] = med.iloc[0] / last[loc]
            r['h3_over_last'] = med.iloc[3] / last[loc]
        if kind == 'sample' and weeks >= 30:
            paths = g.pivot_table(index='output_type_id', columns='date', values='value')
            r['peak'] = paths.max(axis=1).median()
            r['total'] = paths.sum(axis=1).median()
            r['peak_week'] = pd.Series(paths.idxmax(axis=1)).sort_values().iloc[len(paths) // 2]
        rows.append(r)
past = []
for year in (2022, 2023, 2024, 2025):
    a, b = pd.Timestamp(f'{year}-10-29'), pd.Timestamp(f'{year + 1}-06-14')
    s = obs[(obs.date >= a) & (obs.date <= b)]
    for loc, g in s.groupby('location'):
        g = g.sort_values('date')
        if len(g) >= 30:
            past.append(dict(model=f'observed {year}-{str(year + 1)[2:]}', location=loc, peak=g.observation.max(),
                             total=g.observation.sum(),
                             peak_week=pd.Timestamp('2026-11-07') + (g.date.iloc[g.observation.argmax()] - a)))
t = pd.concat([pd.DataFrame(rows), pd.DataFrame(past)])
t.to_csv(out, index=False)
common = set(t[t.model == 'Chromantis 4-week (submitted)'].location)
s = t[t.location.isin(common)].groupby('model').agg(
    locations=('location', 'nunique'), h0_over_last=('h0_over_last', 'median'), h3_over_last=('h3_over_last', 'median'),
    peak=('peak', 'median'), total=('total', 'median'),
    peak_week=('peak_week', lambda x: pd.to_datetime(x.dropna()).sort_values().iloc[len(x.dropna()) // 2].date() if x.notna().any() else None))
print(s.round(2).sort_values('h3_over_last').to_string())
