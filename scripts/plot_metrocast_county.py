"""Plot the actual ensemble comparison, with archived inputs and explicit training setup."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

root = Path('output/metrocast')
data = pd.concat([pd.read_csv(root / f) for f in
                  ['metrocast-ensemble-comparison.csv', 'county-sharing-ensemble-comparison.csv']])
data = data[data.evaluation_inputs.eq('archived')]
fig, axes = plt.subplots(1, 2, figsize=(12, 6.2), sharey=True)
for ax, prefix, title in zip(axes, ['county_initial_12week', 'county_direct_52week'],
                             ['12-week-history MLP', '52-week-history MLP']):
    names = [prefix, prefix + '_pooled', prefix + '_attention']
    table = data.groupby('name').location_mean_wis_ratio.agg(['mean', 'std', 'count']).loc[names]
    assert table['count'].eq(4).all()
    ax.bar(range(3), table['mean'], yerr=table['std'], capsize=4, color=['#8297a5', '#3e8fa3', '#2d668b'])
    for i, value in enumerate(table['mean']):
        ax.text(i, .08, f'{value:.2f}', ha='center', color='white', fontsize=12, weight='bold')
    ax.axhline(1, color='#a63530', linestyle='--', label='MetroCast ensemble = 1')
    ax.set_xticks(range(3), ['Shared weights\nonly', '+ Pooled county\ncontext', '+ Cross-county\nattention'])
    ax.set_title(title)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_ylim(0, 2.8)
axes[0].set_ylabel('WIS ratio versus actual MetroCast ensemble\nLower is better; bars are four-seed means')
axes[1].legend(loc='upper left')
fig.suptitle('Sharing county information helps one architecture, but neither beats the ensemble', fontsize=13)
fig.text(.02, .025,
         'All models share weights across Travis, Dallas, El Paso, Harris and Bexar counties, Texas.\n'
         'Train: revised 2022–23/2023–24 county histories; future county flu-ED proportion labels; no state covariates or simulated delay.\n'
         'Evaluate: archived histories available by each Wednesday; reference dates March 1–May 10, 2025; horizons 0–3.\n'
         'Same 190 observed tasks and nine quantiles as epiENGAGE-ensemble_mean. Mean of county WIS ratios; error bars are seed SD.\n'
         'Four separately trained seeds, not an ensemble of our models. The 2025–26 confirmation season is untouched.',
         fontsize=9, va='bottom')
fig.tight_layout(rect=(0, .23, 1, .94))
fig.savefig(root / 'county-sharing-versus-ensemble.png', dpi=150)
print(root / 'county-sharing-versus-ensemble.png')
