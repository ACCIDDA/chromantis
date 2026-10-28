"""Archived-input county benchmark, separating training delay from spatial context."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

root = Path('output/metrocast')
files = ['metrocast-ensemble-comparison.csv', 'county-sharing-ensemble-comparison.csv',
         'county-delay-ensemble-comparison.csv', 'county-context-ensemble-comparison.csv']
data = pd.concat([pd.read_csv(root / f) for f in files])
data = data[data.evaluation_inputs.eq('archived')]
summary = data.groupby('name').location_mean_wis_ratio.agg(['mean', 'std', 'count'])
labels = ['Latest training week visible\nShared county weights',
          'Latest training week hidden\nShared county weights',
          'Latest training week hidden\n+ Cross-county attention',
          'Latest training week hidden\n+ Attention + Texas history',
          'Latest training week hidden\n+ Attention + Texas/region histories']
names = ['county_initial_12week', 'county_initial_12week_none_lag1',
         'county_initial_12week_attention_lag1', 'county_initial_12week_attention_state',
         'county_initial_12week_attention_state_regional']
table = summary.loc[names]
assert table['count'].eq(4).all()
fig, ax = plt.subplots(figsize=(12, 7.2))
ax.barh(range(len(names)), table['mean'], xerr=table['std'], capsize=4,
        color=['#8899aa', '#197f66', '#2b8f98', '#417bb0', '#665a99'])
ax.set_yticks(range(len(names)), labels)
ax.invert_yaxis()
for i, value in enumerate(table['mean']):
    ax.text(.035, i, f'{value:.3f}', color='white', weight='bold', va='center')
ax.axvline(1, linestyle='--', color='#a63530', label='Actual MetroCast ensemble = 1')
ax.set_xlim(0, 2.1)
ax.set_xlabel('Mean county WIS ratio versus ensemble: lower is better; error bars = SD across four seeds')
ax.spines[['top', 'right']].set_visible(False)
ax.legend(loc='lower right')
ax.set_title('Hiding the latest history week during training improves archived-input forecasts', pad=16)
fig.text(.025, .025,
         '12-week-history MLP, width 128, logit flu-ED output, 160 epochs; learned weights shared across five Texas counties.\n'
         'Train: 2022–23/2023–24 revised histories; future county flu-ED proportion labels unchanged. Only the stated history week is hidden.\n'
         'Texas and regional covariates also have a one-week fitting lag; region = unweighted AR/LA/NM/OK flu-ED mean, not a regional rate.\n'
         'Evaluate: strictly archived county inputs; state inputs use latest recorded cutoff before Wednesday 20:00 ET, usually previous issuance.\n'
         'Same 190 tasks, March 1–May 10 2025 reference dates, horizons 0–3, nine quantiles versus epiENGAGE-ensemble_mean.\n'
         'Travis, Dallas, El Paso, Harris and Bexar only. Four separate fitted seeds, not a model mixture. 2025–26 remains reserved.',
         fontsize=9, va='bottom')
fig.tight_layout(rect=(0, .25, 1, 1))
fig.savefig(root / 'county-delay-versus-ensemble.png', dpi=160)
print(root / 'county-delay-versus-ensemble.png')
