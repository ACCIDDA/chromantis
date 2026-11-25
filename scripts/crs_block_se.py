"""Seed standard error of mixture differences from disjoint 8-seed blocks (COVID/RSV search, 25 Nov 2026).

Reads crs-mix-{cb,cgb,rb,rgb}1..4 (mixtures rebuilt on seeds 44-51, 52-59, 60-67, 68-75); prints each block's relative
difference to the production mixture, their mean and 2 x the standard error of that mean (block sd x 2 / sqrt(number of blocks)). Lower is better.

    python3 scripts/crs_block_se.py   (in the Longleaf campaign folder)
"""
import csv, sys, numpy as np
from pathlib import Path
def score(tag, ed=False):
    out = {}
    f = Path(f'data/experiments/crs-mix-{tag}/ranking/headline-season-scores.csv')
    if not f.exists(): return None
    for r in csv.DictReader(open(f)):
        if r['geography'] != 'states_dc' or r['history'] != 'corrected': continue
        if ed and 'ed visits' in r['target'] or (not ed and r['scale'] == 'log' and 'hosp' in r['target']):
            out.setdefault(r['name'].split(' [')[0], []).append(float(r['mean_wis']))
    return {k: np.mean(v) for k, v in out.items()}
for label, tags, ed, base in (('COVID main log adm', 'cb', False, 'prod4'), ('COVID guard log adm', 'cgb', False, 'prod4'),
                              ('COVID guard ED', 'cgb', True, 'prod4'), ('RSV main log adm', 'rb', False, 'prod4'),
                              ('RSV guard ED', 'rgb', True, 'prod4')):
    blocks = [b for b in (score(f"{tags}{i}", ed) for i in range(1, 6)) if b is not None]
    if len(blocks) < 2: print(label, "missing"); continue
    print('==', label)
    for m in blocks[0]:
        if m == base: continue
        d = np.array([b[m] / b[base] - 1 for b in blocks]) * 100
        print(f'  {m:10s} blocks {np.round(d, 2)}  mean {d.mean():+.2f}%  2SE {2 * d.std(ddof=1) / np.sqrt(len(d)):.2f}%')
