"""Splice for reference date 2026-11-21, same rule as production/submissions/2026-10-31/metrocast/splice.py.

The full-season run is cut at the Hub's last target week, 2027-06-12 (30 weeks from 2026-11-21).
Horizons 0-3 from the 4-week winner (cv_winner_r010_c08), later weeks from full_season_finalist_1, both
unmodified. At each location, the trajectory with the k-th largest week-3 value (2026-12-12) in the 4-week
file continues with the full-season path that is k-th largest at its own week 3.
"""
import pandas as pd

four = pd.read_parquet('winner/2026-11-21-ACCIDDA-Chromantis.parquet')
full = pd.read_parquet('fullseason/2026-11-21-ACCIDDA-Chromantis-fullseason.parquet')
full = full[pd.to_datetime(full.target_end_date) <= '2027-06-12']  # Hub's last target week; the 31-week run reaches 2027-06-19
for d in (four, full):
    d['target_end_date'] = pd.to_datetime(d.target_end_date).dt.date
    d['reference_date'] = pd.to_datetime(d.reference_date).dt.date
boundary = pd.Timestamp('2026-12-12').date()
parts = [four]
for loc, f in full.groupby('location'):
    a = four[(four.location == loc) & (four.target_end_date == boundary)].sort_values('value')
    b = f[f.target_end_date == boundary].sort_values('value')
    tail = f[f.target_end_date > boundary].copy()
    tail['output_type_id'] = tail.output_type_id.map(dict(zip(b.output_type_id, a.output_type_id)))
    parts.append(tail)
out = pd.concat(parts)[four.columns].sort_values(['location', 'output_type_id', 'target_end_date'])
assert out.groupby(['location', 'target_end_date']).output_type_id.nunique().eq(100).all()
assert not out.duplicated(['location', 'target_end_date', 'output_type_id']).any()
assert out.target_end_date.max() == pd.Timestamp('2027-06-12').date()
out.to_parquet('spliced/2026-11-21-ACCIDDA-Chromantis.parquet', index=False)
step = out.pivot_table(index=['location', 'output_type_id'], columns='target_end_date', values='value')
jump = (step[pd.Timestamp('2026-12-19').date()] / step[boundary]).groupby('location').median()
print(len(out), 'rows;', out.target_end_date.nunique(), 'weeks; median week-4/week-3 ratio across locations',
      round(jump.median(), 2))
