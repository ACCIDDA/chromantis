"""Figure for scripts/live_nowcast_decomposition.py: US admissions, nowcast vs growth error per issuance."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

out = Path(sys.argv[1] if len(sys.argv) > 1 else 'output/live-decomposition')
BLUE, ORANGE, INK, MUTED = '#2a78d6', '#eb6834', '#1a1a19', '#8a8980'
fig, axes = plt.subplots(2, 3, figsize=(13, 6.6), sharey='row', constrained_layout=True)
for row, hub in enumerate(('rsv', 'covid')):
    s = pd.read_csv(out / f'{hub}-summary.csv', header=[0, 1], index_col=[0, 1, 2])['US admissions (log ratio)']
    s = s.dropna(how='all').reset_index()
    s = s[s.target.str.endswith('hosp')]
    pct = lambda x: 100 * (np.exp(x) - 1)
    iss = sorted(s.issuance.unique()); x = np.arange(len(iss)); lab = [i[5:] for i in iss]
    h0 = s[s.horizon == 0].set_index('issuance').reindex(iss)
    ax = axes[row, 0]
    ax.plot(x, pct(h0.report_shortfall), 'o-', color=BLUE, lw=2, ms=8, label='as first reported')
    ax.plot(x, pct(h0.nowcast_error), 'o-', color=ORANGE, lw=2, ms=8, label='after the trees\' correction')
    ax.set_title(f'{hub.upper()}: newest reported week vs truth so far', fontsize=10, color=INK, loc='left')
    ax.set_ylabel('% above truth (US, sum of states)', color=INK)
    for h, ax in zip((0, 1), axes[row, 1:]):
        d = s[s.horizon == h].set_index('issuance').reindex(iss)
        ax.bar(x - 0.19, pct(d.nowcast_error), 0.36, color=BLUE, label='nowcast error', edgecolor='white', lw=2)
        ax.bar(x + 0.19, d.growth_error.pipe(pct), 0.36, color=ORANGE, label='growth error', edgecolor='white', lw=2)
        ax.plot(x, pct(d.total_error), 'D', color=INK, ms=7, label='submitted median vs truth (total)')
        ax.set_title(f'{hub.upper()}: submitted US median, horizon {h}', fontsize=10, color=INK, loc='left')
    for ax in axes[row]:
        ax.axhline(0, color=MUTED, lw=1); ax.set_xticks(x, lab, fontsize=8)
        ax.grid(axis='y', color='#e6e5e0', lw=0.8); ax.set_axisbelow(True)
        for side in ('top', 'right'): ax.spines[side].set_visible(False)
    axes[row, 0].legend(frameon=False, fontsize=8, loc='lower right')
    axes[row, 2].legend(frameon=False, fontsize=8, loc='upper left')
for ax in axes[1]: ax.set_xlabel('issuance (Wednesday report)', color=INK)
fig.suptitle('Live 2026-27 forecasts: the excess is in the forecast rise, not the nowcast. Truth = Hub target data as of '
             '18 Nov 2026 (newest weeks still revised up). COVID files exist from the 4 Nov issuance only.', fontsize=9, color=INK)
fig.savefig(out / 'live-decomposition.png', dpi=150)
print(out / 'live-decomposition.png')
