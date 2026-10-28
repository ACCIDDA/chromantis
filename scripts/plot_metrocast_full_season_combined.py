"""Development comparison of full-season MLP recipes and uniform seed mixtures."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
root=Path('output/metrocast')
files=['memory','direct-refine','combined-refine']
a=pd.concat([pd.read_csv(root/f'full-season-{f}-long-horizon.csv') for f in files])
b=pd.concat([pd.read_csv(root/f'full-season-{f}-seed-mixtures.csv') for f in files])
names=['direct_local_training_weekly_and_path_loss','geography0_lag0','no_embedding_path1_lag0','no_embedding_width128_path1_lag0','no_embedding_width128_path1_lag1']
labels=['Width 64, embeddings, path weight 0.25\nLatest training week visible','Width 64, no embeddings, path weight 0.25\nLatest training week visible','Width 64, no embeddings, path weight 1\nLatest training week visible','Width 128, no embeddings, path weight 1\nLatest training week visible','Width 128, no embeddings, path weight 1\nLatest training week hidden']
fig,axes=plt.subplots(1,2,figsize=(13,7),sharey=True)
y=np.arange(len(names))
for ax,metric in zip(axes,['WIS percentage points','Path energy percentage points']):
 d=a[a.horizons.eq('0-33') & a.metric.eq(metric)].groupby('name').value.agg(['mean','std','count']).loc[names]
 assert d['count'].eq(4).all()
 m=b[b.horizons.eq('0-33') & b.metric.eq(metric)].set_index('name').loc[names]
 ax.errorbar(d['mean'],y-.1,xerr=d['std'],fmt='o',capsize=3,color='#7b8590',label='Individual score mean ± seed SD')
 ax.scatter(m.value,y+.1,marker='D',color='#087f70',label='Equal four-seed intact-path mixture')
 for i,v in enumerate(m.value):ax.annotate(f'{v:.3f}',(v,i+.1),xytext=(5,-3),textcoords='offset points',fontsize=9)
 ax.set_xlabel(metric+'; lower is better');ax.grid(axis='x',alpha=.2)
 ax.spines[['top','right']].set_visible(False)
axes[0].set_yticks(y,labels,fontsize=9);axes[0].invert_yaxis();axes[1].legend(fontsize=8)
fig.suptitle('Full-season development: joint-path loss and location embeddings')
fig.text(.02,.025,'All models: direct 52-week linear-output MLP, 320 epochs, batch 2, 16 training draws, original Hub own-state history.\n'
 'Train on revised 2022–23/2023–24 local histories and unchanged future local flu-ED proportion labels.\n'
 'Training-gap treatment hides only the latest target-history week during fitting/inner validation; evaluation inputs are unchanged.\n'
 'Evaluate revised histories at October 26 and November 2/9/16, 2024, all 34 weeks through June 14, 2025; equal location weighting.\n'
 'Individual models: 128 intact paths/origin; mixtures: 128 paths per seed, 512 total, quantiles computed after pooling whole paths.\n'
 'Development only: no actual MetroCast ensemble comparison, no archived-input claim, and no 2025–26 tuning.',fontsize=9)
fig.tight_layout(rect=(0,.23,1,.95))
path=root/'full-season-combined-refinement.png';fig.savefig(path,dpi=150);print(path)
