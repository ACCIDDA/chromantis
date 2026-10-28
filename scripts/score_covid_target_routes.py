"""Audit ED replacement using saved joint-model forecasts; never refits/calibrates."""
import json
from pathlib import Path
import numpy as np
from chromantis.evaluation.ranking import rank
base=Path('data/experiments/covid-ed-forward-mixtures')
out=Path('data/experiments/covid-ed-target-routes')
source=base/'baseline-mixture'
m=json.loads((source/'manifest.json').read_text())
from chromantis.problem import Problem
problem=Problem.load(m['problem'])
assert problem.target_signals[1].hub_target=='wk inc covid prop ed visits'
rows=[]
for variant in ['baseline','ed_linear','ed_fourth_root','national_head','inpatient']:
 donor=base/f'{variant}-mixture';dm=json.loads((donor/'manifest.json').read_text())
 assert dm['problem_sha256']==m['problem_sha256'] and dm['folds']==m['folds']
 target=out/variant
 target.mkdir(parents=True,exist_ok=False)
 for season in m['folds']:
  rel=Path(f'eval_{season}/corrected/forecasts.npz')
  a=dict(np.load(source/rel));b=dict(np.load(donor/rel))
  for key in ['truth','mask','context_end','target_dates','locations','quantile_levels']:
   assert np.array_equal(a[key],b[key]),(variant,key)
  admissions=a['quantiles'][:,:,:,0,:].copy()
  a['quantiles'][:,:,:,1,:]=b['quantiles'][:,:,:,1,:]
  assert np.array_equal(a['quantiles'][:,:,:,0,:],admissions)
  (target/rel).parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(target/rel,**a)
 manifest=dict(m,ensemble={'admissions_source':str(source),'ed_source':str(donor)},definition='Admissions copied exactly from baseline mixture; ED copied from named mixture. Same aligned outcomes, inputs and training season design. No refit or calibration.')
 (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 rows.append(dict(path=target,config_id=f'ED={variant},admissions=baseline',name=variant,seed=0))
rank(rows,'data/evaluation/b0_hub_comparison_q23',out/'ranking')
