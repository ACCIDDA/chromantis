"""Compare development full-path scores, preserving seed versus mixture meanings."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

root = Path('output/metrocast')
parser = argparse.ArgumentParser()
parser.add_argument('--peaks', action='store_true')
peaks = parser.parse_args().peaks
single = pd.concat([
    pd.read_csv(root/'full-season-memory-long-horizon.csv'),
    pd.read_csv(root/'full-season-direct-refine-long-horizon.csv')])
mixture = pd.concat([
    pd.read_csv(root/'full-season-memory-seed-mixtures.csv'),
    pd.read_csv(root/'full-season-direct-refine-seed-mixtures.csv')])
names = ['direct_local_training_weekly_and_path_loss', 'geography0_lag0',
         'width128_lag0', 'pathweight1_lag0', 'county_recipe_34weeks_lag0']
labels = ['52-week MLP: width 64,\nlocation embeddings, path weight 0.25',
          'Same model: no\nlocation embeddings',
          'Same baseline: width 128',
          'Same baseline: path weight 1',
          '12-week logit MLP: width 128,\n80 epochs, no location embeddings']
fig, axes = plt.subplots(1, 2, figsize=(13, 7), sharey=True)
y = np.arange(len(names))
metrics = ['Peak size WIS percentage points', 'Peak timing WIS weeks'] if peaks else ['WIS percentage points', 'Path energy percentage points']
titles = ['Forecast peak size', 'Forecast peak timing'] if peaks else ['34-week marginal WIS', '34-week joint-path energy']
for ax, metric, title in zip(axes, metrics, titles):
    a = single[single.metric.eq(metric) & (single.horizons.eq('observed-season-window') if peaks else single.horizons.eq('0-33'))]
    a = a.groupby('name').value.agg(['mean', 'std', 'count']).loc[names]
    assert a['count'].eq(4).all()
    b = mixture[mixture.metric.eq(metric) & (mixture.horizons.eq('observed-season-window') if peaks else mixture.horizons.eq('0-33'))].set_index('name').loc[names]
    ax.errorbar(a['mean'], y-.12, xerr=a['std'], fmt='o', color='#788692',
                capsize=3, label='Mean individual score ± seed SD')
    ax.scatter(b.value, y+.12, marker='D', color='#087f70', label='Equal four-seed trajectory mixture')
    for i, v in enumerate(b.value):
        ax.annotate(f'{v:.3f}', (v, i+.12), xytext=(5, -3),
                    textcoords='offset points', fontsize=9, color='#087f70')
    ax.set_title(title)
    ax.set_xlabel(('Weeks' if metric.endswith('weeks') else 'Percentage points')+'; lower WIS is better' if peaks else 'Percentage points; lower is better')
    ax.grid(axis='x', alpha=.2)
    ax.spines[['top', 'right']].set_visible(False)
axes[0].set_yticks(y, labels, fontsize=9)
axes[0].invert_yaxis()
axes[1].legend(loc='lower right', fontsize=8)
fig.suptitle('Peak forecasts from intact full-season trajectories' if peaks else 'Full-season development: removing location embeddings helps the seed mixture')
fig.text(.025, .025,
         'All models train on revised 2022–23/2023–24 local flu-ED histories and unchanged future local flu-ED proportion labels.\n'
         'All use own-state Hub history; latest target-history training week remains visible. No transfer pretraining.\n'
         'Baseline: 52-week linear-output MLP, width 64, 320 epochs, batch 2, 16 training draws, weekly + path loss (weight 0.25).\n'
         'Evaluate revised inputs at October 26 and November 2/9/16, 2024; all 34 horizons, with labels through June 14, 2025.\n' +
         ('Peaks: maximum and earliest maximizing week through June 14; complete observed windows only (360 across 90 locations).\n' if peaks else
          'Equal weighting across observed locations; individual fits use 128 intact paths, mixtures pool 128 per seed (512 paths).\n') +
         ('Equal location weighting; 128 paths per seed, 512 per mixture. Timing WIS is a distribution score, not mean timing error.\n' if peaks else '') +
         'Development only: no MetroCast ensemble comparison, no archived-input performance claim, and no 2025–26 selection.',
         fontsize=9)
fig.tight_layout(rect=(0, .25, 1, .94))
output = root/('full-season-peak-diagnostics.png' if peaks else 'full-season-refinement.png')
fig.savefig(output, dpi=150)
print(output)
