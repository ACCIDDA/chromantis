from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('output/covid-tree-20261014')
d=pd.read_csv(root/'confirm02-mixtures/distribution-scores.csv')
d=d[d.name.eq('B_width256.errors_half_time+A4.errors_half_time (mixture)')]
fig,ax=plt.subplots(figsize=(10,6))
for _,r in d.iterrows():
 label=('Admissions' if r.target=='wk inc covid hosp' else 'ED visit share')+' — '+('national' if r.geography=='US' else 'states/DC')
 ax.plot([50,80,90,95],[100*r[f'weekly_coverage_{c}'] for c in [50,80,90,95]],'o-',label=label)
ax.plot([50,95],[50,95],'k--',alpha=.5,label='Nominal coverage')
ax.set(xlabel='Nominal interval coverage (%)',ylabel='Observed weekly coverage (%)',ylim=(30,100),title='Forward evaluation: uncertainty intervals still under-cover')
ax.legend(fontsize=9);ax.grid(alpha=.2)
fig.text(.08,.025,'Equal mixture: width-256 quantile MLP + width-192 sampled MLP, each trained on 2022–23 through 2024–25.\n'
 'Artificial reporting perturbations on half of training episodes; width-256 also learns recent-history reconstruction labels.\n'
 'Both learn finalized future admissions/ED labels. Six seeds 58–63 per recipe; 2024–25 reporting-error donors.\n'
 'Evaluate corrected archived 2025–26 inputs; missing archive values use finalized fills. All available reference dates\n'
 'with all four outcomes observed; states/DC averaged equally. Coverage is marginal, not simultaneous over four weeks.',fontsize=9)
fig.subplots_adjust(bottom=.28,top=.9)
fig.savefig(root/'forward-coverage.png',dpi=160);fig.savefig(root/'forward-coverage.pdf')
d.to_csv(root/'forward-coverage.csv',index=False)
