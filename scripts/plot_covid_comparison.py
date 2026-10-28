from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('output/covid-tree-20261014')
selected=[('B_width256','A: artificial histories'),('B_width256.reported','B: archived reports'),('B_width256.reported+Ba_ll.width512','B + C'),('B_width256+A4','A + D'),('B_width256+B_width256.reported+Ba_ll.width512+A4','A + B + C + D')]
def headline(file):
 d=pd.read_csv(file);d=d[d.deployed & d.target.eq('wk inc covid hosp') & d.scale.eq('log') & d.geography.eq('states_dc')];d['group']=d.name.str.removesuffix(' (mixture)');return d.set_index('group')['mean']
a=headline(root/'mixtures02-screen/headline-rankings.csv');b=headline(root/'mixtures02-forward/headline-rankings.csv')
d=pd.read_csv(root/'mixtures02-forward/summer.csv');d=d[d.target.eq('wk inc covid hosp') & d.scale.eq('log') & d.geography.eq('states_dc')];d['group']=d.name.str.removesuffix('-mixture');c=d.groupby('group').mean_wis.mean()
table=pd.DataFrame({'model':[x[0] for x in selected],'label':[x[1] for x in selected],'retrospective_oct_may':[a[x[0]] for x in selected],'forward_oct_may':[b[x[0]] for x in selected],'forward_jun_sep':[c[x[0]] for x in selected]});table.to_csv(root/'candidate-comparison.csv',index=False)
fig,axes=plt.subplots(1,3,figsize=(14,8),sharey=True)
colors=['#4477aa','#ee7733','#228833','#aa3377','#667788']
for ax,col,title in zip(axes,table.columns[2:],['Three held-out seasons\nArtificial preliminary evaluation inputs','Forward-only: 2025–26\nArchived-report inputs, October–May','Same forward-only models\nArchived-report inputs, June–September']):
 ax.barh(range(len(table)),table[col],color=colors,height=.6)
 for i,v in enumerate(table[col]):ax.text(v+.001,i,f'{v:.4f}',va='center',fontsize=10)
 ax.set_xlim(0,.31);ax.set_title(title,fontsize=11);ax.set_xlabel('States/DC log(1 + admissions) WIS\nLower is better',fontsize=10);ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
axes[0].set_yticks(range(len(table)),table.label);axes[0].invert_yaxis()
fig.suptitle('COVID model candidates: retrospective and forward checks',fontsize=17,y=.96)
text=('Models: A = width-256 quantile MLP, artificial training histories + recent-history reconstruction labels. B = same-width quantile MLP, archived\n'
      'training reports, no reconstruction labels. C = width-512 quantile MLP, artificial/actual-report training mixture + reconstruction labels.\n'
      'D = width-192 sampled MLP, corrected artificial training histories. All learn finalized future COVID admissions and ED labels; no covariates.\n'
      'Deployment view: corrected preliminary histories. Mixtures give equal weight to each recipe and to each seed within a recipe.\n\n'
      'Left: hold out 2023–24, 2024–25 and 2025–26 in turn; fit the other seasons from 2022–23 through 2025–26. COVID 2025–26 reporting errors\n'
      'supply artificial training and evaluation histories; three shared evaluation draws. Four seeds (42–45) per recipe, seasons weighted equally.\n'
      'Middle/right: retrain on 2022–23 through 2024–25 using 2024–25 reporting-error data; evaluate archived 2025–26 reports. Five seeds (46–50).\n'
      'Right is June–September only, not a new fit. All scores use finalized future labels. Archive gaps retain the template’s finalized-value fills.\n'
      'These are different evaluation designs, not a causal comparison of input sources. No uncertainty bars; model selection is still in progress.')
fig.text(.035,.025,text,fontsize=9,va='bottom',linespacing=1.45)
fig.subplots_adjust(left=.17,right=.98,top=.83,bottom=.43,wspace=.17)
fig.savefig(root/'candidate-comparison.png',dpi=160);fig.savefig(root/'candidate-comparison.pdf');plt.close(fig)
print(table.to_string(index=False))
