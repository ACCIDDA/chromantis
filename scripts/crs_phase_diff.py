"""Paired difference of two models' WIS by epidemic phase, with a bootstrap over locations (COVID/RSV search, 25 Nov 2026).

Reads the task table of scripts/flu_phase_check.py --out. For each phase: mean WIS of A and B over the same tasks, the
relative difference (B - A) / A, and a 95% interval from resampling locations (all of a location's tasks together),
so the peak-window rule ('not worse by more than the margin') can be applied with an uncertainty. Lower WIS is better.

    .venv/bin/python scripts/crs_phase_diff.py tasks.csv "prod4 [24 seeds]-mixture" "prodnat [24 seeds]-mixture"
"""
import sys

import numpy as np
import pandas as pd

d = pd.read_csv(sys.argv[1])
a, b = sys.argv[2], sys.argv[3]
key = ['season', 'location', 'phase', 'horizon']
w = d[d.model.isin([a, b])].pivot_table(index=key, columns='model', values='wis').dropna().reset_index()
rng = np.random.default_rng(20261125)
for phase, g in w.groupby('phase'):
    per = g.groupby('location')[[a, b]].agg(['sum', 'count'])
    locs = per.index.to_numpy()
    sa, sb, n = per[(a, 'sum')].to_numpy(), per[(b, 'sum')].to_numpy(), per[(a, 'count')].to_numpy()
    rel = sb.sum() / sa.sum() - 1
    boot = []
    for _ in range(2000):
        i = rng.integers(0, len(locs), len(locs))
        boot.append(sb[i].sum() / sa[i].sum() - 1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f'{phase:8s} tasks {int(n.sum()):5d}  A {sa.sum() / n.sum():.4f}  B {sb.sum() / n.sum():.4f}  '
          f'B vs A {rel * 100:+.1f}% (95% {lo * 100:+.1f}% to {hi * 100:+.1f}%)')
