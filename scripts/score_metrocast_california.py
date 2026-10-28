"""California winter pilot: common WIS and intact-path energy on published counts."""
import argparse,json,time
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import torch
from chromantis.dataset.build import load
from chromantis.dataset.cv import score_episodes
from chromantis.evaluation.standard import quantile_scores
from chromantis.experiment.planner import collect
from chromantis.experiment.training import evaluate,path_scores
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from chromantis.evaluation.quantiles import LEVELS
from metrocast_seed_mixture import combine


def score_california_mixtures(entries, expected_seeds, root, training_dates, evaluation_dates, confirmation):
 groups=defaultdict(list)
 for record,path in entries:
  groups[(record['name'],record['scenario'])].append((record['seed'],path))
 rows=[]
 for (name,scenario),members in groups.items():
  seeds=[seed for seed,_ in members]
  if set(seeds)!=set(expected_seeds):continue
  assert len(seeds)==len(set(seeds))
  meta,draws=combine([path for _,path in sorted(members)],horizons=34,unit='count')
  y=meta['truth'][:,:,0,:];mask=meta['mask'][:,:,0,:].astype(bool)
  assert (meta['target_dates'][mask.any(-1)]<=evaluation_dates.split('/')[1]).all()
  q=np.quantile(draws,LEVELS,axis=1)
  wis=quantile_scores(q.reshape(len(LEVELS),-1).T,y.reshape(-1),LEVELS).wis.to_numpy().reshape(y.shape)
  base=dict(name=name,scenario=scenario,seeds=';'.join(map(str,sorted(seeds))),
            aggregation='equal-weight intact-draw seed mixture',draws_per_origin=draws.shape[1],
            training_dates=training_dates,evaluation_dates=evaluation_dates,
            evaluation_inputs='revised published source',labels='published nonmissing-age admission sums; ambiguous duplicate weeks masked',
            ensemble_comparison=False)
  for band,start,stop in [('0-3',0,4),('4-12',4,13),('13-25',13,26),('26-33',26,34),('0-33',0,34)]:
   seen=mask[:,start:stop];n=seen.sum((0,1));loc=np.where(seen,wis[:,start:stop],0).sum((0,1))/np.maximum(n,1)
   rows.append(dict(base,metric='WIS admission counts',horizons=band,value=float(loc[n>0].mean()) if (n>0).any() else np.nan,cells=int(n.sum()),locations=int((n>0).sum())))
  energy=np.zeros((y.shape[0],y.shape[-1]))
  for location in range(y.shape[-1]):
   values,_=path_scores(torch.from_numpy(draws[...,location:location+1].transpose(1,0,2,3).copy()),
                       torch.from_numpy(y[...,location:location+1]),
                       torch.from_numpy(mask[...,location:location+1]),log_counts=True)
   energy[:,location]=values.numpy()[:,0]
  seen=mask.any(1);n=seen.sum(0);loc=(energy*seen).sum(0)/np.maximum(n,1)
  rows.append(dict(base,metric='Path energy log1p counts',horizons='0-33',value=float(loc[n>0].mean()),cells=int(seen.sum()),locations=int((n>0).sum())))
 result=pd.DataFrame(rows)
 result.to_csv(root/('california-confirmation-seed-mixtures.csv' if confirmation else 'california-development-seed-mixtures.csv'),index=False)
 return result


def main():
 p=argparse.ArgumentParser();p.add_argument('-e','--experiment',required=True);p.add_argument('--wait',action='store_true');p.add_argument('--confirmation',action='store_true');a=p.parse_args()
 season='2025-2026' if a.confirmation else '2025-winter'
 evaluation_dates='2025-08-02/2026-06-13' if a.confirmation else '2025-02-01/2025-06-14'
 training_dates='2024-07-06/2025-07-26' if a.confirmation else '2024-07-06/2025-01-25'
 end_date=evaluation_dates.split('/')[1]
 if a.confirmation:
  state=json.loads(Path('experiments/metrocast-20261019/tree.json').read_text())
  assert a.experiment==state.get('california_confirmation')
  frozen=json.loads(Path('experiments/metrocast-20261019/california-frozen-selection.json').read_text())
 torch.set_num_threads(1);root=Path('data/experiments')/a.experiment
 if a.wait:
  end=time.monotonic()+3600
  while True:
   records=collect(root)
   if records and all(r['status']=='complete' for r in records):break
   if any(r['status']=='failed' for r in records) or time.monotonic()>end:raise RuntimeError('California fits failed or wait expired')
   time.sleep(30)
 rows=[];mixture_entries=[]
 for r in collect(root):
  if r['status']!='complete':continue
  run=root/r['attempt'];manifest=json.loads((run/'manifest.json').read_text())
  assert manifest['folds']==[season]
  if a.confirmation:assert r['scenario'] in frozen['candidates'].values()
  problem=Problem.load(manifest['problem']);assert problem.id==('metrocast-california-confirm' if a.confirmation else 'metrocast-california-pilot')
  folder=run/f'eval_{season}';s=Scenario.from_string(r['scenario'])
  base=dict(name=r['name'],scenario=r['scenario'],seed=r['seed'],training_dates=training_dates,evaluation_dates=evaluation_dates,evaluation_inputs='revised published source',labels='published nonmissing-age admission sums; ambiguous duplicate weeks masked')
  with np.load(folder/'forecasts.npz') as f:
   q=f['quantiles'][:,:,:,0,:];y=f['truth'][:,:,0,:];mask=f['mask'][:,:,0,:].astype(bool);levels=f['quantile_levels']
   assert (f['target_dates'][mask.any(-1)]<=end_date).all()
   assert np.isfinite(q).all() and (q>=0).all()
   wis=quantile_scores(q.reshape(len(levels),-1).T,y.reshape(-1),levels).wis.to_numpy().reshape(y.shape)
  for band,start,stop in [('0-3',0,4),('4-12',4,13),('13-25',13,26),('26-33',26,34),('0-33',0,34)]:
   seen=mask[:,start:stop];n=seen.sum((0,1));loc=np.where(seen,wis[:,start:stop],0).sum((0,1))/np.maximum(n,1)
   rows.append(dict(base,metric='WIS admission counts',horizons=band,value=float(loc[n>0].mean()) if (n>0).any() else np.nan,cells=int(n.sum()),locations=int((n>0).sum())))
  cache=folder/('confirmation-joint-paths' if a.confirmation else 'winter-joint-paths')
  if not (cache/'forecasts.npz').exists():
   eps=score_episodes(load(problem.panel),problem,s,season)
   model=load_model(torch.load(folder/'model.pt',map_location='cpu',weights_only=False))
   torch.manual_seed(r['seed']);cache.mkdir(exist_ok=True);evaluate(model,eps,128,'cpu',cache,keep_samples=True);del model
  with np.load(cache/'forecasts.npz') as f:
   draws=f['samples'][:,:,:,0,:].transpose(1,0,2,3).copy()
   assert draws.shape==(128,*y.shape) and np.allclose(y,f['truth'][:,:,0,:])
   assert np.isfinite(draws).all() and (draws>=0).all()
  mixture_entries.append((r,cache/'forecasts.npz'))
  energy,_=path_scores(torch.from_numpy(draws),torch.from_numpy(y),torch.from_numpy(mask),log_counts=True)
  seen=mask.any(1);n=seen.sum(0);loc=(energy.numpy()*seen).sum(0)/np.maximum(n,1)
  rows.append(dict(base,metric='Path energy log1p counts',horizons='0-33',value=float(loc[n>0].mean()),cells=int(seen.sum()),locations=int((n>0).sum())))
  print(r['name'],r['seed'],'scored',flush=True)
 pd.DataFrame(rows).to_csv(root/('california-confirmation-scores.csv' if a.confirmation else 'california-winter-scores.csv'),index=False)
 score_california_mixtures(mixture_entries,range(42,47 if a.confirmation else 46),root,training_dates,evaluation_dates,a.confirmation)
 print('Equal weighting of seven locations, including overlapping California statewide and six regional targets; unavailable long-horizon cells excluded explicitly.')
if __name__=='__main__':main()
