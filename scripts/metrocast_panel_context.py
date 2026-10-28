"""Own-state and other-state HHS-region histories for unchanged MetroCast targets."""
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from chromantis.dataset.build import load
from chromantis.dataset.extract import HHS_REGIONS

ROOT=Path('data/metrocast-panel-context')
NAMES=('state_flu_context','region_other_state_flu_mean')


def build():
 source=Path('data/processed/panel.npz');state=load(source);base=load('data/metrocast/panel.npz')
 metadata=pd.read_csv('data/metrocast/locations.csv').set_index('location').loc[base['locations']]
 states=list(state['locations']);channel=list(state['target_names']).index('nssp_flu_proportion')
 memberships={s:k for k,v in HHS_REGIONS.items() for s in v.split()}
 mapping={}
 for loc,row in metadata.iterrows():
  own=row.state_abb;region=memberships[own]
  mapping[loc]=dict(state=own,hhs_region=region,other_states=[s for s in HHS_REGIONS[region].split() if s!=own])
 index=pd.Index(state['dates'].astype(str)).get_indexer(base['dates'].astype(str));valid=index>=0
 def context(values):
  out=np.full((*values.shape[:-3],len(base['dates']),len(base['locations']),2),np.nan,np.float32)
  for i,loc in enumerate(base['locations']):
   m=mapping[str(loc)];neighbors=[states.index(s) for s in m['other_states']]
   x=values[...,neighbors,channel];n=np.isfinite(x).sum(-1)
   avg=np.where(n>0,np.nansum(x,axis=-1)/np.maximum(n,1),np.nan)
   out[...,valid,i,0]=values[...,index[valid],states.index(m['state']),channel]
   out[...,valid,i,1]=avg[...,index[valid]]
  return out
 revised=context(state['targets']);archive=context(state['asof_targets'])
 hub=list(state['hub_names']).index('flusight');cutoffs=state['issuance_cutoffs_utc'][hub].astype(str)
 assert len(cutoffs)==len(archive)
 assert np.nanmin(revised)>=0 and np.nanmax(revised)<=1
 base['covariates']=revised;base['covariate_names']=np.array(NAMES)
 ROOT.mkdir(exist_ok=True)
 np.savez_compressed(ROOT/'panel.npz',**base)
 np.savez_compressed(ROOT/'context-vintages.npz',dates=base['dates'],locations=base['locations'],names=np.array(NAMES),cutoffs_utc=cutoffs,values=archive)
 digest=hashlib.sha256()
 with source.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
 (ROOT/'manifest.json').write_text(json.dumps(dict(source=str(source),source_sha256=digest.hexdigest(),mapping=mapping,
   target_treatment='Exactly unchanged 90-location MetroCast flu ED labels and histories; NYC target inconsistency remains.',
   covariates='Own-state NSSP flu ED share and unweighted observed mean of other states in its HHS region. Not a population-weighted regional ED rate; NSSP state source may differ from local Hub state source.',
   fitting='Revised covariates with latest week hidden by source schedule; target-history masking specified by scenario.',
   replay='Latest recorded source UTC cutoff no later than Wednesday20ET; often previous Wednesday23ET snapshot. No finalized fill.',
   source_last_date=str(state['dates'][-1]),missing_source_dates=base['dates'].astype(str)[~valid].tolist()),indent=2)+'\n')
 print('Built',len(mapping),'location mappings; source missing for',int((~valid).sum()),'panel weeks')


def archived_context(episode,names,archive,cutoff):
 requested=pd.Timestamp(cutoff+' 20:00',tz='America/New_York').tz_convert('UTC')
 cutoffs=pd.to_datetime(archive['cutoffs_utc'],utc=True);eligible=np.flatnonzero(cutoffs<=requested)
 out=np.zeros((len(episode['context_dates']),len(names),2,len(episode['locations'])),np.float32)
 if not len(eligible):return out,None
 row=eligible[np.argmax(cutoffs[eligible].asi8)]
 dates=pd.Index(archive['dates'].astype(str)).get_indexer(episode['context_dates']);valid=dates>=0
 locs=pd.Index(archive['locations']).get_indexer(episode['locations']);cols=pd.Index(archive['names']).get_indexer(names)
 assert (locs>=0).all() and (cols>=0).all() and cutoffs[row]<=requested
 x=archive['values'][row][dates[valid]][:,locs][:,:,cols].transpose(0,2,1)
 out[valid,:,0,:]=np.nan_to_num(x);out[valid,:,1,:]=np.isfinite(x)
 return out,cutoffs[row].isoformat()

if __name__=='__main__':build()
