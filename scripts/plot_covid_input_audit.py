from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('output/covid-tree-20261014')
rows=[]
for folder,label in [('data-mixtures','Held-out seasons\nartificial inputs'),('data-reported-mixtures','Same fitted models\narchived inputs'),('confirm02-mixtures','Forward 2025–26\narchived inputs')]:
 h=pd.read_csv(root/folder/'ranking/headline-rankings.csv');h=h[h.deployed & h.target.eq('wk inc covid hosp') & h.scale.eq('log') & h.geography.eq('states_dc')].set_index('name')['mean']
 s=pd.read_csv(root/folder/'summer.csv');s=s[s.target.eq('wk inc covid hosp') & s.scale.eq('log') & s.geography.eq('states_dc')].groupby('name').mean_wis.mean()
 for model,name in [('Full perturbation','B_width256+A4'),('Half perturbation','B_width256.errors_half_time+A4.errors_half_time' if folder=='confirm02-mixtures' else 'half-errors-pair')]:
  rows.append(dict(design=label,model=model,oct_may=h[name+' (mixture)'],summer=s[name+'-mixture']))
t=pd.DataFrame(rows);t.to_csv(root/'input-audit.csv',index=False)
fig,axes=plt.subplots(1,2,figsize=(12,7),sharey=True)
for ax,col,title in zip(axes,['oct_may','summer'],['October–May','June–September']):
 for j,(m,c) in enumerate([('Full perturbation','#4477aa'),('Half perturbation','#ee7733')]):
  d=t[t.model.eq(m)]
  ax.barh([i+(j-.5)*.33 for i in range(3)],d[col],height=.3,color=c,label=m)
  for i,v in enumerate(d[col]):ax.text(v+.001,i+(j-.5)*.33,f'{v:.3f}',va='center',fontsize=9)
 ax.set(title=title,xlim=(0,.34),xlabel='States/DC log(1 + admissions) WIS; lower is better')
 ax.spines[['top','right']].set_visible(False)
axes[0].set_yticks(range(3),t.design.drop_duplicates());axes[0].invert_yaxis();axes[1].legend()
fig.suptitle('Leading candidate: training perturbation and evaluation-input audit')
fig.text(.03,.025,'Both pairs mix width-256 quantile MLP (with recent-history reconstruction labels) and width-192 sampled MLP equally.\n'
 'All learn finalized future admissions and ED labels. Full vs half changes reporting-error frequency in training inputs only.\n'
 'Top two rows: hold out 2023–24, 2024–25, 2025–26 in turn; train on other seasons from 2022–23 through 2025–26.\n'
 'Four seeds 54–57 per recipe; 2025–26 error donors. First row averages three prescribed preliminary histories.\n'
 'Second row reuses those checkpoints with archived evaluation inputs. Third row retrains on 2022–23 through 2024–25,\n'
 'uses 2024–25 error donors and independent seeds 58–63. All use corrected deployment inputs; archive gaps use finalized fills.\n'
 'Summer is scored separately. Designs differ; compare models within each row. ED/national interval undercoverage remains unresolved.',fontsize=9,linespacing=1.4)
fig.subplots_adjust(left=.21,right=.98,top=.88,bottom=.34,wspace=.17)
fig.savefig(root/'input-audit.png',dpi=160);fig.savefig(root/'input-audit.pdf')
print(t.to_string(index=False))
