"""Summarize ebola_noise_backtest.py: mean WIS by window, training noise, test inputs; forecast response to the newest week.

    .venv/bin/python scripts/ebola_noise_summary.py output/ebola-noise-backtest
"""
import sys
from pathlib import Path

import pandas as pd

folder = Path(sys.argv[1])
s = pd.concat(pd.read_csv(f) for f in folder.glob('scores-*.csv'))
k = pd.concat(pd.read_csv(f) for f in folder.glob('slopes-*.csv'))
pd.set_option('display.width', 220)
level = {'local': 'health zone / district', 'middle': 'province / country', 'top': 'outbreak total'}
s['level'] = s.level.map(level)
for scale in ('natural', 'log'):
    t = s[s.scale == scale].pivot_table(index=['inputs', 'level', 'fold'], columns='train_noise', values='wis', aggfunc='mean')
    t['ratio 0.5/0'], t['ratio 1/0'] = t[.5] / t[0.], t[1.] / t[0.]
    print(f'\nMean WIS, {scale} scale (lower is better); columns = training noise strength\n', t.round(3).to_string())
    a = s[s.scale == scale].pivot_table(index=['inputs', 'level'], columns='train_noise', values='wis', aggfunc='mean')
    print('\nAll windows pooled\n', (a.div(a[0.], axis=0)).round(3).to_string())
r = k.pivot_table(index=['fold'], columns=['train_noise', 'horizon'], values='slope', aggfunc='mean')
print('\nResponse of the outbreak-total forecast to the newest input week (log-log slope over 50 noisy copies; 1 = follows it one for one)\n',
      r.round(2).to_string())
print('\nAll windows\n', k.groupby(['train_noise', 'horizon']).slope.mean().unstack().round(2).to_string())
