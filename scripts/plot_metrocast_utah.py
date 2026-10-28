"""Provisional Utah-only full-season development results; no ensemble comparison."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
root=Path('output/metrocast')
a=pd.read_csv(root/'utah-proposed-long-horizon.csv');b=pd.read_csv(root/'utah-proposed-seed-mixtures.csv')
names=[f'mlp{arch}_{spatial}_lag{lag}' for arch in ['52_linear_320epochs','12_logit_80epochs'] for spatial in ['none','attention'] for lag in [0,1]]
labels=[f'{history}-week {output}, width {width}, {epochs} epochs\n{spatial}; latest fitting week {gap}' for history,output,width,epochs in [(52,'linear',64,320),(12,'logit',128,80)] for spatial in ['shared weights only','cross-location attention'] for gap in ['visible','hidden']]
fig,axes=plt.subplots(1,2,figsize=(14,9),sharey=True)
y=np.arange(8)
for ax,metric in zip(axes,['WIS percentage points','Path energy percentage points']):
 d=a[a.horizons.eq('0-33') & a.metric.eq(metric)].groupby('name').value.agg(['mean','std','count']).loc[names]
 assert d['count'].eq(4).all()
 m=b[b.horizons.eq('0-33') & b.metric.eq(metric)].set_index('name').loc[names]
 ax.errorbar(d['mean'],y-.12,xerr=d['std'],fmt='o',capsize=3,color='#7c8792',label='Mean individual score ± seed SD')
 ax.scatter(m.value,y+.12,color='#087f70',marker='D',label='Equal four-seed intact-path mixture')
 for i,v in enumerate(m.value):ax.annotate(f'{v:.3f}',(v,i+.12),xytext=(5,-3),textcoords='offset points',fontsize=8)
 ax.set_xlabel(metric+'; lower is better');ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False)
axes[0].set_yticks(y,labels,fontsize=9);axes[0].invert_yaxis();axes[1].legend(loc='lower right',fontsize=8)
fig.suptitle('Provisional Utah weekly targets: 34-week forecasts across 13 districts and the state')
fig.text(.02,.025,'All models train on revised 2022–23/2023–24 Utah histories and unchanged future local influenza ED proportion labels.\n'
 'Shared weights, no location embeddings or external covariates; batch 2, 16 training draws, weekly + native-path loss (weight 0.25).\n'
 'The gap hides only the latest target-history week during fitting/inner validation; future labels and evaluation histories stay unchanged.\n'
 'Evaluate revised inputs at October 26 and November 2/9/16, 2024; 34 weeks through June 14, 2025.\n'
 'Equal weighting of 14 locations includes statewide/district overlap. Individual: 128 intact draws; mixture: 512, equal contributions.\n'
 'Source: proposed weekly Hub data from unmerged PR587, pinned head 747e910; not dashboard seven-day averages.\n'
 'Development only: no archived-input or MetroCast ensemble claim, no 2025–26 tuning, no comparison with the separate main panel.',fontsize=9)
fig.tight_layout(rect=(0,.22,1,.95));path=root/'utah-proposed-full-season.png';fig.savefig(path,dpi=150);print(path)
