from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('output/covid-tree-20261014')
models=['B_width256','Ba_ll.width512','B_width256+A4','B_width256+B_width256.reported+Ba_ll.width512+A4','half-errors-pair']
labels=['Width-256 quantile MLP','Width-512 quantile MLP','Width-256 + width-192 sampled','Four-recipe mixture','Width-256 + sampled, half perturbation']
fig,axes=plt.subplots(1,2,figsize=(13,7),sharey=True)
rows=[]
for folder,seeds,offset,color in [('mixtures02-forward','46–50',-.24,'#4477aa'),('data-forward-mixtures','54–57',0,'#ee7733'),('confirm02-mixtures','58–63',.24,'#228833')]:
 base=root/folder
 h=pd.read_csv(base/('ranking/headline-rankings.csv' if folder!='mixtures02-forward' else 'headline-rankings.csv'))
 h=h[h.deployed & h.target.eq('wk inc covid hosp') & h.scale.eq('log') & h.geography.eq('states_dc')]
 h=h.assign(name=h.name.str.replace('B_width256.errors_half_time+A4.errors_half_time','half-errors-pair',regex=False));h=h.assign(model=h.name.str.removesuffix(' (mixture)')).set_index('model')['mean']
 s=pd.read_csv(base/'summer.csv');s=s[s.target.eq('wk inc covid hosp') & s.scale.eq('log') & s.geography.eq('states_dc')]
 s=s.assign(name=s.name.str.replace('B_width256.errors_half_time+A4.errors_half_time','half-errors-pair',regex=False));s=s.assign(model=s.name.str.removesuffix('-mixture')).groupby('model').mean_wis.mean()
 for ax,values,period in zip(axes,[h,s],['October–May','June–September']):
  for i,m in enumerate(models):
   if m not in values:continue
   v=values[m];ax.barh(i+offset,v,height=.22,color=color,label=f'Seeds {seeds}' if i==0 else None);ax.text(v+.002,i+offset,f'{v:.3f}',va='center',fontsize=9)
   rows.append(dict(model=m,seeds=seeds,period=period,wis=v))
  ax.set_title(period);ax.set_xlim(0,.32);ax.set_xlabel('States/DC log(1 + admissions) WIS; lower is better');ax.spines[['top','right']].set_visible(False)
axes[0].set_yticks(range(len(models)),labels);axes[0].invert_yaxis();axes[1].legend()
fig.suptitle('Forward evaluation: recipe rankings vary across seed groups')
fig.text(.025,.025,'All models retrained on 2022–23 through 2024–25; finalized future admissions and ED prediction labels.\n'
 'Evaluate archived 2025–26 reports, corrected deployment view; archive gaps use finalized fills. Error donors: 2024–25.\n'
 'Width-256: artificial training histories with reconstruction labels. Width-512: artificial/actual-report histories with reconstruction.\n'
 'Sampled width-192: corrected artificial training histories. Fourth recipe: archived-training-report width-256, no reconstruction.\n'
 'Half perturbation changes training inputs: reporting errors applied on half of episodes; same prediction labels and evaluation inputs.\n'
 'Each bar mixes all indicated seeds equally; multi-recipe mixtures also weight recipes equally. Half-perturbation pair is exploratory.\n'
 'Seed groups contain five, four and six fits per recipe. Differences are not confidence intervals or a paired significance test.',fontsize=9,linespacing=1.4)
fig.subplots_adjust(left=.29,right=.98,bottom=.36,top=.89,wspace=.15)
fig.savefig(root/'forward-seed-comparison.png',dpi=160);fig.savefig(root/'forward-seed-comparison.pdf')
pd.DataFrame(rows).to_csv(root/'forward-seed-comparison.csv',index=False)
