"""Export California 'Flu hosp admits' sample trajectories from current-season fits.

Fits come from the metrocast-current-california problem (trained on all weeks before
2026-08-01). The context ends at the panel's last week; the first forecast week is the
Hub's horizon -1 (reference date minus one week). Equal mixture over the chosen
recipes and their seeds: 100 whole trajectories drawn at random from all fits' pooled draws, the
same draws across weeks and locations. (Until 18 Nov 2026 each fit gave ceil(100/n_fits) draws
at indices seeded by the fit's seed only, so fits sharing a seed shared indices; with 45 fits the
135 draws came from 5 index sets, which skewed the 14 Nov California median.)
Weeks past the Hub's last target date are dropped.

--anchor ALPHA (added 2026-11-18) scales each fit's whole trajectories, per location, by
(last observed week / that fit's week -1 median)^ALPHA. The 14 Nov file's week -1 came in 26%
low; on the four held-out seasons of metrocast-ca-r03, ALPHA=0.5 cut week -1 WIS by 32% and
weeks 0-3 by 8-18%, for all 18 recipes and all four seasons (scripts/anchor_ca_backtest.py).
--growth G multiplies the anchor level by G, the NHSN California growth into week -1 (NHSN is
published for that week by the Wednesday deadline). With --anchor 1, revised NHSN growth cut the
9 submitted recipes' mean WIS over weeks -1..3 from 56.5 (as is) and 50.3 (half anchor) to 38.0,
in every held-out season (scripts/anchor_ca_nhsn_backtest.py; optimistic, since real-time NHSN
first reports are revised up later).
"""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path

import numpy as np
import torch

from chromantis.dataset.build import load
from chromantis.dataset.episodes import episodes
from chromantis.experiment.planner import collect
from chromantis.experiment.training import evaluate
from chromantis.metrocast import write_samples
from chromantis.model.network import load_model
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem


def inference_episode(panel, problem, scenario):
    panel = dict(panel)
    last = date.fromisoformat(str(panel['dates'][-1]))
    pad = max(problem.horizons)
    panel['dates'] = np.concatenate([panel['dates'], np.array([last+timedelta(weeks=i) for i in range(1, pad+1)], dtype='datetime64[D]')])
    for key in ('targets', 'covariates', 'covariates_national'):
        x = panel[key]
        panel[key] = np.concatenate([x, np.full((pad, *x.shape[1:]), np.nan, dtype=x.dtype)])
    found = [e for e in episodes(panel, problem, problem.input_names(scenario.input_set), scenario.lookback, 'scheduled_final',
                                 problem.covariate_names(scenario.covariate_set), horizons=problem.horizons, require_labels=False)
             if e['context_dates'][-1] == last.isoformat()]
    assert len(found) == 1 and not found[0]['target_available'].any()
    return found[0]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-e', '--experiment', required=True)
    p.add_argument('--recipes', nargs='+', required=True)
    p.add_argument('--reference', required=True, help='Saturday reference date of the round')
    p.add_argument('--out', required=True)
    p.add_argument('--anchor', type=float, default=0.0, help='0 = off; 0.5 = half anchor on the last observed week')
    p.add_argument('--growth', type=float, default=1.0, help='anchor level = last observed week x this growth (NHSN)')
    a = p.parse_args()
    folder = Path('data/experiments')/a.experiment
    records = [r for r in collect(folder) if r['name'] in a.recipes]
    assert records and all(r['status'] == 'complete' for r in records), 'fits missing or incomplete'
    assert {r['name'] for r in records} == set(a.recipes)
    tasks = json.loads(Path('data/metrocast/source/tasks.json').read_text())
    task = next(t for t in tasks['rounds'][-1]['model_tasks'] if 'Flu hosp admits' in (t['task_ids']['target'].get('optional') or []))
    valid = set(task['task_ids']['target_end_date']['optional'])
    torch.set_num_threads(4)
    draws, provenance, locations, dates = [], [], None, None
    for r in sorted(records, key=lambda r: (r['name'], r['seed'])):
        run = folder/r['attempt']
        manifest = json.loads((run/'manifest.json').read_text())
        problem = Problem.load(manifest['problem'])
        scenario = Scenario.from_string(r['scenario'])
        panel = load(problem.panel)
        episode = inference_episode(panel, problem, scenario)
        assert dates is None or list(episode['target_dates']) == dates
        locations, dates = list(episode['locations']), list(episode['target_dates'])
        model = load_model(torch.load(run/f"eval_{manifest['folds'][0]}/model.pt", map_location='cpu', weights_only=False))
        torch.manual_seed(r['seed']+1000)
        cache = Path(a.out).parent/'fits'/f"{r['name']}-s{r['seed']}"
        cache.mkdir(parents=True, exist_ok=True)
        evaluate(model, [episode], 128, 'cpu', cache, keep_samples=True)
        with np.load(cache/'forecasts.npz') as f:
            x = f['samples'][0, :, :, 0, :]
        if a.anchor:
            plocs = [str(v) for v in panel['locations']]
            last = np.asarray(panel['targets'])[-1, [plocs.index(l) for l in episode['locations']], 0]*a.growth
            assert np.isfinite(last).all()
            x = x*((last/np.median(x[:, 0], axis=0))**a.anchor)[None, None, :]
        draws.append(x)  # all draws; write_samples takes 100 at random from the pool (equal weight per fit)
        provenance.append(dict(recipe=r['name'], seed=r['seed'], scenario=r['scenario'], checkpoint=str(run)))
    x = np.concatenate(draws)
    reference = date.fromisoformat(a.reference)
    first = (date.fromisoformat(dates[0])-reference).days//7
    assert first == -1, f'first forecast week {dates[0]} is not reference-1 week'
    keep = [i for i, d in enumerate(dates) if d in valid]
    assert keep == list(range(len(keep)))
    x = x[:, keep]
    write_samples(x, locations, a.reference, a.out, target='Flu hosp admits', first_horizon=first)
    q = np.quantile(x, [.1, .5, .9], axis=0)
    summary = {loc: {d: [round(float(v), 1) for v in q[:, j, i]] for j, d in enumerate(dates[:5])} for i, loc in enumerate(locations)}
    Path(a.out).with_suffix('.json').write_text(json.dumps(dict(reference_date=a.reference, weeks=[dates[i] for i in keep],
        recipes=a.recipes, anchor=a.anchor, growth=a.growth, fits=provenance, draws_per_fit=len(draws[0]), panel=problem.panel,
        quantiles_10_50_90_first_five_weeks=summary), indent=2)+'\n')
    print(a.out, x.shape)


if __name__ == '__main__':
    main()
