"""Summary figure of the flu search (experiments/flu-search-20261120): B7 against the recommended masked candidate A.

Equal-weight mixtures, 48 seeds per recipe, scored by the planner's ensemble ranking (flu-mix-fm48: 2024-25 and 2025-26
held out in turn, archived Wednesday reports; flu-mix-fgm48: 2023-24 held out, artificial reports; flu-mix-st48: the
same fits with every location's newest admission week removed at the deadline). Phases from scripts/flu_phase_check.py.
WIS over the 50 states and DC, lower is better. Run in the Longleaf campaign folder; writes output/flu-search/summary.png.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

KEYS = ['B7', 'A_masked']
NAMES = {'B7': 'B7 (submitted design, refit leak-free)', 'A_masked': 'Candidate A, masked: sampled Bq + B_width256 + Ar.peak (no Kinsa)'}
COLORS = {'B7': '#8a8a85', 'A_masked': '#2a78d6'}


def scores(tag):
    s = pd.read_csv(f'data/experiments/flu-mix-{tag}/ranking/headline-season-scores.csv')
    s = s[s.geography == 'states_dc']
    s['key'] = s.name.str.split(' \\[').str[0]
    return s


s = pd.concat([scores('fm48'), scores('fgm48')])
s = s[s.deployed]
adm = s[(s.target == 'wk inc flu hosp') & (s.scale == 'log')].pivot_table(index='key', columns='season', values='mean_wis')
ed = s[(s.target == 'wk inc flu prop ed visits') & (s.scale == 'natural')].pivot_table(index='key', columns='season', values='mean_wis') * 1e4
st = scores('st48')
st = st[(st.target == 'wk inc flu hosp') & (st.scale == 'log')].groupby(['key', 'history']).mean_wis.mean().unstack()
k = pd.read_csv('data/experiments/flu-mix-fm48/ranking/headline-rankings.csv')
k = k[k.deployed & (k.scale == 'log') & (k.geography == 'states_dc') & (k.target == 'wk inc flu hosp')]
k['key'] = k.name.str.split(' \\[').str[0]
october = k.set_index('key').october
phase = {'B7': {'rising': 0.3385, 'peak': 0.3186, 'falling': 0.2561}, 'A_masked': {'rising': 0.3152, 'peak': 0.3123, 'falling': 0.2470}}
seasons = ['2024-2025', '2025-2026', '2023-2024']
slabels = ['2024-25\n(archived)', '2025-26\n(archived)', '2023-24\n(artificial)']
fig, axes = plt.subplots(1, 4, figsize=(18, 4.6), gridspec_kw=dict(width_ratios=[3, 3, 4, 2]))


def bars(ax, groups, labels, title, ylim=None):
    x = np.arange(len(labels))
    for i, key in enumerate(KEYS):
        v = [groups[key][g] for g in range(len(labels))]
        ax.bar(x + (i - .5) * .38, v, .34, color=COLORS[key], label=NAMES[key])
    ax.set_xticks(x, labels, fontsize=9)
    ax.set_title(title, fontsize=10.5)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(axis='y', color='#e5e5e0'); ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)


bars(axes[0], {k: adm.loc[k, seasons].values for k in KEYS}, slabels, 'Flu admissions: WIS of log(1 + admissions)', (.24, .33))
bars(axes[1], {k: ed.loc[k, seasons].values for k in KEYS}, slabels, 'ED share: WIS x 10,000', (30, 52))
bars(axes[2], {k: [phase[k]['rising'], phase[k]['peak'], phase[k]['falling'], october[k]] for k in KEYS},
     ['Rising', 'Peak window\n(±2 weeks)', 'Falling', 'October\nreference dates'],
     'Log-admission WIS by epidemic phase\n(2024-25 and 2025-26)', (.2, .52))
bars(axes[3], {k: [st.loc[k, 'corrected'], st.loc[k, 'delayed']] for k in KEYS}, ['Normal\ninputs', 'Newest week\nmissing'],
     'Robustness: newest admission\nweek missing at the deadline', (.25, .38))
axes[0].legend(loc='upper center', bbox_to_anchor=(2.3, -0.2), ncol=2, frameon=False, fontsize=10)
fig.suptitle('Flu search, 20-22 Nov 2026: recommended mixture against B7 (lower is better; 48 seeds per recipe; no 2026-27 data)',
             fontsize=12)
fig.tight_layout(rect=(0, .03, 1, .95))
fig.savefig('output/flu-search/summary.png', dpi=140, bbox_inches='tight')
print('wrote output/flu-search/summary.png')
