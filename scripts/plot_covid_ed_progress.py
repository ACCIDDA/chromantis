from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('output/covid-ed-20261015'); rows=[]
fig,axes=plt.subplots(1,2,figsize=(12,7),sharey=True)
models=['baseline','ed_linear','ed_fourth_root','national_head','inpatient','wastewater']
for folder,seeds,offset,color in [('forward-mixtures','70–73',-.17,'#4477aa'),('confirm-mixtures','74–79',.17,'#ee7733')]:
 d=pd.read_csv(root/folder/'ranking/hub-relative-scores.csv');d=d[d.deployed&d.target.eq('wk inc covid prop ed visits')]
 for ax,geo in zip(axes,['states_dc','US']):
  vals=[float(d[d.name.eq(m+' (mixture)')&d.geography.eq(geo)].wis_ratio.iloc[0]) for m in models]
  ax.barh([i+offset for i in range(len(models))],vals,height=.3,label=f'Seeds {seeds}',color=color)
  for i,v in enumerate(vals):ax.text(v+.015,i+offset,f'{v:.2f}',va='center',fontsize=9);rows.append(dict(model=models[i],seeds=seeds,geography=geo,hub_wis_ratio=v))
  ax.axvline(1,color='black',ls='--',lw=1);ax.set(title='States/DC' if geo=='states_dc' else 'National',xlabel='ED WIS / Hub ensemble WIS; below 1 is better',xlim=(0,2.3));ax.spines[['top','right']].set_visible(False)
axes[0].set_yticks(range(len(models)),['Baseline logit','Linear ED','Fourth-root ED','Separate national head','Inpatient covariates','Wastewater covariates']);axes[0].invert_yaxis();axes[1].legend()
fig.suptitle('COVID ED improvements: initial and fresh-seed comparisons')
fig.text(.025,.025,'Each bar mixes width-256 quantile and width-192 sampled MLPs equally, then all indicated seeds equally.\n'
 'Both trained jointly on finalized future admissions and ED labels from 2022–23 through 2024–25, with artificial\n'
 'reporting perturbations on half of training episodes and 2024–25 error donors; width-256 also uses reconstruction labels.\n'
 'Each named treatment changes only the indicated baseline setting; covariates enter training and evaluation inputs.\n'
 'Evaluate corrected archived 2025–26 inputs on matched Hub ED tasks, Jan 17–Aug 1, 2026, horizons0–3.\n'
 'Archive gaps use finalized fills. Same season reused adaptively; fresh seeds are not an untouched temporal test.\n'
 'Lower WIS does not establish calibrated intervals: fourth-root 95% coverage remains about89% states/DC in confirmation.',fontsize=9,linespacing=1.35)
fig.subplots_adjust(left=.2,right=.98,top=.88,bottom=.34,wspace=.2)
fig.savefig(root/'ed-progress.png',dpi=160);fig.savefig(root/'ed-progress.pdf');pd.DataFrame(rows).to_csv(root/'ed-progress.csv',index=False)
