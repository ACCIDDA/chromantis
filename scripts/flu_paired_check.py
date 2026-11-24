"""Seed-paired child-vs-parent check on ED share and log admissions (flu search): mean over both held-out seasons per seed,
difference with 2 SE, and per-season means. Run in the Longleaf campaign folder:
    PYTHONPATH=src .venv/bin/python scripts/flu_paired_check.py flu-s-r25,flu-s-r19 CHILD:PARENT ...
"""
import sys
sys.path.insert(0, 'scripts')
import numpy as np
from flu_search_table import load, sel, ED, HOSP
exps, pairs = sys.argv[1].split(','), [p.split(':') for p in sys.argv[2:]]
seasons, seeds, _, _ = load(exps)
for label, target, scale in (('ED share x1e4', ED, 'natural'), ('log admissions', HOSP, 'log')):
    s = sel(seeds, target, scale).groupby(['name', 'seed']).score.mean().unstack()
    q = sel(seasons, target, scale).groupby(['name', 'season']).mean_wis.mean().unstack()
    k = 1e4 if target == ED else 1
    print(f'== {label}: child vs parent, seed-paired over both seasons; per season')
    for child, parent in pairs:
        common = s.columns[s.loc[child].notna() & s.loc[parent].notna()]
        d = (s.loc[child, common] - s.loc[parent, common]) * k
        pm = s.loc[parent, common].mean() * k
        print(f'{child:30s} {s.loc[child, common].mean()*k:8.4f} vs {pm:8.4f}  diff {d.mean()/pm*100:+5.1f}%  2SE {2*d.std(ddof=1)/np.sqrt(len(d))/pm*100:4.1f}%  n={len(d)}  '
              + '  '.join(f'{c}: {q.loc[child, c]*k:.4f} vs {q.loc[parent, c]*k:.4f}' for c in q.columns))
