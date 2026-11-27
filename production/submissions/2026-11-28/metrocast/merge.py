"""Merge the spliced ED file with one California version into the Hub file; check against the Hub's tasks.

Usage: python merge.py CALIFORNIA_DIR OUT.parquet
"""
import json, sys
import pandas as pd, pyarrow.parquet as pq
e = pd.read_parquet('spliced/2026-11-28-ACCIDDA-Chromantis.parquet'); c = pd.read_parquet(f'{sys.argv[1]}/2026-11-28-california.parquet')
for d in (e, c):
    d['reference_date'] = pd.to_datetime(d.reference_date).dt.date; d['target_end_date'] = pd.to_datetime(d.target_end_date).dt.date
out = pd.concat([e, c[e.columns]], ignore_index=True)
assert not out.duplicated(['target', 'location', 'target_end_date', 'output_type_id']).any()
assert out.groupby(['target', 'location', 'target_end_date']).output_type_id.nunique().eq(100).all()
assert not set(out[out.target == 'Flu hosp admits'].output_type_id) & set(out[out.target == 'Flu ED visits pct'].output_type_id)
t = json.load(open('../../../hubs/flu-metrocast/hub-config/tasks.json'))
for task in t['rounds'][-1]['model_tasks']:
    tid = task['task_ids']; tg = tid['target'].get('optional') or []
    sub = out[out.target.isin(tg)]
    assert not set(sub.location) - set(tid['location'].get('optional') or [])
    assert not set(sub.target_end_date.astype(str)) - set(tid['target_end_date'].get('optional') or [])
    assert '2026-11-28' in tid['reference_date']['optional']
    print(tg, len(sub), sub.location.nunique(), sub.target_end_date.min(), sub.target_end_date.max())
# Write with the previous round's exact Arrow schema (a newer pandas writes large_string instead of string).
import pyarrow as pa
prev = pq.read_schema('../../2026-11-21/metrocast/2026-11-21-ACCIDDA-Chromantis.parquet')
pq.write_table(pa.Table.from_pandas(out, schema=prev.remove_metadata(), preserve_index=False), sys.argv[2])
print(pq.read_schema(sys.argv[2]).remove_metadata().equals(pq.read_schema('../../2026-11-21/metrocast/2026-11-21-ACCIDDA-Chromantis.parquet').remove_metadata()), len(out))
