"""Plot archived-input county comparisons with the actual MetroCast ensemble."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

folder = Path('output/metrocast')
individual = pd.concat([
    pd.read_csv(folder/'county-delay-ensemble-comparison.csv'),
    pd.read_csv(folder/'county-delay-refine-ensemble-comparison.csv')])
individual = individual[individual.evaluation_inputs.eq('archived')]
mixtures = pd.concat([
    pd.read_csv(folder/'county-delay-seed-mixtures.csv'),
    pd.read_csv(folder/'county-refine-seed-mixtures.csv')]).set_index('name')
chosen = [
    ('epochs80', '12-week history, 80 epochs\nShared weights, no location messages'),
    ('county_initial_12week_none_lag1', '12-week history, 160 epochs\nShared weights, no location messages'),
    ('county_initial_12week_attention_lag1', '12-week history, 160 epochs\nCross-county attention'),
    ('county_direct_52week_none_lag1', '52-week history, 320 epochs\nShared weights, no location messages')]
names, labels = zip(*chosen)
means = individual.groupby('name').location_mean_wis_ratio.mean().reindex(names)
pooled = mixtures.loc[list(names), 'location_mean_wis_ratio']
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(11, 6.8))
y = np.arange(len(names))
ax.barh(y-.17, means, .3, label='Mean score of four individual fits', color='#a4b4c7')
ax.barh(y+.17, pooled, .3, label='Equal-weight mixture of four fitted seeds', color='#147d92')
for i, (a, b) in enumerate(zip(means, pooled)):
    ax.text(a+.012, i-.17, f'{a:.3f}', va='center', fontsize=10)
    ax.text(b+.012, i+.17, f'{b:.3f}', va='center', fontsize=10)
ax.axvline(1, color='#a34636', linestyle='--', label='Actual MetroCast ensemble = 1')
ax.set(yticks=y, yticklabels=labels, xlim=(0, 1.13),
       xlabel='Mean of county WIS ratios to the actual ensemble · lower is better')
ax.invert_yaxis()
ax.legend(loc='lower right', fontsize=9)
fig.suptitle('Combining fitted seeds improves the archived-input county forecast', x=.03, ha='left', fontsize=16)
fig.text(.03, .9, 'Development benchmark: five Texas counties · 190 matched tasks · March 1–May 10, 2025 reference dates', fontsize=11)
fig.text(.03, .025,
         'All models trained on 2022–23/2023–24 revised county histories with the latest history week hidden;\n'
         'future county flu-ED proportion labels unchanged. Evaluation uses archived inputs available before the Wednesday deadline.\n'
         'Mixtures pool 512 intact draws per seed (2,048 total), then compute the same nine ensemble quantiles. No fitted mixture weights.\n'
         'The 12-week models use a width-128 logit MLP; the 52-week model uses a width-64 linear MLP. This is not reserved-season confirmation.',
         fontsize=9, linespacing=1.4)
fig.subplots_adjust(left=.31, right=.97, top=.83, bottom=.24)
fig.savefig(folder/'county-seed-mixtures-versus-ensemble.png', dpi=170)
print(folder/'county-seed-mixtures-versus-ensemble.png')
