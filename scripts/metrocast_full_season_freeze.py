"""Freeze long-horizon finalists using development-season scores only."""
from datetime import datetime, timezone
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from chromantis.model.scenario import Scenario
from chromantis.experiment.planner import collect

STAGES = {'full-season-memory', 'full-season-delay', 'full-season-sharing', 'full-season-direct-refine'}
METRICS = ['WIS percentage points', 'Path energy percentage points']


def launch_score(name, root):
    command = ['sbatch', f'--job-name={name}-score', 'scripts/metrocast_confirmation_score.sbatch', name]
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    with (root / 'manager-commands.sh').open('a') as out:
        out.write('\n' + ' '.join(command) + '\n# ' + result.stdout.strip() + '\n')
        if name.startswith('metrocast-california-confirm-'):
            out.write(f'.venv/bin/python scripts/score_metrocast_california.py -e {name} --confirmation\n')
        elif not name.startswith('metrocast-utah-confirm-'):
            out.write(f'.venv/bin/python scripts/score_metrocast_confirmation.py -e {name}\n')
        if name.startswith(('metrocast-full-season-confirm-', 'metrocast-utah-confirm-')):
            out.write(f'.venv/bin/python scripts/score_metrocast_full_season.py -e {name} --paths --confirmation\n')


def freeze_utah(state, root, plan, save, state_path):
    """Keep proposed Utah targets and their development ranking separate."""
    record_path = root/'utah-frozen-selection.json'
    if record_path.exists():
        frozen = json.loads(record_path.read_text())
    else:
        ranked, hashes = [], {}
        for rd in state['rounds']:
            if rd['stage'] != 'utah-proposed-fullseason':
                continue
            path = Path('data/experiments')/rd['name']/'early-season-long-horizon.csv'
            if path.exists():
                hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
                ranked.extend(dict(row, experiment=rd['name']) for row in eligible(pd.read_csv(path)))
        if not ranked:
            raise RuntimeError('Utah freeze requires four development seeds for whole-season WIS and path energy')
        chosen = {}
        for metric in ['wis', 'path_energy']:
            row = min(ranked, key=lambda r: (r[metric], r['scenario']))
            chosen[row['scenario']] = row
        candidates = {f'utah_finalist_{i+1}': s for i, s in enumerate(chosen)}
        reference = next(r['scenario'] for r in ranked if r['name'] == 'mlp52_linear_320epochs_none_lag0')
        if reference not in candidates.values():
            candidates['utah_direct_reference'] = reference
        for label, value in list(candidates.items()):
            config = Scenario.from_string(value)
            assert config.training_target_lag in {0, 1}
            paired = replace(config, training_target_lag=1-config.training_target_lag).scenario_string
            if paired not in candidates.values():
                candidates[label+'_paired_history_gap'] = paired
        source_path = Path('data/metrocast-utah-proposed/manifest.json')
        frozen = dict(
            frozen_at=datetime.now(timezone.utc).isoformat(), candidates=candidates,
            eligible=ranked, source_sha256=hashes,
            proposed_source=json.loads(source_path.read_text()),
            proposed_manifest_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
            criterion='Utah-only mean four-seed 2024-25 whole34 WIS and intact-path energy; direct reference and paired training gaps. Equal14 locations including overlapping statewide. No main-panel or holdout ranking.')
        save(record_path, frozen)
    name = plan(state, frozen['candidates'], {}, [42,43,44,45,46], stage='utah-confirm',
                problem='problems/metrocast-utah-confirm.json', protocol=dict(
                    training_seasons=['2022-2023','2023-2024','2024-2025'], evaluation_season='2025-2026',
                    inputs='Provisional revised weekly PR587 source; selected target-history gap applies only during fitting and inner validation.',
                    labels='Future local influenza ED proportions for13 Utah districts and overlapping state, explicit name mapping.',
                    evaluation_inputs='Revised proposed weekly source only; no archived-release or actual-ensemble claim.',
                    selection='Utah-only 2024-25 development WIS/path energy, frozen before holdout; unmerged source remains provisional.'))
    state['utah_confirmation'] = name
    save(state_path, state)
    launch_score(name, root)
    return name


def freeze_context(state, root, plan, save, state_path):
    rows=[]
    for rd in state['rounds']:
        if rd['stage']!='panel-context':
            continue
        folder=Path('data/experiments')/rd['name']
        for record in collect(folder):
            if record['status']!='complete':
                continue
            run=folder/record['attempt']
            assert json.loads((run/'manifest.json').read_text())['folds']==['2024-2025']
            score=pd.read_csv(run/'scores-raw.csv')
            score=score[score.history.eq('raw') & score.scale.eq('natural') & score.geography.eq('locations')]
            assert len(score)==1
            rows.append(dict(scenario=record['scenario'],seed=record['seed'],wis=float(score.mean_wis.iloc[0])))
    complete=[]
    for scenario,group in pd.DataFrame(rows).groupby('scenario'):
        if len(group)==4 and set(group.seed)=={42,43,44,45} and np.isfinite(group.wis).all():
            complete.append(dict(scenario=scenario,wis=float(group.wis.mean())))
    if not complete:
        raise RuntimeError('Context confirmation needs four complete development seeds')
    best=min(complete,key=lambda x:(x['wis'],x['scenario']))
    base=Scenario.from_string(best['scenario'])
    candidates={f'context_{cov}':replace(base,covariate_set=cov).scenario_string
                for cov in ['none','state','state_regional']}
    assert set(candidates.values()).issubset({r['scenario'] for r in complete}), 'All matched context comparisons need development results'
    save(root/'context-frozen-selection.json',dict(
        frozen_at=datetime.now(timezone.utc).isoformat(),candidates=candidates,development=complete,
        criterion='Choose architecture/spatial mode using 2024-25 revised WIS, then retain matched none/state/state+region comparisons; no holdout selection.'))
    name=plan(state,candidates,{},[42,43,44,45,46],stage='context-confirm',
              problem='problems/metrocast-panel-context-confirm.json',protocol=dict(
                  training_seasons=['2022-2023','2023-2024','2024-2025'],evaluation_season='2025-2026',
                  inputs='Revised local history with latest target week hidden during fitting/validation; covariates none versus own-state NSSP versus own-state and other HHS-state mean, latest covariate week masked.',
                  labels='Unchanged future flu ED proportions for 90 jurisdictions.',
                  evaluation_inputs='Revised histories plus conservative archived local/state/regional replay against matched ensemble tasks.',
                  selection='Architecture and spatial mode chosen using 2024-25 only; all three context treatments frozen before confirmation.'))
    state['context_confirmation']=name
    save(state_path,state)
    launch_score(name,root)
    return name


def freeze_california(state, root, plan, save, state_path):
    rows=[]
    for rd in state['rounds']:
        if rd['stage']!='california-pilot':
            continue
        path=Path('data/experiments')/rd['name']/'california-winter-scores.csv'
        if not path.exists():
            continue
        table=pd.read_csv(path)
        assert table.training_dates.eq('2024-07-06/2025-01-25').all()
        assert table.evaluation_dates.eq('2025-02-01/2025-06-14').all()
        for scenario,group in table[table.horizons.eq('0-33')].groupby('scenario'):
            metrics={}
            for metric in ['WIS admission counts','Path energy log1p counts']:
                values=group[group.metric.eq(metric)]
                if len(values)==4 and set(values.seed)=={42,43,44,45} and np.isfinite(values.value).all():
                    metrics[metric]=float(values.value.mean())
            if len(metrics)==2:
                rows.append(dict(scenario=scenario,**metrics))
    if not rows:
        raise RuntimeError('California confirmation needs four-seed winter WIS and path scores')
    chosen={}
    for metric in ['WIS admission counts','Path energy log1p counts']:
        item=min(rows,key=lambda x:(x[metric],x['scenario']))
        chosen[item['scenario']]=item
    candidates={f'california_finalist_{i+1}':s for i,s in enumerate(chosen)}
    reference=Scenario.from_string('geography=0,decoder=residual2,noise=local,width=64,epochs=160,batch_size=2,members=16,forecast_view=raw').scenario_string
    if reference not in candidates.values():
        candidates['california_direct_reference']=reference
    save(root/'california-frozen-selection.json',dict(
        frozen_at=datetime.now(timezone.utc).isoformat(),candidates=candidates,development=rows,
        criterion='Best available-horizon winter WIS and log-count path energy on Feb-Jun2025 only, plus direct reference; pilot cannot validate all34 future weeks.'))
    name=plan(state,candidates,{},[42,43,44,45,46],stage='california-confirm',
              problem='problems/metrocast-california-confirm.json',protocol=dict(
                  training_seasons=['2024-07-06 through 2025-07-26'],evaluation_season='2025-08-02 through 2026-06-13',
                  inputs='Revised published regional admission sums; per-scenario latest target-history week hidden during fitting/validation only.',
                  labels='Future published sums over nonmissing age groups, not unsuppressed admission totals; duplicate region/weeks masked.',
                  evaluation_inputs='Revised source only; archived release histories and comparable hospitalization ensemble unavailable.',
                  selection='Frozen using only 2024-25 winter pilot results; no 2025-26 tuning.'))
    state['california_confirmation']=name
    save(state_path,state)
    launch_score(name,root)
    return name


def freeze_delay(state, root, plan, save, state_path):
    """Predeclared paired reporting-delay comparison; no holdout-driven selection."""
    reference = next(r for r in state['rounds'] if r['name'] == state['confirmation'])
    source = json.loads(Path(reference['study']).read_text())
    candidates = {name + '_fit_lag1': replace(Scenario.from_string(value), training_target_lag=1).scenario_string
                  for name, value in source['candidates'].items()}
    candidates['county_development_recipe_fit_on_main_panel'] = Scenario.from_string(
        'ed_transform=logit,geography=0,decoder=residual2,noise=local,width=128,epochs=80,members=32,training_target_lag=1,forecast_view=raw'
    ).scenario_string
    save(root / 'delay-frozen-selection.json', dict(
        frozen_at=datetime.now(timezone.utc).isoformat(), paired_experiment=state['confirmation'],
        candidates=candidates, criterion='Exact four-week finalists with latest target week hidden during fitting/inner validation; plus 80-epoch county-development recipe refitted on 90-location labels. No confirmation outcomes consulted.'))
    name = plan(state, candidates, {}, [42,43,44,45,46], stage='confirm-delay',
                problem='problems/metrocast-flu-confirm.json', protocol=dict(
                    training_seasons=['2022-2023','2023-2024','2024-2025'], evaluation_season='2025-2026',
                    inputs='Same revised training data as paired finalists, with latest target-history week hidden during fitting and inner validation. Covariates unchanged.',
                    labels='Unchanged future local flu ED proportions on the main 90-location panel.',
                    evaluation_inputs='Identical revised and strictly before-Wednesday archived replay as paired finalists.',
                    selection='Predeclared reporting-delay ablation; no tuning or choosing mixture weights on confirmation outcomes.'))
    state['delay_confirmation'] = name
    save(state_path, state)
    launch_score(name, root)
    return name


def eligible(table):
    """Require the same four development seeds for both whole-season metrics."""
    table = table[table.horizons.astype(str).eq('0-33') & table.metric.isin(METRICS)].copy()
    assert table.evaluation_season.eq('2024-2025').all()
    assert table.training_seasons.eq('2022-2023;2023-2024').all()
    assert table.final_target_date.eq('2025-06-14').all()
    assert not table.ensemble_comparison.astype(str).str.lower().eq('true').any()
    assert np.isfinite(table.value).all()
    rows = []
    for (name, scenario), group in table.groupby(['name', 'scenario']):
        if any(set(group[group.metric.eq(metric)].seed) != {42, 43, 44, 45}
               or len(group[group.metric.eq(metric)]) != 4 for metric in METRICS):
            continue
        # High-memory pilot settings must never be relaunched under shared allocations.
        config = Scenario.from_string(scenario)
        if config.batch_size > 2 or config.members > 16:
            continue
        scores = group.groupby('metric').value.mean()
        rows.append(dict(name=name, scenario=scenario, wis=float(scores[METRICS[0]]),
                         path_energy=float(scores[METRICS[1]])))
    return rows


def freeze(state, root, plan, save, state_path):
    existing = next((r['name'] for r in state['rounds'] if r['stage'] == 'full-season-confirm'), None)
    if existing:
        state['full_season_confirmation'] = existing
        save(state_path, state)
        return existing
    record_path = root / 'full-season-frozen-selection.json'
    if record_path.exists():
        frozen = json.loads(record_path.read_text())
    else:
        ranked = []
        hashes = {}
        for rd in state['rounds']:
            if rd['stage'] not in STAGES:
                continue
            path = Path('data/experiments') / rd['name'] / 'early-season-long-horizon.csv'
            if not path.exists():
                continue
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            ranked.extend(dict(row, experiment=rd['name']) for row in eligible(pd.read_csv(path)))
        if not ranked:
            raise RuntimeError('Full-season freeze requires complete four-seed development WIS and path scores')
        chosen = {}
        for metric in ['wis', 'path_energy']:
            row = min(ranked, key=lambda x: (x[metric], x['scenario']))
            chosen.setdefault(row['scenario'], dict(row, selected_by=metric))
        reference = json.loads((root / 'round-057-full-season-memory.json').read_text())['candidates']['direct_local_training_weekly_loss']
        candidates = {f'full_season_finalist_{i+1}': row['scenario'] for i, row in enumerate(chosen.values())}
        if reference not in candidates.values():
            candidates['full_season_direct_reference'] = reference
        # Revised-input ranking cannot establish which history gap is operationally best.
        # Freeze matched gap/no-gap fits before seeing archived confirmation results.
        for label, scenario in list(candidates.items()):
            config = Scenario.from_string(scenario)
            assert config.training_target_lag in {0, 1}
            paired = replace(config, training_target_lag=1-config.training_target_lag).scenario_string
            if paired not in candidates.values():
                candidates[label + '_paired_history_gap'] = paired
        frozen = dict(frozen_at=datetime.now(timezone.utc).isoformat(), source_sha256=hashes,
                      selection_season='2024-2025', candidates=candidates, selected=list(chosen.values()),
                      eligible=ranked, criterion='Best mean horizon 0-33 WIS and best mean intact-path energy; four development seeds; deduplicate scenarios; add direct reference and matched training-history gap/no-gap variants. Revised development histories only; paired treatments predeclared before operational confirmation.')
        save(record_path, frozen)
    name = plan(state, frozen['candidates'], {}, [42,43,44,45,46], stage='full-season-confirm',
                problem='problems/metrocast-flu-full-season-confirm.json', protocol=dict(
                    training_seasons=['2022-2023','2023-2024','2024-2025'], evaluation_season='2025-2026',
                    inputs='Revised training histories; per-scenario training_target_lag masks fitting and inner-validation target tails only. Existing covariate release lag retained.',
                    labels='Unchanged future local flu ED proportions; scenario-specific historical ILI or state ED pretraining.',
                    evaluation_inputs='Revised 2025-26 histories initially; separately report archived-input replay against matched MetroCast ensemble.',
                    selection='Frozen 2024-25 whole-season WIS/path energy; never select, tune or choose ensemble weights on 2025-26 confirmation outcomes.'))
    state['full_season_confirmation'] = name
    save(state_path, state)
    launch_score(name, root)
    return name
