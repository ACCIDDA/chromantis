"""Figure for scripts/live_decomposition_fits.py: US nowcast vs growth error by horizon, per recipe."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

out = Path(sys.argv[1] if len(sys.argv) > 1 else 'output/live-decomposition')
INK, MUTED, GRID = '#1a1a19', '#8a8980', '#e6e5e0'
COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']
LABEL = {'ref.Bw': 'Bw (submitted recipe, refit)', 'ref.A4c0': 'A4c0 (submitted recipe, refit)', 'Bw.national': 'Bw + US-only summary',
         'A4c0.national': 'A4c0 + US-only summary', 'A4c0.national.rsvnet.calendar.weeks1': 'candidate: A4c0 + US summary + RSV-NET + calendar, 1-week trees',
         'ref.pN_gru': 'GRU, US summary (submitted recipe, refit)', 'ref.Bh_wd': 'Bh_wd (submitted recipe, refit)', 'ref.Ah': 'Ah sampled (submitted recipe, refit)',
         'T.pN_gru.real.log_loss1': 'candidate: GRU + real-pair trees, log-loss 1', 'T.pN_gru.real.log_loss1.attention': 'candidate partner: same, attention encoder'}
fig, axes = plt.subplots(2, 2, figsize=(13, 7.5), constrained_layout=True)
for row, hub in enumerate(('rsv', 'covid')):
    s = pd.read_csv(out / f'{hub}-fits-summary.csv')
    pct = lambda x: 100 * (np.exp(x) - 1)
    recipes = list(dict.fromkeys(s.recipe))
    ax = axes[row, 0]
    h0 = s[s.horizon == 0].set_index('recipe').reindex(recipes)
    y = np.arange(len(recipes))
    ax.barh(y + 0.2, pct(h0.report_shortfall), 0.38, color=MUTED, label='as first reported')
    ax.barh(y - 0.2, pct(h0.nowcast_error), 0.38, color=COLORS[0], label="after the fit's own trees (nowcast error)")
    ax.set_yticks(y, [LABEL.get(r, r) for r in recipes], fontsize=8); ax.invert_yaxis()
    ax.set_title(f'{hub.upper()}: newest reported week, US, vs truth', fontsize=10, color=INK, loc='left')
    ax.set_xlabel('% above truth', color=INK); ax.legend(frameon=False, fontsize=8, loc='lower right')
    ax = axes[row, 1]
    for k, r in enumerate(recipes):
        g = s[s.recipe == r].sort_values('horizon')
        ax.plot(g.horizon, pct(g.growth_error), 'o-', color=COLORS[k % len(COLORS)], lw=2, ms=8, label=LABEL.get(r, r))
    ax.set_xticks([0, 1, 2, 3]); ax.set_xlabel('Hub horizon (weeks after the reference date)', color=INK)
    ax.set_ylabel('growth error, % (forecast rise vs actual rise)', color=INK)
    ax.set_title(f'{hub.upper()}: error of the forecast rise from the corrected newest week, US', fontsize=10, color=INK, loc='left')
    ax.legend(frameon=False, fontsize=7.5, loc='upper left')
    for ax in axes[row]:
        ax.axvline(0, color=MUTED, lw=1) if ax is axes[row, 0] else ax.axhline(0, color=MUTED, lw=1)
        ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
        for side in ('top', 'right'): ax.spines[side].set_visible(False)
fig.suptitle('All-season fits (trained on 2022-23..2025-26, finalized labels as of 12 Nov 2026) run on the 2026-27 reports of 14 Oct-4 Nov; '
             'truth = Hub target data as of 18 Nov (newest weeks still revised up). Mean over reports and 4-20 seeds.', fontsize=9, color=INK)
fig.savefig(out / 'live-decomposition-fits.png', dpi=150)
print(out / 'live-decomposition-fits.png')
