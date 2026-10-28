"""Frozen 2025-26 MetroCast comparison on matching targets and stable geographies."""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from chromantis.dataset.build import load
from chromantis.dataset.cv import score_episodes
from chromantis.evaluation.standard import quantile_scores
from chromantis.experiment.planner import collect
from chromantis.experiment.training import evaluate
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from metrocast_seed_mixture import has_samples, score_mixtures

ROOT = Path('data/metrocast-ensemble-2025-26')
KEY = ['reference_date', 'target_end_date', 'location', 'horizon']
LEVELS = np.array([.025,.05,.1,.25,.5,.75,.9,.95,.975])


def prepare_archive(archive):
    archive = archive[archive.target.eq('Flu ED visits pct')].copy()
    keys = ['as_of','target_end_date','location']
    # Conflicting same-date vintages have no within-day ordering. Keep them missing.
    conflicting = archive.groupby(keys).observation.transform('nunique', dropna=False).gt(1)
    archive.loc[conflicting,'observation'] = np.nan
    return archive.drop_duplicates(keys).sort_values('as_of')


def ensemble_tasks():
    old = pd.read_csv(ROOT / 'source/locations-2025-26.csv').set_index('location').fillna('')
    new = pd.read_csv('data/metrocast/locations.csv').set_index('location').fillna('')
    common = old.index.intersection(new.index)
    fields = ['original_location_code','state_abb','location_type','hsa_counties']
    stable = (old.loc[common,fields].astype(str) == new.loc[common,fields].astype(str)).all(axis=1)
    locations = set(common[stable]) - {'nyc'}
    source = pd.concat([pd.read_csv(p) for p in sorted((ROOT/'source').glob('*-epiENGAGE-ensemble_mean.csv'))])
    source = source[source.target.eq('Flu ED visits pct') & source.horizon.isin(range(4)) & source.output_type.eq('quantile')]
    excluded = sorted(set(source.location)-locations)
    source = source[source.location.isin(locations)]
    assert not source.duplicated([*KEY,'output_type_id']).any()
    wide = source.pivot(index=KEY,columns='output_type_id',values='value').reindex(columns=LEVELS)
    assert np.isfinite(wide.to_numpy()).all()
    wide.columns = [f'ensemble_q{q:g}' for q in LEVELS]
    return wide.reset_index(), excluded


def replay_episode(episode, archive, metadata, context_archive=None, covariate_names=()):
    reference = date.fromisoformat(str(episode['context_dates'][-1])) + timedelta(days=7)
    cutoff = (reference-timedelta(days=3)).isoformat()
    # Archive timestamps are dates only: exclude the entire Wednesday to guarantee the 20:00 ET cutoff.
    released = archive[archive.as_of.lt(cutoff)].drop_duplicates(['target_end_date','location'],keep='last')
    wide = released.pivot(index='target_end_date',columns='location',values='observation')
    x = wide.reindex(index=episode['context_dates'],columns=episode['locations']).to_numpy(np.float32)[:,None,:]/100
    result = dict(episode,values=np.nan_to_num(x),available=np.isfinite(x),known_final=np.isfinite(x))
    if 'covariates' in episode and episode['covariates'].shape[1]:
        if context_archive is not None:
            from metrocast_panel_context import archived_context
            result['covariates'], result['context_source_cutoff_utc'] = archived_context(
                episode, covariate_names, context_archive, cutoff)
        else:
            assert episode['covariates'].shape[1] == 1
            states = metadata.loc[list(episode['locations']),'state'].str.lower().str.replace(' ','-').tolist()
            c = wide.reindex(index=episode['context_dates'],columns=states).to_numpy(np.float32)/100
            cov = np.zeros_like(episode['covariates'])
            cov[:,0,0,:] = np.nan_to_num(c)
            cov[:,0,1,:] = np.isfinite(c)
            result['covariates'] = cov
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e','--experiment',required=True)
    parser.add_argument('--device',default='cpu')
    args = parser.parse_args()
    tree = json.loads(Path('experiments/metrocast-20261019/tree.json').read_text())
    assert args.experiment in {tree.get('confirmation'),tree.get('full_season_confirmation'),tree.get('delay_confirmation'),tree.get('context_confirmation')}, 'Only frozen confirmation experiments may be scored'
    torch.set_num_threads(1)
    ensemble, excluded = ensemble_tasks()
    archive = pd.read_csv('data/metrocast/source/time-series.csv')
    archive = prepare_archive(archive)
    assert not archive.duplicated(['as_of','target_end_date','location']).any()
    metadata = pd.read_csv('data/metrocast/locations.csv').set_index('location')
    folder = Path('data/experiments')/args.experiment
    rows=[]
    mixture_entries=[]
    context_archive=None
    for record in collect(folder):
        if record['status']!='complete': continue
        run=folder/record['attempt']
        manifest=json.loads((run/'manifest.json').read_text())
        assert manifest['folds']==['2025-2026']
        problem=Problem.load(manifest['problem'])
        assert Path(problem.panel).resolve() in {Path('data/metrocast/panel.npz').resolve(),Path('data/metrocast-panel-context/panel.npz').resolve()}
        scenario=Scenario.from_string(record['scenario'])
        covariates=problem.covariate_names(scenario.covariate_set)
        uses_context=Path(problem.panel).resolve()==Path('data/metrocast-panel-context/panel.npz').resolve()
        if uses_context:
            assert covariates in ((),('state_flu_context',),('state_flu_context','region_other_state_flu_mean'))
            if context_archive is None:
                with np.load('data/metrocast-panel-context/context-vintages.npz') as f:
                    context_archive={k:f[k] for k in f.files}
        else:
            assert covariates in ((),('state_flu_proportion',))
        fold=run/'eval_2025-2026'; archived=fold/'metrocast-before-wednesday-inputs'
        if not has_samples(archived/'forecasts.npz'):
            episodes=score_episodes(load(problem.panel),problem,scenario,'2025-2026')
            replay=[replay_episode(e,archive,metadata,context_archive if uses_context else None,covariates) for e in episodes if
                    (date.fromisoformat(str(e['context_dates'][-1]))+timedelta(days=7)).isoformat() in set(ensemble.reference_date)]
            assert replay
            model=load_model(torch.load(fold/'model.pt',map_location='cpu',weights_only=False)).to(args.device)
            torch.manual_seed(record['seed'])
            archived.mkdir(exist_ok=True)
            evaluate(model,replay,512,args.device,archived,keep_samples=True)
            if uses_context:
                (archived/'context-cutoffs.json').write_text(json.dumps([
                    dict(context_end=str(e['context_dates'][-1]),source_cutoff_utc=e.get('context_source_cutoff_utc'))
                    for e in replay],indent=2)+'\n')
            del model
        mixture_entries.append((record,archived/'forecasts.npz','archived_before_wednesday'))
        for view,path in [('revised',fold),('archived_before_wednesday',archived)]:
            with np.load(path/'forecasts.npz') as f:
                idx=[int(np.flatnonzero(np.isclose(f['quantile_levels'],q))[0]) for q in LEVELS]
                q=f['quantiles'][idx,:,:4,0,:]
                n,h,l=q.shape[1:]
                refs=[(date.fromisoformat(str(v))+timedelta(days=7)).isoformat() for v in f['context_end']]
                pred=pd.DataFrame(dict(reference_date=np.repeat(refs,h*l),target_end_date=np.repeat(f['target_dates'][:,:4].reshape(-1),l),
                    location=np.tile(f['locations'],n*h),horizon=np.tile(np.repeat(np.arange(h),l),n),
                    observed=f['truth'][:,:4,0,:].reshape(-1),available=f['mask'][:,:4,0,:].reshape(-1)))
                qcols=[f'q{x:g}' for x in LEVELS];pred[qcols]=q.reshape(len(LEVELS),-1).T
            matched=ensemble.merge(pred[pred.available],on=KEY,validate='one_to_one')
            assert len(matched)
            y=matched.observed.to_numpy()
            ours=quantile_scores(matched[qcols].to_numpy(),y,LEVELS).wis.to_numpy()
            theirs=quantile_scores(matched[[f'ensemble_q{x:g}' for x in LEVELS]].to_numpy()/100,y,LEVELS).wis.to_numpy()
            cells=matched[KEY].assign(model_wis=ours,ensemble_wis=theirs)
            loc=cells.groupby('location')[['model_wis','ensemble_wis']].sum()
            rows.append(dict(name=record['name'],scenario=record['scenario'],seed=record['seed'],evaluation_inputs=view,
                training_seasons='2022-2023;2023-2024;2024-2025',evaluation_season='2025-2026',labels='future local flu ED proportions',
                tasks=len(cells),ensemble_tasks=len(ensemble),locations=len(loc),excluded_geographies=';'.join(excluded),
                model_wis_percentage_points=float(ours.mean()*100),ensemble_wis_percentage_points=float(theirs.mean()*100),
                location_mean_wis_ratio=float((loc.model_wis/loc.ensemble_wis).mean()),pooled_wis_ratio=float(ours.mean()/theirs.mean())))
            cells.to_parquet(path/'metrocast-confirmation-ensemble-cells.parquet',index=False)
        print(record['name'],record['seed'],'scored',flush=True)
    pd.DataFrame(rows).to_csv(folder/'metrocast-confirmation-ensemble-comparison.csv',index=False)
    score_mixtures(mixture_entries,ensemble,range(42,47),folder,'2022-2023;2023-2024;2024-2025','2025-2026')
    print('Excluded geography mismatches:',excluded,'; NYC ILI target excluded separately.')
    print('Archive date-only safety rule: strictly before Wednesday; no finalized fill; local and state inputs use same cutoff.')
    print('Conflicting observations with identical archive date/location/week are masked, not arbitrarily selected.')

if __name__=='__main__':
    main()
