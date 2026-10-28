"""Cluster-side branching search using the common planner, dispatcher and scorer."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import random
import shlex
import subprocess
import sys

import pandas as pd

from chromantis.experiment.planner import collect, read_jobs, scenario_directory
from chromantis.experiment.provenance import save
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem

ROOT = Path('experiments/metrocast-20261019')
STATE = ROOT / 'tree.json'
STOP = datetime(2026, 10, 21, 13, 30, tzinfo=timezone.utc).timestamp()
BASE = ROOT / 'round-00.json'


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return dict(stop_utc='2026-10-21T13:30:00+00:00', rounds=[], seen=[], confirmation=None)


def commands(experiment, study, problem):
    lines = [
        f'.venv/bin/python -m chromantis.experiment.planner plan -e {experiment} --problem {problem} --study {study} --device cuda',
        f'LANES=4 GPUS=6 sbatch --job-name={experiment} --array=0-3 scripts/jlessler.sbatch {experiment}',
        f'LANES=8 GPUS=6 sbatch --job-name={experiment} --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch {experiment}',
        f'.venv/bin/python -m chromantis.experiment.planner status -e {experiment}',
        f'.venv/bin/python -m chromantis.experiment.planner rank -e {experiment} --allow-incomplete --no-report',
    ]
    ledger = ROOT / 'manager-commands.sh'
    new = not ledger.exists()
    with ledger.open('a') as out:
        if new:
            out.write('# Run on Longleaf. Do not re-plan completed experiments or launch duplicate workers.\n'
                      'cd /hickory/proj/jlessler/projects/tapestry-all/metrocast-20261019\n'
                      'export PYTHONPATH="$PWD/src"\n')
        out.write(f'\n# {experiment}; actual execution uses the already queued metrocast_tree.sbatch workers.\n')
        out.write('\n'.join(lines) + '\n')
    return lines


def plan(state, candidates, parents, seeds, stage='screen', problem=None, protocol=None):
    number = len(state['rounds'])
    name = f'metrocast-{stage}-r{number:03d}'
    study = ROOT / f'round-{number:03d}-{stage}.json'
    problem = problem or f'problems/metrocast-flu-{"confirm" if stage == "confirm" else "screen"}.json'
    description = dict(
        seeds=seeds, candidates=candidates, parents=parents,
        training_seasons=['2022-2023', '2023-2024'] + (['2024-2025'] if stage == 'confirm' else []),
        evaluation_season='2025-2026' if stage == 'confirm' else '2024-2025',
        inputs='latest revised local flu ED histories; optional own-state ED history',
        labels='future observed local flu ED proportions; pretraining labels stated by each scenario',
        selection='WIS on 2024-25 only; lower is better; confirmation outcomes never enter search',
    )
    description.update(protocol or {})
    study.write_text(json.dumps(description, indent=2) + '\n')
    lines = commands(name, study, problem)
    result = subprocess.run(shlex.split(lines[0]), text=True, capture_output=True)
    with (ROOT / 'planning.log').open('a') as out:
        out.write(result.stdout + result.stderr)
    result.check_returncode()
    state['rounds'].append(dict(name=name, stage=stage, study=str(study), parents=parents))
    state['seen'] = sorted(set(state['seen']) | set(candidates.values()))
    if stage == 'confirm':
        state['confirmation'] = name
    save(STATE, state)
    return name


def pending(name):
    path = Path('data/experiments') / name
    d = path / 'dispatch.json'
    if not d.exists():
        return True
    state = json.loads(d.read_text())
    return any(v == 'pending' for task in state['tasks'].values() for v in task['seeds'].values())


def results(state):
    """Only four-seed results on the development season can choose parents."""
    with (ROOT / 'results.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _results(state)


def _results(state):
    rows = []
    for rd in state['rounds']:
        if rd['stage'] != 'screen':
            continue
        folder = Path('data/experiments') / rd['name']
        dispatch = folder / 'dispatch.json'
        tick = dispatch.stat().st_mtime_ns if dispatch.exists() else 0
        cached = folder / 'development-records.json'
        if cached.exists():
            prior = json.loads(cached.read_text())
            if prior['dispatch_mtime_ns'] == tick:
                rows.extend(prior['rows'])
                continue
        local = []
        for record in collect(folder):
            if record['status'] != 'complete':
                continue
            cache = folder / record['attempt'] / 'scores-raw.csv'
            if not cache.exists():
                continue
            score = pd.read_csv(cache)
            score = score[(score.history == 'raw') & (score.scale == 'natural') &
                          (score.geography == 'locations')]
            if len(score) != 1 or not pd.notna(score.mean_wis.iloc[0]):
                continue
            local.append(dict(experiment=rd['name'], name=record['name'], scenario=record['scenario'],
                              seed=record['seed'], wis=float(score.mean_wis.iloc[0])))
        save(cached, dict(dispatch_mtime_ns=tick, rows=local))
        rows.extend(local)
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows).drop_duplicates(['scenario', 'seed'])
    summary = frame.groupby('scenario').agg(mean=('wis', 'mean'), std=('wis', 'std'),
                                            seeds=('seed', 'nunique'), name=('name', 'first'),
                                            experiment=('experiment', 'first')).reset_index()
    summary = summary[summary.seeds >= 4].sort_values('mean')
    summary.assign(wis_percentage_points=100 * summary['mean']).to_csv(ROOT / 'selection.csv', index=False)
    return summary


def family(s):
    return 'ILI pretraining' if s.ili_training != 'none' else 'state ED transfer' if s.state_pretrain_steps else 'direct local training'


def children(state, ranked):
    roots = json.loads(BASE.read_text())['candidates']
    chosen = []
    if not ranked.empty:
        # Keep distinct learning strategies alive even when one dominates the average.
        for fam in ('direct local training', 'ILI pretraining', 'state ED transfer'):
            for r in ranked.to_dict('records'):
                if family(Scenario.from_string(r['scenario'])) == fam:
                    chosen.append(r)
                    break
        chosen += [r for r in ranked.head(4).to_dict('records') if r not in chosen]
    if not chosen:
        chosen = [dict(name=k, scenario=v, mean=None) for k, v in roots.items()
                  if k in ('mlp_linear_width128', 'ili_linear_200', 'state_transfer_linear_200')]
    rng = random.Random(721 + len(state['rounds']))
    axes = dict(width=[32, 64, 128, 192, 256, 384], lookback=[6, 8, 12, 16, 20, 26, 36],
                lr=[.0002, .0005, .001, .002, .004], epochs=[80, 160, 240, 320, 480],
                ed_transform=['linear', 'fourth_root', 'logit'],
                weight_decay=[0., .0001, .001, .01],
                spatial=['none', 'pooled', 'gated_pool', 'attention'], geography=[False, True],
                dynamics=[False, True], annual_calendar=[False, True],
                location_embedding=[0, 4, 8, 16], noise=['global', 'local'],
                latent=[4, 8, 16, 32], growth_anchor=[False, True],
                signal_features=['none', 'multiscale', 'smooth_multiscale'],
                decoder_blocks=[0, 2, 3, 4], members=[16, 32, 64],
                input_normalization=['none', 'b0'], batch_size=[4, 8, 16, 32])
    out, parents = {}, {}
    seen = set(state['seen'])
    p = Problem.load('problems/metrocast-flu-screen.json')
    # Broaden the search after six rounds without a new best four-seed result.
    # These change model/training choices, never seasons, labels or evaluation inputs.
    best_round = next((i for i, rd in enumerate(state['rounds'])
                       if not ranked.empty and rd['name'] == ranked.iloc[0].experiment), len(state['rounds']))
    if len(state['rounds']) - best_round >= 6:
        direct = next(r for r in chosen if family(Scenario.from_string(r['scenario'])) == 'direct local training')
        fresh = dict(name='mlp_logit_width128', scenario=roots['mlp_logit_width128'], mean=None)
        width = rng.choice([64, 128, 256])
        probes = [
            (direct, dict(input_normalization='b0', width=width)),
            (direct, dict(spatial='attention', location_embedding=0, width=width)),
            (fresh, dict(encoder='series_mlp', decoder_blocks=0, width=width, lookback=26)),
            (fresh, dict(encoder='series_mixer', decoder_blocks=0, width=width, lookback=52)),
            (fresh, dict(lookback=52, input_normalization='b0', ed_transform='linear',
                         covariate_set='state', covariate_dropout=.25, width=width)),
            (direct, dict(batch_size=32, lr=.002, epochs=rng.choice([80, 160, 320]))),
        ]
        for r in chosen:
            s = Scenario.from_string(r['scenario'])
            if s.ili_training != 'none':
                probes.append((r, dict(ili_steps=rng.choice([1600, 3200]), ili_training='pretrain')))
            elif s.state_pretrain_steps:
                probes.append((r, dict(state_pretrain_steps=rng.choice([1600, 3200]))))
        for parent, changes in probes:
            try:
                child = replace(Scenario.from_string(parent['scenario']), **changes)
                p.validate_scenario(child)
            except ValueError:
                continue
            value = child.scenario_string
            if value in seen:
                continue
            name = f'r{len(state["rounds"]):03d}_explore{len(out):02d}'
            out[name] = value
            parents[name] = dict(parent=parent['name'], scenario=parent['scenario'],
                                 development_wis=parent['mean'], changes=changes,
                                 reason='six rounds without a new best development mean')
            seen.add(value)
    for i in range(1000):
        parent = chosen[i % len(chosen)]
        s = Scenario.from_string(parent['scenario'])
        # Half single changes for interpretable branches; half broader exploration.
        keys = rng.sample(list(axes), 1 if i % 2 else 3)
        changes = {k: rng.choice(axes[k]) for k in keys}
        if i % 7 == 0 and s.encoder == 'mlp':
            changes.update(covariate_set='state', covariate_encoder=rng.choice(['raw', 'summary', 'growth']),
                           covariate_dropout=rng.choice([0., .1, .25]))
        if i % 11 == 0 and s.ili_training == 'none' and not s.state_pretrain_steps:
            changes.update(encoder=rng.choice(['mlp', 'gru', 'conv', 'multiscale_conv', 'attention']),
                           decoder_blocks=0, growth_anchor=False)
        try:
            child = replace(s, **changes)
            p.validate_scenario(child)
        except ValueError:
            continue
        value = child.scenario_string
        if value in seen:
            continue
        name = f'r{len(state["rounds"]):03d}_child{len(out):02d}'
        out[name] = value
        parents[name] = dict(parent=parent['name'], scenario=parent['scenario'],
                             development_wis=parent['mean'], changes=changes)
        seen.add(value)
        if len(out) == 24:
            break
    if not out:
        raise RuntimeError('Search produced no new candidates')
    return out, parents


def next_round():
    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT / 'tree.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = load_state()
        now = datetime.now(timezone.utc).timestamp()
        if now >= STOP:
            return 'STOP'
        if not state['rounds']:
            return plan(state, json.loads(BASE.read_text())['candidates'], {}, [42, 43, 44, 45])
        # Confirmation is one frozen selection, scheduled eight hours before the deadline.
        if now >= STOP - 8 * 3600 and not state['confirmation']:
            ranked = results(state)
            if not ranked.empty:
                top = ranked.head(5)
                candidates = dict(zip(top.name, top.scenario))
                candidates['direct_reference'] = json.loads(BASE.read_text())['candidates']['mlp_linear_width128']
                name = plan(state, candidates, {}, [42, 43, 44, 45, 46], stage='confirm')
                from metrocast_full_season_freeze import launch_score
                launch_score(name, ROOT)
                return name
        if now >= STOP - 8 * 3600 and not state.get('full_season_confirmation'):
            from metrocast_full_season_freeze import freeze
            return freeze(state, ROOT, plan, save, STATE)
        if now >= STOP - 8 * 3600 and state.get('confirmation') and not state.get('delay_confirmation'):
            from metrocast_full_season_freeze import freeze_delay
            return freeze_delay(state, ROOT, plan, save, STATE)
        if now >= STOP - 8 * 3600 and not state.get('context_confirmation'):
            from metrocast_full_season_freeze import freeze_context
            return freeze_context(state, ROOT, plan, save, STATE)
        if now >= STOP - 8 * 3600 and not state.get('california_confirmation'):
            from metrocast_full_season_freeze import freeze_california
            return freeze_california(state, ROOT, plan, save, STATE)
        if now >= STOP - 8 * 3600 and not state.get('utah_confirmation'):
            from metrocast_full_season_freeze import freeze_utah
            return freeze_utah(state, ROOT, plan, save, STATE)
        if now >= STOP - 8 * 3600 and len(state.get('current_refits', {})) < 4:
            from metrocast_current_refit import plan_next
            return plan_next(state, ROOT, plan, save, STATE)
        if state.get('full_season_confirmation') and pending(state['full_season_confirmation']):
            return state['full_season_confirmation']
        if state['confirmation'] and pending(state['confirmation']):
            return state['confirmation']
        if state.get('delay_confirmation') and pending(state['delay_confirmation']):
            return state['delay_confirmation']
        for key in ['context_confirmation', 'california_confirmation', 'utah_confirmation']:
            if state.get(key) and pending(state[key]):
                return state[key]
        for name in state.get('current_refits', {}).values():
            if pending(name):
                return name
        # Finish submission and ensemble experiments before replenishing the broad screen.
        for rd in sorted(state['rounds'], key=lambda r: r['stage'] == 'screen'):
            if pending(rd['name']):
                return rd['name']
        ranked = results(state)
        # Stop runaway branching if the implementation or cluster is failing.
        if ranked.empty and len(state['rounds']) >= 2:
            raise RuntimeError('No complete four-seed candidate after two rounds; inspect failures')
        candidates, parents = children(state, ranked)
        return plan(state, candidates, parents, [42, 43, 44, 45])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['next', 'status', 'rank'])
    args = parser.parse_args()
    if args.command == 'next':
        print(next_round())
    else:
        state = load_state()
        for rd in state['rounds']:
            rows = collect(Path('data/experiments') / rd['name'])
            print(rd['name'], pd.Series([r['status'] for r in rows]).value_counts().to_dict())
            if args.command == 'rank' and any(r['status'] == 'complete' for r in rows):
                subprocess.run([sys.executable, '-m', 'chromantis.experiment.planner', 'rank',
                                '-e', rd['name'], '--allow-incomplete', '--no-report'], check=True)
        ranked = results(state)
        if not ranked.empty:
            print(ranked[['name', 'mean', 'std', 'seeds']].head(12).to_string(index=False))


if __name__ == '__main__':
    main()
