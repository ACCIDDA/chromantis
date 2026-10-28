"""California winter pilot: individual fits and uniform whole-path seed mixtures."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
root=Path('output/metrocast')
a=pd.read_csv(root/'california-winter-scores.csv')
b=pd.read_csv(root/'california-development-seed-mixtures.csv')
names=[f'{pre}_historylag{lag}_path{weight}' for pre in ['direct','ILI_pretraining'] for lag in [0,1] for weight in ['0','0.25']]
labels=[f'{pre}; latest fitting week {gap}\nPath-loss weight {weight}' for pre in ['Direct training','Historical state ILI pretraining'] for gap in ['visible','hidden'] for weight in ['0','0.25']]
p=argparse.ArgumentParser();p.add_argument('--sharing',action='store_true');args=p.parse_args()
if args.sharing:
 a=pd.concat([a,pd.read_csv(root/'california-sharing-winter-scores.csv')])
 b=pd.concat([b,pd.read_csv(root/'california-sharing-seed-mixtures.csv')])
 names=[name for pre in ['direct','ILI_pretraining'] for name in
        [f'{pre}_historylag1_path0',f'california_{pre}_attention_lag1',f'california_{pre}_pooled_lag1']]
 labels=[f'{pre}; latest fitting week hidden\n{scope}' for pre in ['Direct training','Historical state ILI pretraining']
         for scope in ['Shared weights, no messages','Attention across regions and state','Pooled histories across regions and state']]
fig,axes=plt.subplots(1,2,figsize=(14,9),sharey=True);y=np.arange(len(names))
for ax,metric in zip(axes,['WIS admission counts','Path energy log1p counts']):
 d=a[a.horizons.eq('0-33') & a.metric.eq(metric)].groupby('name').value.agg(['mean','std','count']).loc[names]
 assert d['count'].eq(4).all()
 m=b[b.horizons.eq('0-33') & b.metric.eq(metric)].set_index('name').loc[names]
 ax.errorbar(d['mean'],y-.12,xerr=d['std'],fmt='o',capsize=3,color='#7c8792',label='Mean individual score ± seed SD')
 ax.scatter(m.value,y+.12,color='#087f70',marker='D',label='Equal four-seed intact-path mixture')
 for i,v in enumerate(m.value):ax.annotate(f'{v:.2f}',(v,i+.12),xytext=(5,-3),textcoords='offset points',fontsize=8)
 ax.set_xlabel(metric+'; lower is better');ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False)
axes[0].set_yticks(y,labels,fontsize=9);axes[0].invert_yaxis();axes[1].legend(loc='lower right',fontsize=8)
fig.suptitle('California winter development: '+('cross-location history sharing, weekly loss only' if args.sharing else 'published partial admission sums'))
fig.text(.02,.025,'All models: 12-week MLP, width 64, 160 epochs, batch 2, 16 training draws, fourth-root count transform; shared weights, no covariates.\n'
 'Train July 6, 2024–January 25, 2025 on revised histories and future published sums over nonmissing age groups. Duplicate weeks masked.\n'
 'ILI treatment: 600 pretraining updates using pre-August 2022 California state ILI, broadcast to regions and fitting-only scaled into pseudocounts.\n'
 'The fitting gap hides only the latest target-history week during fitting/inner validation; future admission labels and evaluation inputs stay unchanged.\n'
 'Evaluate revised inputs February 1–June 14, 2025. Score available horizons only: no labels at horizons 26–33; not full-season validation.\n'
 'Equal weighting of overlapping statewide and six regional targets. Mixture: 128 intact paths per seed, 512 total; quantiles after pooling.\n'
 'Development only; no comparable actual ensemble or archived release history, no 2025–26 tuning. Published sums are not unsuppressed totals.',fontsize=9)
fig.tight_layout(rect=(0,.23,1,.95));out=root/('california-history-sharing.png' if args.sharing else 'california-seed-mixtures.png');fig.savefig(out,dpi=150);print(out)
