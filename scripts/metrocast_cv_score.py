"""Score season-CV runs (2026-10-21) and rebuild the CV ranking.

Each run trains one model per held-out season (the other three of 2022-23..2025-26).
- 2025-26 held out: inputs replayed from Hub archive versions dated on or before each Wednesday
  deadline, scored on the tasks the actual MetroCast ensemble forecast (score_metrocast_confirmation).
  Every Wednesday archive version already holds the Saturday four days earlier, so this is the data
  the ensemble had. The earlier confirmation used versions strictly before Wednesday, which dropped
  that latest week and favoured models trained with it hidden.
- Other held-out seasons: no archive exists; inputs are the latest revised histories through the
  Saturday before each deadline.
WIS uses hub horizons 0-3 (model horizons 1-4), natural scale, lower is better.
"""
import argparse, json, os, time
from datetime import date, timedelta
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
from score_metrocast_confirmation import LEVELS, ensemble_tasks, prepare_archive, replay_episode

TRACK = os.environ.get('TRACK', 'short')
ROOT = Path('experiments/metrocast-cv-20261021' if TRACK == 'short' else 'experiments/metrocast-cv-long-20261022')
# Long track (2026-10-22): full-season models, revised inputs in every fold, no ensemble exists for
# long horizons; cells keep horizons 4-33 only, so the objective is long-horizon WIS.
ARCHIVED = '2025-2026' if TRACK == 'short' else None
HORIZONS = slice(0, 4) if TRACK == 'short' else slice(4, None)
KEY = ['reference_date', 'location', 'horizon']


def rounds():
    state = json.loads((ROOT / 'tree.json').read_text())
    return state['rounds']


def todo():
    out = []
    for name in rounds():
        folder = Path('data/experiments') / name
        for r in collect(folder):
            run = folder / r['attempt'] if r.get('attempt') else None
            if r['status'] == 'complete' and not (run / 'cv-cells.parquet').exists():
                out.append((name, r))
    return out


def claim(run):
    path = run / 'cv-score.claim'
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        if time.time() - path.stat().st_mtime > 1800:   # stale claim from a killed scorer
            path.touch()
            return True
        return False



def cells(path):
    with np.load(path / 'forecasts.npz') as f:
        idx = [int(np.flatnonzero(np.isclose(f['quantile_levels'], q))[0]) for q in LEVELS]
        q = f['quantiles'][idx, :, HORIZONS, 0, :]
        offset = HORIZONS.start
        n, h, l = q.shape[1:]
        refs = [(date.fromisoformat(str(v)) + timedelta(days=7)).isoformat() for v in f['context_end']]
        d = pd.DataFrame(dict(reference_date=np.repeat(refs, h * l), location=np.tile(f['locations'], n * h),
                              horizon=np.tile(np.repeat(np.arange(h) + offset, l), n),
                              observed=f['truth'][:, HORIZONS, 0, :].reshape(-1),
                              available=f['mask'][:, HORIZONS, 0, :].reshape(-1)))
        qcols = [f'q{x:g}' for x in LEVELS]
        d[qcols] = q.reshape(len(LEVELS), -1).T
    d = d[d.available].copy()
    d['wis'] = quantile_scores(d[qcols].to_numpy(), d.observed.to_numpy(), LEVELS).wis.to_numpy()
    return d


def score_run(folder, record, device, ensemble, archive, metadata):
    run = folder / record['attempt']
    manifest = json.loads((run / 'manifest.json').read_text())
    problem = Problem.load(manifest['problem'])
    scenario = Scenario.from_string(record['scenario'])
    covariates = problem.covariate_names(scenario.covariate_set)
    panel = load(problem.panel)
    parts = []
    for fold in manifest['folds']:
        fdir = run / f'eval_{fold}'
        out = fdir / ('cv-archived-wednesday-inputs' if fold == ARCHIVED else 'cv-revised-inputs')
        if not (out / 'forecasts.npz').exists():
            eps = score_episodes(panel, problem, scenario, fold)
            if fold == ARCHIVED:
                refs = set(ensemble.reference_date)
                eps = [replay_episode(e, archive, metadata, None, covariates) for e in eps
                       if (date.fromisoformat(str(e['context_dates'][-1])) + timedelta(days=7)).isoformat() in refs]
            model = load_model(torch.load(fdir / 'model.pt', map_location='cpu', weights_only=False)).to(device)
            torch.manual_seed(record['seed'])
            out.mkdir(exist_ok=True)
            evaluate(model, eps, 512, device, out)
            del model
        c = cells(out)
        if fold == ARCHIVED:
            e = ensemble.rename(columns={'target_end_date': 'ensemble_target_end_date'})
            c = c.merge(e, on=KEY, validate='one_to_one')
            c['ensemble_wis'] = quantile_scores(c[[f'ensemble_q{x:g}' for x in LEVELS]].to_numpy() / 100,
                                                c.observed.to_numpy(), LEVELS).wis.to_numpy()
        parts.append(c[KEY + ['wis'] + (['ensemble_wis'] if 'ensemble_wis' in c else [])].assign(fold=fold))
    pd.concat(parts).to_parquet(run / 'cv-cells.parquet', index=False)


def rank():
    rows = []
    for name in rounds():
        folder = Path('data/experiments') / name
        for r in collect(folder):
            if r['status'] == 'complete' and r.get('attempt') and (folder / r['attempt'] / 'cv-cells.parquet').exists() \
                    and (folder / r['attempt'] / 'cv-cells.parquet').stat().st_size > 0:
                rows.append(dict(experiment=name, name=r['name'], scenario=r['scenario'], seed=r['seed'],
                                 path=folder / r['attempt'] / 'cv-cells.parquet'))
    if not rows:
        return
    runs = pd.DataFrame(rows).drop_duplicates(['scenario', 'seed'])
    state = json.loads((ROOT / 'tree.json').read_text())
    if state['reference'] not in set(runs.scenario):
        return   # nothing to rank against until the reference recipe is scored
    data = {s: pd.concat([pd.read_parquet(p) for p in g.path]) for s, g in runs.groupby('scenario')}
    ref = data[state['reference']].groupby(['fold'] + KEY).wis.mean()
    out = []
    for s, g in runs.groupby('scenario'):
        d = data[s]
        mean = d.groupby(['fold'] + KEY).wis.mean()
        joined = pd.concat([mean.rename('m'), ref.rename('r')], axis=1, join='inner')
        fold = joined.groupby('fold').sum()
        ratio = fold.m / fold.r
        row = dict(name=g.name.iloc[0], experiment=g.experiment.iloc[0], seeds=g.seed.nunique(), folds=len(ratio),
                   cv_log_ratio=float(np.log(ratio).mean()), cv_ratio=float(np.exp(np.log(ratio).mean())))
        for f, v in ratio.items():
            row[f'ratio_{f}'] = float(v)
        a = d[d.fold == ARCHIVED]
        if len(a) and 'ensemble_wis' in a:
            loc = a.groupby(['location']).agg(m=('wis', 'sum'), e=('ensemble_wis', 'sum'))
            row['ensemble_ratio_2025_26_location_mean'] = float((loc.m / loc.e).mean())
            row['ensemble_ratio_2025_26_pooled'] = float(a.wis.sum() / a.ensemble_wis.sum())
        row['scenario'] = s
        out.append(row)
    table = pd.DataFrame(out)
    table = table[table.seeds >= 3].sort_values('cv_log_ratio')
    table.to_csv(ROOT / 'cv-ranking.csv', index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--device', default='cuda')
    ap.add_argument('--max-runs', type=int, default=12)
    ap.add_argument('--rank-only', action='store_true')
    a = ap.parse_args()
    if not a.rank_only:
        torch.set_num_threads(4)
        ensemble = ensemble_tasks()[0] if ARCHIVED else None
        archive = prepare_archive(pd.read_csv('data/metrocast/source/time-series.csv'))
        # replay_episode keeps versions strictly before Wednesday; shifting each version date back one
        # day makes the Wednesday release (data through the prior Saturday) visible, as it was to the Hub.
        archive['as_of'] = (pd.to_datetime(archive.as_of) - pd.Timedelta(days=1)).dt.strftime('%Y-%m-%d')
        metadata = pd.read_csv('data/metrocast/locations.csv').set_index('location')
        done = 0
        for name, record in todo():
            run = Path('data/experiments') / name / record['attempt']
            if done >= a.max_runs or not claim(run):
                continue
            try:
                score_run(Path('data/experiments') / name, record, a.device, ensemble, archive, metadata)
                print('scored', name, record['name'], record['seed'], flush=True)
            except Exception as error:
                print('failed', name, record['name'], record['seed'], repr(error), flush=True)
                (run / 'cv-score.failed').write_text(repr(error))
                (run / 'cv-cells.parquet').write_bytes(b'')  # never retried; empty file marks the failure
                continue
            done += 1
    rank_safe()


def rank_safe():
    import fcntl
    with (ROOT / 'rank.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        rank()


if __name__ == '__main__':
    main()
