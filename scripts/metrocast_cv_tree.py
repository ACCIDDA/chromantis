"""Season-CV tree search for MetroCast (2026-10-21).

Replaces the development-season screen of metrocast_tree.py, whose revised-input 2024-25 WIS
picked models that lost to the MetroCast ensemble on 2025-26. Every candidate here hides the
latest history week in training and is scored by leave-one-season-out CV over 2022-23..2025-26:
2025-26 with archived before-Wednesday inputs against the actual ensemble, the other seasons with
the latest week hidden at evaluation. Objective: mean over folds of log(WIS / reference WIS).
"""
import argparse, fcntl, json, os, random, subprocess, sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from chromantis.experiment.planner import collect
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem

# TRACK=short: horizons 0-3, objective described above. TRACK=long (added 2026-10-22): full-season
# models (34 horizons), revised inputs in every held-out season, objective on horizons 4-33 only.
TRACK = os.environ.get('TRACK', 'short')
ROOT = Path('experiments/metrocast-cv-20261021' if TRACK == 'short' else 'experiments/metrocast-cv-long-20261022')
STATE = ROOT / 'tree.json'
QUEUE = ROOT / 'queue.txt'          # extra experiments to run first, one per line
PROBLEM = 'problems/metrocast-flu-cv.json' if TRACK == 'short' else 'problems/metrocast-flu-cv-long.json'
PREFIX = 'metrocast-cv-r' if TRACK == 'short' else 'metrocast-cvlong-r'
STOP = datetime(2026, 10, 22, 12, 40, tzinfo=timezone.utc).timestamp()
SEEDS = [42, 43, 44, 45] if TRACK == 'short' else [42, 43, 44]
AXES = dict(width=[64, 96, 128, 192, 256], lookback=[8, 12, 16, 26, 52],
            lr=[.0005, .001, .002, .004], epochs=[80, 120, 160, 240, 320],
            ed_transform=['linear', 'fourth_root', 'logit'], weight_decay=[0., .0001, .001, .01],
            spatial=['none', 'pooled', 'gated_pool', 'attention'], geography=[False, True],
            location_embedding=[0, 4, 8, 16], noise=['global', 'local'], latent=[4, 8, 16, 32],
            signal_features=['none', 'multiscale', 'smooth_multiscale'], decoder_blocks=[0, 2, 3],
            members=[16, 32, 64], input_normalization=['none', 'b0'], batch_size=[8, 16, 32],
            training_target_lag=[0, 1, 2], covariate_dropout=[0., .1, .25, .5],
            covariate_encoder=['raw', 'summary', 'growth'])
if TRACK == 'long':
    AXES.update(path_loss_weight=[0., .25, .5, 1., 2.], lookback=[26, 52, 78], batch_size=[2, 4, 8, 16],
                epochs=[80, 160, 320], annual_calendar=[False, True])


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else dict(rounds=['metrocast-cv-r000'], seen=[])


def save_state(state):
    STATE.write_text(json.dumps(state, indent=1) + '\n')


def pending(name):
    d = Path('data/experiments') / name / 'dispatch.json'
    if not d.exists():
        return True
    tasks = json.loads(d.read_text())['tasks'].values()
    return any(v == 'pending' for t in tasks for v in t['seeds'].values())


def unscored():
    from metrocast_cv_score import todo
    return todo()


def ranked():
    path = ROOT / 'cv-ranking.csv'
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def children(state, table, number):
    rng = random.Random(1021 + number)
    p = Problem.load(PROBLEM)
    seen = set(state['seen'])
    good = table[table.folds == 4].sort_values('cv_log_ratio')
    parents = good.head(6).to_dict('records')
    out, why = {}, {}
    for i in range(2000):
        parent = parents[i % len(parents)] if i % 4 else parents[0]
        s = Scenario.from_string(parent['scenario'])
        keys = rng.sample(list(AXES), 1 if i % 3 else 2)
        changes = {k: rng.choice(AXES[k]) for k in keys}
        if i % 9 == 0:   # keep the shared state-series encoder branch alive
            changes.update(covariate_set='state', covariate_encoder=rng.choice(['raw', 'summary', 'growth']))
        if i % 13 == 0:
            changes.update(state_pretrain_steps=rng.choice([400, 800, 1600]))
        if i % 17 == 0:
            changes.update(ili_units='flu_scaled', ili_steps=rng.choice([400, 800, 1600]), ili_training='pretrain',
                           ili_path='data/metrocast/historical_ili.npz')
        try:
            child = replace(s, **changes)
            p.validate_scenario(child)
        except (ValueError, TypeError):
            continue
        value = child.scenario_string
        if value in seen:
            continue
        name = f'r{number:03d}_c{len(out):02d}'
        out[name] = value
        why[name] = dict(parent=parent['name'], parent_cv_log_ratio=parent['cv_log_ratio'],
                         changes={k: str(v) for k, v in changes.items()})
        seen.add(value)
        if len(out) == (24 if TRACK == 'short' else 15):
            break
    # The reference rides along in every round so seed noise between rounds can be checked.
    out[f'r{number:03d}_ref'] = state['reference']
    return out, why


def plan_round(state):
    number = len(state['rounds'])
    name = f'{PREFIX}{number:03d}'
    candidates, why = children(state, ranked(), number)
    study = ROOT / f'cv-r{number:03d}.json'
    study.write_text(json.dumps(dict(seeds=SEEDS, candidates=candidates, parents=why,
        selection='mean over four folds of log(WIS / reference WIS); lower is better'), indent=1) + '\n')
    cmd = [sys.executable, '-m', 'chromantis.experiment.planner', 'plan', '-e', name, '--problem', PROBLEM,
           '--study', str(study), '--device', 'cuda']
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    with (ROOT / 'manager-commands.sh').open('a') as f:
        f.write(f'\n# {name} (run by metrocast_cv.sbatch workers)\n{" ".join(cmd[1:]).replace("-m ", ".venv/bin/python -m ", 1)}\n'
                f'.venv/bin/python -m chromantis.experiment.planner status -e {name}\n'
                f'.venv/bin/python -m chromantis.experiment.planner rank -e {name} --allow-incomplete --no-report\n')
    state['rounds'].append(name)
    state['seen'] = sorted(set(state['seen']) | set(candidates.values()))
    save_state(state)
    return name


def other_rounds():
    """Rounds of the other track, so idle workers can help fit them (2026-10-22)."""
    path = Path('experiments/metrocast-cv-long-20261022' if TRACK == 'short' else 'experiments/metrocast-cv-20261021') / 'tree.json'
    return json.loads(path.read_text())['rounds'] if path.exists() else []


def next_work():
    # Order (2026-10-22): array task 0 scores while the others fit, so GPUs no longer idle during
    # scoring; then own pending fits, then the other track's pending fits, then a new own round.
    with (ROOT / 'tree.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if datetime.now(timezone.utc).timestamp() >= STOP:
            return 'STOP'
        state = load_state()
        scorer = os.environ.get('SLURM_ARRAY_TASK_ID', '0') == '0'
        if scorer and unscored():
            return 'SCORE'
        queue = [l.strip() for l in QUEUE.read_text().splitlines() if l.strip()] if QUEUE.exists() else []
        for name in queue + state['rounds']:
            if pending(name):
                return name
        for name in other_rounds():
            if pending(name):
                return name
        table = ranked()
        done = set(table.experiment) if not table.empty else set()
        unfinished = [r for r in state['rounds'] if r not in done]
        if not table.empty and len(unfinished) <= 1:
            return plan_round(state)
        return 'SCORE' if unscored() else 'WAIT'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('command', choices=['next', 'status'])
    a = ap.parse_args()
    if a.command == 'next':
        print(next_work())
    else:
        for r in load_state()['rounds']:
            rows = collect(Path('data/experiments') / r)
            print(r, pd.Series([x['status'] for x in rows]).value_counts().to_dict())
        t = ranked()
        if not t.empty:
            print(t.head(15).to_string(index=False))
