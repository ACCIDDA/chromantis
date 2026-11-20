"""Replay a submitted release's saved fits on past 2026-27 reports, as a pseudo-experiment (19 November 2026).

Production (`production/forecast.py`) refuses issuances whose outcomes are already known; this replay does the
same computation (saved network, saved trees times the release's correction_strength, `corrected` view, 512
members, seed + 1000) on every requested Wednesday report of a research panel, without that check. Output:
data/experiments/<NAME>/runs.csv and <recipe>/s<seed>/eval_2026-2027/corrected/forecasts.npz, so
scripts/score_gate_hub_truth.py scores the release's members and mixture on exactly the same tasks as research fits.
    PYTHONPATH=src .venv/bin/python scripts/replay_release.py --release production/releases/rsv-four-20261014.json \
        --campaign tapestry --panel data/processed/panel-coverage-rsv.npz --hub rsv --name rsv-replay-submitted
"""
import argparse
import csv
import json
import pickle
from pathlib import Path

import torch

from chromantis.dataset.build import load, for_hub
from chromantis.dataset.episodes import episodes
from chromantis.experiment.fit import ForecastSlice
from chromantis.experiment.training import evaluate
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem

ROOT = Path('/hickory/proj/jlessler/projects/tapestry-all')


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--release', required=True)
    a.add_argument('--campaign', required=True, help='Longleaf folder holding the release fits under data/experiments/')
    a.add_argument('--panel', required=True)
    a.add_argument('--hub', required=True)
    a.add_argument('--name', required=True)
    a.add_argument('--issuances', nargs='+', default=['2026-10-14', '2026-10-21', '2026-10-28', '2026-11-04', '2026-11-11'])
    args = a.parse_args()
    release = json.loads(Path(args.release).read_text())
    problem = Problem.load(release['problem'])
    panel = for_hub(load(args.panel), args.hub)
    strength = release.get('correction_strength', 1.0)
    out = Path('data/experiments') / args.name
    out.mkdir(parents=True, exist_ok=True)
    rows, cache = [], {}
    for recipe, members in release['recipes'].items():
        for member in members:
            path = ROOT / args.campaign / member['checkpoint'].replace('data/production-fits/', 'data/experiments/')
            meta = json.loads((path / 'manifest.json').read_text())
            scenario = Scenario.from_string(meta['scenario'])
            key = (scenario.input_set, scenario.covariate_set, scenario.lookback)
            if key not in cache:
                eps = episodes(panel, problem, problem.input_names(scenario.input_set), scenario.lookback, 'reported',
                               problem.covariate_names(scenario.covariate_set), horizons=problem.horizons, require_labels=False)
                cache[key] = [e for e in eps if e['issuance'] in args.issuances]
            eps = cache[key]
            with (path / 'nowcaster.pkl').open('rb') as f:
                trees = pickle.load(f)
            trees.strength *= strength[recipe] if isinstance(strength, dict) else strength
            eps = trees.apply_batch(eps)
            model = load_model(torch.load(path / 'model.pt', map_location='cpu', weights_only=False))
            if scenario.reconstruction_labels:
                model = ForecastSlice(model, problem.future_indices(scenario))
            attempt = f'{recipe}/s{meta["seed"]}'
            target = out / attempt / 'eval_2026-2027' / 'corrected'
            target.mkdir(parents=True, exist_ok=True)
            torch.manual_seed(meta['seed'] + 1000)
            evaluate(model, eps, 512, 'cpu', target)
            rows.append(dict(task=len(rows), name=recipe, seed=meta['seed'], status='complete', attempt=attempt, scenario=meta['scenario']))
            print(recipe, meta['seed'], flush=True)
    with (out / 'runs.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == '__main__':
    main()
