"""Score saved flu forecasts by epidemic phase: does a model do worse, or lean low, around the peak? (flu search, 20 Nov 2026)

For every scored task (state or DC, reference date October-May, Hub horizon 0-3, target = flu admissions) the target
week's phase is set from that state's finalized season curve: 'rising' = more than 2 weeks before the season peak
week, 'peak' = within 2 weeks of it, 'falling' = more than 2 weeks after it. Per model, phase and horizon: WIS of
log(1 + admissions) (pinball form, 23 Hub levels; lower is better), bias = mean log((1 + median) / (1 + truth))
(positive = too high), 50% and 90% interval coverage.

    .venv/bin/python scripts/flu_phase_check.py RUN_FOLDER [RUN_FOLDER ...]   (run folders with eval_<season>/corrected)
    .venv/bin/python scripts/flu_phase_check.py --out tasks.csv RUN_FOLDER ...  also writes every scored task (COVID/RSV search)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LEVELS = np.array([.01, .025, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9, .95, .975, .99])
args = sys.argv[1:]
out = None
if args and args[0] == '--out':
    out, args = args[1], args[2:]
rows = []
for run in args:
    run = Path(run)
    for season_dir in sorted(run.glob('eval_*')):
        f = np.load(season_dir / 'corrected' / 'forecasts.npz')
        q, truth, mask = f['quantiles'][..., 0, :], f['truth'][..., 0, :], f['mask'][..., 0, :]  # [lev, iss, h, L], [iss, h, L]
        dates, locs = f['target_dates'], [str(l) for l in f['locations']]
        ref = f['context_end']
        # Season curve per location from the truth seen in this file (finalized labels), by target date.
        curve = {}
        for i in range(truth.shape[0]):
            for h in range(truth.shape[1]):
                for l in range(truth.shape[2]):
                    if mask[i, h, l]:
                        curve.setdefault(l, {})[dates[i, h]] = truth[i, h, l]
        peak = {l: max(c, key=c.get) for l, c in curve.items()}
        lq, lt = np.log1p(np.maximum(q, 0)), np.log1p(np.maximum(truth, 0))
        pin = np.where(lt[None] >= lq, LEVELS[:, None, None, None] * (lt[None] - lq), (1 - LEVELS[:, None, None, None]) * (lq - lt[None]))
        wis = 2 * pin.mean(0)
        for i in range(truth.shape[0]):
            month = int(str(ref[i])[5:7])
            if 6 <= month <= 9:
                continue
            for h in range(truth.shape[1]):
                for l, loc in enumerate(locs):
                    if loc == 'US' or not mask[i, h, l]:
                        continue
                    gap = (np.datetime64(dates[i, h]) - np.datetime64(peak[l])).astype(int) // 7
                    phase = 'rising' if gap < -2 else 'peak' if gap <= 2 else 'falling'
                    rows.append((run.name, season_dir.name[5:], loc, phase, h, wis[i, h, l], lq[11, i, h, l] - lt[i, h, l],
                                 lq[6, i, h, l] <= lt[i, h, l] <= lq[16, i, h, l], lq[3, i, h, l] <= lt[i, h, l] <= lq[19, i, h, l]))
d = pd.DataFrame(rows, columns=['model', 'season', 'location', 'phase', 'horizon', 'wis', 'bias', 'cov50', 'cov90'])
if out:
    d.to_csv(out, index=False)
pd.set_option('display.width', 250, 'display.max_rows', 200, 'display.max_columns', 20); d['model'] = d.model.str.replace(' [4 seeds]-mixture', '', regex=True).str.replace(' [4 seeds]-mixture', '', regex=False)
print('Tasks per phase:', d[d.model == d.model.iloc[0]].groupby('phase').size().to_dict())
print('\nBy phase (both seasons, all horizons):')
print(d.groupby(['phase', 'model'])[['wis', 'bias', 'cov50', 'cov90']].mean().round(4))
print('\nWIS by phase and horizon:')
print(d.pivot_table(index=['phase', 'horizon'], columns='model', values='wis').round(4))
print('\nBias by phase and horizon (log median - log truth):')
print(d.pivot_table(index=['phase', 'horizon'], columns='model', values='bias').round(3))
print('\nBy season and phase:')
print(d.pivot_table(index=['season', 'phase'], columns='model', values='wis').round(4))
