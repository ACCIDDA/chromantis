"""Cluster-side branching search for the BDBV Ebola forecaster (common planner, dispatcher, scorer).

Every candidate is one Chromantis recipe trained on weekly case histories of West Africa
2014-15, Kivu 2018-20 and the BDBV 2026 weeks before each scoring window (finalized latest
values as inputs and labels). It is scored on the BDBV 2026 windows 6 Jun-18 Jul and
25 Jul-29 Aug (problems/ebola-bdbv-screen.json): mean WIS over BDBV locations of weekly cases
1-4 weeks ahead, natural scale, task-weighted over both windows; lower is better. Parents are
chosen from four-seed means only. Three hours before STOP the five best recipes and the root
reference are frozen and rerun with five seeds on the held-back window 5 Sep-3 Oct
(problems/ebola-bdbv-confirm.json), whose outcome never enters the search.
"""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import random
import shlex
import subprocess
import sys

import pandas as pd

from chromantis.experiment.planner import collect
from chromantis.experiment.provenance import save
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem

ROOT = Path('experiments/ebola-20261026')
STATE = ROOT / 'tree.json'
STOP_ISO = '2026-10-28T03:00:00+00:00'
STOP = datetime.fromisoformat(STOP_ISO).timestamp()
BASE = ROOT / 'round-00.json'
SCREEN = 'problems/ebola-bdbv-screen.json'
CONFIRM = 'problems/ebola-bdbv-confirm.json'
REFERENCE = 'mlp_width64'


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return dict(stop_utc=STOP_ISO, rounds=[], seen=[], confirmation=None)


def commands(experiment, study, problem):
    lines = [
        f'.venv/bin/python -m chromantis.experiment.planner plan -e {experiment} --problem {problem} --study {study} --device cuda',
        f'LANES=4 GPUS=6 sbatch --job-name={experiment} --array=0-3 scripts/jlessler.sbatch {experiment}',
        f'.venv/bin/python -m chromantis.experiment.planner status -e {experiment}',
        f'.venv/bin/python -m chromantis.experiment.planner rank -e {experiment} --allow-incomplete --no-report',
    ]
    ledger = ROOT / 'manager-commands.sh'
    new = not ledger.exists()
    with ledger.open('a') as out:
        if new:
            out.write('# Run on Longleaf. Do not re-plan completed experiments or launch duplicate workers.\n'
                      'cd /hickory/proj/jlessler/projects/tapestry-all/ebola-20261026\n'
                      'export PYTHONPATH="$PWD/src"\n')
        out.write(f'\n# {experiment}; actual execution uses the already queued ebola_tree.sbatch workers.\n')
        out.write('\n'.join(lines) + '\n')
    return lines


def plan(state, candidates, parents, seeds, stage='screen'):
    number = len(state['rounds'])
    name = f'ebola-{stage}-r{number:03d}'
    study = ROOT / f'round-{number:03d}-{stage}.json'
    problem = CONFIRM if stage == 'confirm' else SCREEN
    description = dict(
        seeds=seeds, candidates=candidates, parents=parents,
        training='weekly cases, West Africa 2014-15 districts/countries/total, Kivu 2018-20 health zones/'
                 'provinces/total, and BDBV 2026 weeks before the scoring window; latest values',
        evaluation='BDBV 2026 ' + ('5 Sep-3 Oct' if stage == 'confirm' else '6 Jun-18 Jul and 25 Jul-29 Aug')
                   + '; inputs are latest (finalized) values; horizons 1-4 weeks',
        selection='task-weighted mean WIS over BDBV locations, natural scale; lower is better; '
                  'the confirmation window never enters the search',
    )
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
    d = Path('data/experiments') / name / 'dispatch.json'
    if not d.exists():
        return True
    state = json.loads(d.read_text())
    return any(v == 'pending' for task in state['tasks'].values() for v in task['seeds'].values())


def scores(stage, state):
    rows = []
    for rd in state['rounds']:
        if rd['stage'] != stage:
            continue
        folder = Path('data/experiments') / rd['name']
        for record in collect(folder):
            cache = folder / record['attempt'] / 'scores-raw.csv' if record['status'] == 'complete' else None
            if cache is None or not cache.exists():
                continue
            s = pd.read_csv(cache)
            s = s[(s.history == 'raw') & (s.scale == 'natural') & (s.geography == 'locations')]
            if s.empty or not s.mean_wis.notna().all():
                continue
            rows.append(dict(experiment=rd['name'], name=record['name'], scenario=record['scenario'],
                             seed=record['seed'], wis=float((s.mean_wis * s.tasks).sum() / s.tasks.sum())))
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows).drop_duplicates(['scenario', 'seed'])
    return frame.groupby('scenario').agg(mean=('wis', 'mean'), std=('wis', 'std'), seeds=('seed', 'nunique'),
                                         name=('name', 'first'), experiment=('experiment', 'first')).reset_index()


def results(state):
    with (ROOT / 'results.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        summary = scores('screen', state)
        if summary.empty:
            return summary
        summary = summary[summary.seeds >= 4].sort_values('mean')
        summary.to_csv(ROOT / 'selection.csv', index=False)
        return summary


def family(s):
    return 'spatial' if s.spatial != 'none' else 'temporal' if s.encoder != 'mlp' else 'mlp'


def children(state, ranked):
    roots = json.loads(BASE.read_text())['candidates']
    chosen = []
    # Keep each encoder family alive even when one dominates the average.
    for fam in ('mlp', 'temporal', 'spatial'):
        best = next((r for r in ranked.to_dict('records') if family(Scenario.from_string(r['scenario'])) == fam), None)
        if best:
            chosen.append(best)
    chosen += [r for r in ranked.head(4).to_dict('records') if r not in chosen]
    rng = random.Random(1026 + len(state['rounds']))
    axes = dict(width=[32, 64, 96, 128, 192, 256], lookback=[4, 6, 8, 10, 12, 16, 20, 26],
                lr=[.0003, .0005, .001, .002, .004], epochs=[40, 80, 160, 240, 320, 480],
                count_transform=['fourth_root', 'sqrt', 'log1p'], weight_decay=[0., .0001, .001, .01],
                spatial=['none', 'pooled', 'gated_pool', 'attention'], dynamics=[False, True],
                noise=['global', 'local'], latent=[4, 8, 16, 32], growth_anchor=[False, True],
                signal_features=['none', 'multiscale', 'smooth_multiscale'], decoder_blocks=[0, 2, 3, 4],
                members=[16, 32, 64], input_normalization=['none', 'b0'], batch_size=[4, 8, 16, 32],
                covariate_set=['none', 'parent', 'outbreak', 'parent+outbreak'],
                covariate_encoder=['raw', 'summary', 'growth'], covariate_dropout=[0., .1, .25],
                log_loss_weight=[0., .25, .5, 1.], location_embedding=[0, 4, 8])
    out, parents = {}, {}
    seen = set(state['seen'])
    p = Problem.load(SCREEN)
    best_round = next((i for i, rd in enumerate(state['rounds']) if rd['name'] == ranked.iloc[0].experiment),
                      len(state['rounds']))
    stalled = len(state['rounds']) - best_round >= 5
    for i in range(2000):
        parent = chosen[i % len(chosen)]
        s = Scenario.from_string(parent['scenario'])
        # Half single changes for interpretable branches; half broader exploration; after five
        # rounds without a new best, also restart from a fresh encoder with wider moves.
        keys = rng.sample(list(axes), 1 if i % 2 else (5 if stalled else 3))
        changes = {k: rng.choice(axes[k]) for k in keys}
        if i % 9 == 0 or (stalled and i % 3 == 0):
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
        parents[name] = dict(parent=parent['name'], scenario=parent['scenario'], development_wis=parent['mean'],
                             changes={k: v for k, v in changes.items()}, stalled=stalled)
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
        if now >= STOP - 3 * 3600 and not state['confirmation']:
            ranked = results(state)
            if not ranked.empty:
                top = ranked.head(5)
                candidates = dict(zip(top.name, top.scenario))
                candidates['root_reference'] = json.loads(BASE.read_text())['candidates'][REFERENCE]
                return plan(state, candidates, {}, [42, 43, 44, 45, 46], stage='confirm')
        if state['confirmation'] and pending(state['confirmation']):
            return state['confirmation']
        if state['confirmation']:
            return 'STOP'
        for rd in state['rounds']:
            if pending(rd['name']):
                return rd['name']
        ranked = results(state)
        if ranked.empty:
            raise RuntimeError('No complete four-seed candidate after the root round; inspect failures')
        candidates, parents = children(state, ranked)
        return plan(state, candidates, parents, [42, 43, 44, 45])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['next', 'status'])
    args = parser.parse_args()
    if args.command == 'next':
        print(next_round())
        return
    state = load_state()
    for rd in state['rounds']:
        rows = collect(Path('data/experiments') / rd['name'])
        print(rd['name'], pd.Series([r['status'] for r in rows], dtype=str).value_counts().to_dict())
    ranked = results(state)
    if not ranked.empty:
        print(ranked[['name', 'mean', 'std', 'seeds', 'experiment']].head(12).to_string(index=False))
    confirm = scores('confirm', state)
    if not confirm.empty:
        print('confirmation (5 Sep-3 Oct):')
        print(confirm.sort_values('mean')[['name', 'mean', 'std', 'seeds']].to_string(index=False))


if __name__ == '__main__':
    main()
