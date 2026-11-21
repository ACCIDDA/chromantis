"""Summary figure of the flu search (experiments/flu-search-20261120): B7 against the candidate mixtures.

Mixtures are equal weight per recipe, 32 seeds per recipe (24 for Ar.peak.nokinsa), scored by the planner's ensemble
ranking: flu-mix-m32 (2024-25 and 2025-26 held out in turn, archived Wednesday reports), flu-mix-g32 (2023-24 held out,
artificial reports). WIS over the 50 states and DC, lower is better. Run in the Longleaf campaign folder; writes
output/flu-search/summary.png.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

NAMES = {'B7': 'B7 (submitted design,\nrefit leak-free)', 'A': 'A: sampled Bq + B_width256\n+ Ar.peak',
         'A_nokinsa': 'A without Kinsa', 'B': 'B: all sampled\n(Bh.smp instead of B_width256)'}
COLORS = {'B7': '#8a8a85', 'A': '#2a78d6', 'A_nokinsa': '#1baf7a', 'B': '#eb6834'}
rows = []
for tag in ('m32', 'g32'):
    s = pd.read_csv(f'data/experiments/flu-mix-{tag}/ranking/headline-season-scores.csv')
    s = s[s.deployed & (s.geography == 'states_dc')]
    s['key'] = s.name.str.split(' \\[').str[0]
    rows.append(s)
s = pd.concat(rows)
s = s[s.key.isin(NAMES)]
adm = s[(s.target == 'wk inc flu hosp') & (s.scale == 'log')].pivot_table(index='key', columns='season', values='mean_wis')
ed = s[(s.target == 'wk inc flu prop ed visits') & (s.scale == 'natural')].pivot_table(index='key', columns='season', values='mean_wis') * 1e4
k = pd.read_csv('data/experiments/flu-mix-m32/ranking/headline-rankings.csv')
k = k[k.deployed & (k.scale == 'log') & (k.geography == 'states_dc') & (k.target == 'wk inc flu hosp')]
k['key'] = k.name.str.split(' \\[').str[0]
october = k.set_index('key').october
peak = pd.Series({'B7': 0.3227, 'A': 0.3107, 'A_nokinsa': 0.3156, 'B': 0.3288})  # scripts/flu_phase_check.py on flu-mix-m32
order = ['B7', 'A', 'A_nokinsa', 'B']
seasons = ['2024-2025', '2025-2026', '2023-2024']
labels = ['2024-25\n(archived reports)', '2025-26\n(archived reports)', '2023-24\n(artificial reports)']
fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), gridspec_kw=dict(width_ratios=[3, 3, 2]))
for ax, table, title in ((axes[0], adm, 'Flu admissions: WIS of log(1 + admissions)'),
                         (axes[1], ed, 'ED share: WIS x 10,000')):
    x = np.arange(len(seasons))
    w = .2
    for i, key in enumerate(order):
        v = table.loc[key, seasons].values
        ax.bar(x + (i - 1.5) * w, v, w * .9, color=COLORS[key], label=NAMES[key])
    ax.set_xticks(x, labels)
    ax.set_title(title, fontsize=11)
    lo = np.nanmin(table.loc[order, seasons].values)
    ax.set_ylim(lo * .9, np.nanmax(table.loc[order, seasons].values) * 1.03)
    ax.grid(axis='y', color='#e5e5e0'); ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
ax = axes[2]
x = np.arange(2)
for i, key in enumerate(order):
    ax.bar(x + (i - 1.5) * .2, [peak[key], october[key]], .18, color=COLORS[key])
ax.set_xticks(x, ['Peak window\n(within 2 weeks of\neach state\'s maximum)', 'October\nreference dates'])
ax.set_title('Log-admission WIS by phase\n(2024-25 and 2025-26)', fontsize=11)
ax.set_ylim(.25, .52); ax.grid(axis='y', color='#e5e5e0'); ax.set_axisbelow(True)
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
axes[0].legend(loc='upper center', bbox_to_anchor=(1.3, -0.17), ncol=4, frameon=False, fontsize=9.5)
fig.suptitle('Flu search, 20-21 Nov 2026: candidate mixtures against B7 (lower is better; 32 seeds per recipe; '
             'no 2026-27 data)', fontsize=12)
fig.tight_layout(rect=(0, .02, 1, .95))
fig.savefig('output/flu-search/summary.png', dpi=140, bbox_inches='tight')
print('wrote output/flu-search/summary.png')
