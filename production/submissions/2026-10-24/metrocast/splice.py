"""Splice: horizons 0-3 from the 4-week winner, later weeks from the full-season model, both unmodified.

Each horizon comes from the model that scored best there: the season-CV 4-week winner for weeks
0-3, full_season_finalist_1 (lowest 2025-26 WIS at horizons 4-12 and 13-25 of four full-season
candidates) after. At each location, the trajectory with the k-th largest week-3 value (2026-11-14)
in the 4-week file continues with the full-season path that is k-th largest at its own week 3.
The full-season model runs about 40% below the 4-week model, so paths drop at the join. An earlier
version faded the level ratio out over four weeks to hide the drop; it was removed because it
changed the full-season model's weeks 4-7 with an unvalidated adjustment.
"""
import pandas as pd

four = pd.read_parquet('2026-10-24-ACCIDDA-Chromantis.parquet')
full = pd.read_parquet('full-season/2026-10-24-ACCIDDA-Chromantis-fullseason.parquet')
for d in (four, full):
    d['target_end_date'] = pd.to_datetime(d.target_end_date).dt.date
    d['reference_date'] = pd.to_datetime(d.reference_date).dt.date
boundary = pd.Timestamp('2026-11-14').date()
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
out.to_parquet('spliced/2026-10-24-ACCIDDA-Chromantis.parquet', index=False)
step = out.pivot_table(index=['location', 'output_type_id'], columns='target_end_date', values='value')
jump = (step[pd.Timestamp('2026-11-21').date()] / step[boundary]).groupby('location').median()
print(len(out), 'rows;', out.target_end_date.nunique(), 'weeks; median week-4/week-3 ratio across locations',
      round(jump.median(), 2))
