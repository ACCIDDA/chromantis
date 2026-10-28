"""California published admission sums, retaining suppression and duplicate ambiguity."""
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT=Path('data/metrocast-california')
SOURCE=Path('data/metrocast/source/ca-rv-dashboard.csv')


def main():
    raw=pd.read_csv(SOURCE)
    d=raw[raw.AGE_GRP.isin(['0-4 yrs','5-17 yrs','18-64 yrs','>64 yrs'])].copy()
    d['date']=pd.to_datetime(d.WEEKENDING).dt.strftime('%Y-%m-%d')
    d['location']=d.RPHO_REGION.str.lower().map(lambda x:re.sub('[^a-z0-9]+','-',x))
    keys=['location','date','AGE_GRP']
    duplicates=d[d.duplicated(keys,keep=False)][['location','date']].drop_duplicates()
    grouped=d.groupby(['date','location']).FLU_ADM.agg(observation=lambda s:s.sum(min_count=1),observed_age_groups='count').reset_index()
    duplicate_keys=set(map(tuple,duplicates[['date','location']].to_numpy()))
    grouped['ambiguous']=list(map(lambda row:tuple(row) in duplicate_keys,grouped[['date','location']].to_numpy()))
    grouped.loc[grouped.ambiguous,'observation']=np.nan
    assert (grouped.observation.dropna()>=0).all()
    assert pd.to_datetime(grouped.date).dt.dayofweek.eq(5).all()
    locations=sorted(grouped.location.unique())
    metadata=pd.read_csv('data/metrocast/source/locations.csv').set_index('location').loc[locations]
    dates=pd.date_range(grouped.date.min(),grouped.date.max(),freq='W-SAT')
    values=grouped.pivot(index='date',columns='location',values='observation').reindex(index=dates.strftime('%Y-%m-%d'),columns=locations).to_numpy(np.float32)
    ROOT.mkdir(exist_ok=True)
    np.savez_compressed(ROOT/'panel.npz',dates=dates.to_numpy(dtype='datetime64[D]'),locations=np.array(locations),
        target_names=np.array(['metrocast_ca_flu_admissions']),targets=values[...,None],
        covariates=np.empty((*values.shape,0),np.float32),covariate_names=np.array([],dtype='U1'),
        covariates_national=np.empty((len(dates),0),np.float32),covariate_national_names=np.array([],dtype='U1'),truth_day=np.array('2026-10-20'))
    metadata.reset_index().to_csv(ROOT/'locations.csv',index=False)
    grouped.to_csv(ROOT/'published-admission-sums.csv',index=False)
    with np.load('data/processed/historical_ili.npz') as f:
        ca=[str(v).upper() for v in f['locations']].index('CA')
        np.savez_compressed(ROOT/'historical_ili.npz',dates=f['dates'],locations=np.array(locations),
                            values=np.repeat(f['values'][:,ca:ca+1],len(locations),axis=1))
    manifest=dict(source=str(SOURCE),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),locations=locations,
        first=str(dates[0].date()),last=str(dates[-1].date()),target='Flu hosp admits',unit='count',
        aggregation='Match official MetroCast script: sum nonmissing FLU_ADM over 0-4,5-17,18-64,>64; all missing stays missing. Published partial sums, not unsuppressed total admissions.',
        duplicate_treatment='Entire location/week masked when any age-group key duplicated; no arbitrary version choice or double counting.',
        ambiguous_location_weeks=duplicates.to_dict('records'),
        historical_pretraining='2010-11 through 2021-22 California state ILI broadcast to seven regions, scaled with fitting-only regional admission Q95. Pseudo-counts are not historical regional admissions.',
        evaluation='Revised source only; historical publication vintages unavailable. Do not call operational or ensemble-relative.',
        overlap='California statewide total overlaps six constituent regions; equal location scoring counts both levels.')
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('locations',len(locations),'dates',len(dates),'ambiguous location/weeks masked',len(duplicates))

if __name__=='__main__': main()
