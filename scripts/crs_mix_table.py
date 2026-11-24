"""Mixture table of the COVID/RSV search: states/DC log-admission WIS per season, ED share x 1e4, from evaluation.ensembles output.

    .venv/bin/python scripts/crs_mix_table.py data/experiments/crs-mix-c02/ranking/headline-season-scores.csv
"""
import csv,collections,sys
d=collections.defaultdict(dict)
for f in sys.argv[1:]:
  for r in csv.DictReader(open(f)):
    if r["geography"]!="states_dc" or r["history"]!=r.get("history") : continue
    d[r["name"]][(r["target"].split()[-1],r["scale"],r["season"],r["history"])]=float(r["mean_wis"])
print('name  log2425 log2526 mean | ED2425 ED2526 (x1e4) | delayed mean')
for n,v in sorted(d.items(), key=lambda x: sum(x[1].get(("hosp","log",s,"corrected"),9) for s in ("2024-2025","2025-2026"))):
  a=[v.get(("hosp","log",s,"corrected")) for s in ("2024-2025","2025-2026")]
  e=[v.get(("visits","natural",s,"corrected")) for s in ("2024-2025","2025-2026")]
  dl=[v.get(("hosp","log",s,"delayed")) for s in ("2024-2025","2025-2026")]
  m=lambda x: round(sum(x)/2,4) if None not in x else None
  print(n, [round(x,4) for x in a if x], m(a), '|', [round(x*1e4,2) for x in e if x], '|', m(dl))
