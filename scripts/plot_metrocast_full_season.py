"""Full-season development metrics with explicit model and input treatment."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

root=Path('output/metrocast')
p=pd.read_csv(root/'full-season-memory-long-horizon.csv')
p=p[p.horizons.eq('0-33')]
names=['direct_local_training_weekly_loss','direct_local_training_weekly_and_path_loss',
       'ILI_pretraining_weekly_loss','ILI_pretraining_weekly_and_path_loss']
labels=['Direct local\nWeekly loss','Direct local\nWeekly + path loss',
        'State ILI pretraining\nWeekly loss','State ILI pretraining\nWeekly + path loss']
fig,axes=plt.subplots(1,2,figsize=(12,6))
for ax,metric in zip(axes,['WIS percentage points','Path energy percentage points']):
 t=p[p.metric.eq(metric)].groupby('name').value.agg(['mean','std','count']).loc[names]
 assert t['count'].eq(4).all()
 ax.bar(range(4),t['mean'],yerr=t['std'],capsize=3,color=['#7d96a4','#147f68','#8b7aad','#5d4984'])
 ax.set_xticks(range(4),labels,fontsize=9)
 ax.set_ylabel(metric+'; lower is better')
 ax.set_ylim(0,t['mean'].max()+t['std'].max()+.3)
 for i,value in enumerate(t['mean']): ax.text(i,.05,f'{value:.3f}',ha='center',color='white',weight='bold')
 ax.spines[['top','right']].set_visible(False)
fig.suptitle('34-week forecasts: direct training with joint-path loss leads the completed candidates')
fig.text(.025,.025,
 'Train: local 2022–23/2023–24 flu-ED proportion histories and future labels; revised inputs with own-state history.\n'
 'Direct MLP: 52-week context, width 64, 320 epochs. ILI MLP: 12-week context, width 128, logit outputs, 160 epochs;\n'
 '800 pretraining updates on 2010–11 through 2021–22 state ILI, scaled using fitting data only. Architectures also differ.\n'
 'All: batch size 2, 16 training draws; path-loss weight 0 or 0.25. No simulated target-history gap in these fits.\n'
 'Evaluate: revised inputs at October 26 and November 2/9/16, 2024; horizons 0–33, labels through June 14, 2025.\n'
 'Equal weighting across observed locations in the 90-location panel; 128 intact draws for path energy; bars = four-seed mean ± SD.\n'
 'No MetroCast ensemble comparison here. State-ED transfer omitted because seeds remain incomplete. 2025–26 stays reserved.',fontsize=9)
fig.tight_layout(rect=(0,.3,1,.94))
fig.savefig(root/'full-season-development.png',dpi=150)
print(root/'full-season-development.png')
