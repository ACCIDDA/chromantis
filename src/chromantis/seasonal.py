"""Season peak forecasts: FluSight's `peak week inc flu hosp` and `peak inc flu hosp` (2026-10-11).

A problem with `evaluation.kind = season_peak` names one weekly count target, a season window in
CDC epiweeks (FluSight: 40-21, week ending about 10 October to the end of May) and leave-one-season-out
folds. For every held-out season and every Saturday reference date r in the window, a model sees the
finalized history through the week ending r - 7 days and returns, for every location:

- peak week: probabilities over the window's weeks (sum to one);
- peak incidence: the 23 Hub quantiles of the season's highest weekly count.

Both come from joint season trajectories: weeks already observed are kept, the rest are drawn,
and each trajectory's maximum and argmax give one peak draw. Scores (lower is better):

- peak week: negative log score, -log p(true peak week), probability floored at 0.001;
  location-seasons whose maximum is reached in two weeks are not scored (FluSight rule);
- peak incidence: WIS of the quantiles on log(1 + count) and on counts.

Truth is the problem panel's finalized values (FluSight scores reported values).
`inputs=reported` replays Wednesday deadline histories with no finalized-value fallback,
including the observed part of each season path. A location/date is excluded if any
past week of its peak window lacks a report. Training is unchanged by this replay.

Models are recipes (a short `key=value` string, like scenarios):

- `model=climatology`: a training season's curve for the same location, drawn at random;
- `model=analogue`: training seasons weighted by how well their recent weeks, rescaled, match the
  last `match_weeks` observed weeks; the rescaled continuation of the drawn season;
- `model=recursive`: a fitted four-week model (`checkpoints`, one folder per held-out season) run
  recursively on its own sampled forecasts (sandbox/recursive-peak, 2026-10-10);
- `model=trajectory`: a fitted sampled model trained to the season's end (`checkpoints`; e.g. the
  season-peak-stage2 experiment): each member is one joint path over weeks and locations.
  `fold_problem` is the weekly problem the fold models were trained on, used when their recorded
  experiment copy is not on this machine.

`library=own` draws training seasons from the problem's panel; `library=all` also from the other
seasonal panels listed in `LIBRARIES` (e.g. NHSN seasons for the ILI-converted problem). Every
trajectory gets one lognormal level factor (`noise`).

    python -m chromantis.seasonal convert-ili
    python -m chromantis.seasonal run --problem problems/us-flu-season-peak.json --recipe model=analogue,library=all
    python -m chromantis.seasonal score data/seasonal/<problem>/<recipe>
"""
import argparse
import json
from dataclasses import dataclass, fields, asdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.dataset.build import load
from chromantis.dataset.cv import season, season_start
from chromantis.evaluation.quantiles import LEVELS
from chromantis.evaluation.standard import epiweek, quantile_scores
from chromantis.problem import Problem

OUT = Path('data/seasonal')
HISTORY_WEEKS = 8  # weeks before the window kept in season curves (summer context for early origins)
LIBRARIES = {  # seasonal panels whose seasons `library=all` may draw (problem file -> its training seasons)
    'problems/us-flu-season-peak.json': None,
    'problems/us-flu-season-peak-ili.json': None,
}
FLOOR = 1e-3


def read_panel(path):
    """A built panel (with report vintages) or a plain one (e.g. the ILI-converted panel)."""
    return load(path)


@dataclass(frozen=True)
class Recipe:
    model: str = 'analogue'
    inputs: str = 'finalized'
    library: str = 'own'
    samples: int = 1000
    noise: float = 0.15
    match_weeks: int = 6
    tau: float = 0.05
    checkpoints: str = ''
    fold_problem: str = 'problems/us-flu-short-term-prescribed.json'

    @classmethod
    def from_string(cls, value):
        names = {f.name: f.type for f in fields(cls)}
        out = {}
        for token in filter(None, value.split(',')):
            key, raw = token.split('=', 1)
            if key not in names:
                raise ValueError(f'Unknown recipe field {key!r}')
            out[key] = type(getattr(cls(), key))(raw)
        recipe = cls(**out)
        if recipe.model not in ('climatology', 'analogue', 'recursive', 'trajectory') or recipe.library not in ('own', 'all'):
            raise ValueError(f'Invalid recipe {value!r}')
        if recipe.inputs not in ('finalized', 'reported'):
            raise ValueError('inputs must be finalized or reported')
        if recipe.model in ('recursive', 'trajectory') and not recipe.checkpoints:
            raise ValueError(f'model={recipe.model} needs checkpoints=<folder with one subfolder per held-out season>')
        return recipe

    @property
    def string(self):
        default = Recipe()
        return ','.join(f'{k}={v}' for k, v in asdict(self).items() if k == 'model' or v != getattr(default, k))


def window_weeks(year, window):
    """Saturdays of season `year`-`year + 1` from epiweek window[0] to window[1], plus HISTORY_WEEKS before."""
    day = season_start(year) + timedelta(days=6)
    while epiweek(day.isoformat()) != window[0]:
        day += timedelta(weeks=1)
    weeks = [day - timedelta(weeks=k) for k in range(HISTORY_WEEKS, 0, -1)]
    while True:
        weeks.append(day)
        if epiweek(day.isoformat()) == window[1] and day.year == year + 1:
            return [d.isoformat() for d in weeks]
        day += timedelta(weeks=1)


class SeasonPanel:
    """Weekly values of the problem's target per location (US = panel US, else the sum of states)."""
    def __init__(self, problem, inputs='finalized'):
        panel = read_panel(problem.panel)
        self.panel = panel if inputs == 'reported' else None
        self.target_index = list(map(str, panel['target_names'])).index(problem.targets[0])
        self.issuances = {str(d): i for i, d in enumerate(panel.get('issuance_dates', []))}
        if inputs == 'reported' and 'asof_targets' not in panel:
            raise ValueError('Reported peak evaluation requires archived report vintages')
        names = list(map(str, panel['target_names']))
        self.dates = [str(d) for d in panel['dates']]
        self.index = {d: i for i, d in enumerate(self.dates)}
        self.locations = [str(l) for l in panel['locations']]
        self.values = panel['targets'][..., names.index(problem.targets[0])].astype(float)  # [T, L]
        if 'US' not in self.locations:
            self.locations.append('US')
            self.values = np.concatenate((self.values, np.nansum(self.values, 1, keepdims=True)), 1)

    def curve(self, weeks, locations):
        out = np.full((len(weeks), len(locations)), np.nan)
        cols = [self.locations.index(l) if l in self.locations else None for l in locations]
        for i, d in enumerate(weeks):
            if d in self.index:
                for j, c in enumerate(cols):
                    if c is not None:
                        out[i, j] = self.values[self.index[d], c]
        return out

    def reported_curve(self, weeks, locations, reference):
        """The Wednesday information set for a Saturday reference; never fill with final truth."""
        issuance = (date.fromisoformat(reference) - timedelta(days=3)).isoformat()
        if issuance not in self.issuances:
            return np.full((len(weeks), len(locations)), np.nan)
        source = self.panel['asof_targets'][self.issuances[issuance], ..., self.target_index]
        source_locations = list(map(str, self.panel['locations']))
        values = np.full((len(weeks), len(locations)), np.nan)
        for w, day in enumerate(weeks):
            if day not in self.index:
                continue
            row = source[self.index[day]]
            for l, loc in enumerate(locations):
                if loc in source_locations:
                    values[w, l] = row[source_locations.index(loc)]
                elif loc == 'US' and np.isfinite(row).all():
                    values[w, l] = row.sum()
        return values


def without_truth_fallback(episode):
    """Remove the generic reported loader's final-value fills before peak inference."""
    episode['available'] &= ~episode['filled']
    episode['known_final'] &= ~episode['filled']
    episode['values'] = np.where(episode['available'], episode['values'], 0)
    if 'covariates_filled' in episode:
        cov = episode['covariates'].copy()
        cov[..., 1, :] *= ~episode['covariates_filled']
        cov[..., 0, :] *= cov[..., 1, :]
        episode['covariates'] = cov
    return episode


def library(problem, recipe, held_out, locations):
    """[(season label, curve [W, L])] for training seasons, aligned on season-relative weeks."""
    sources = [(problem, [s for s in problem.training_folds if s != held_out])]
    if recipe.library == 'all':
        for path in LIBRARIES:
            other = Problem.load(path)
            if other.panel != problem.panel:
                sources.append((other, list(other.training_folds)))
    length = len(window_weeks(int(held_out[:4]), problem.season_window))
    out = []
    for source, seasons in sources:
        data = SeasonPanel(source)
        for label in seasons:
            # Aligned on position from the window's first epiweek; 52- and 53-week seasons differ by one end week.
            curve = data.curve(window_weeks(int(label[:4]), problem.season_window), locations)[:length]
            curve = np.concatenate((curve, np.full((length - len(curve), len(locations)), np.nan)))
            if np.isfinite(curve[HISTORY_WEEKS:]).mean() > .8:
                out.append((f'{source.id}:{label}', curve))
    return out


def library_trajectories(recipe, curves, observed, now, rng):
    """[N, W, L]: library continuations after observed weeks [0, now] (inclusive, positions in the curve)."""
    lib = np.stack([c for _, c in curves])  # [S, W, L]
    n, (S, W, L) = recipe.samples, lib.shape
    if recipe.model == 'climatology':
        scale = np.ones((S, L))
        weights = np.full((S, L), 1 / S)
    else:
        start = max(0, now - recipe.match_weeks + 1)
        obs = np.log1p(observed[start:now + 1])[None]  # [1, k, L]
        ref = np.log1p(np.nan_to_num(lib[:, start:now + 1]))
        ok = np.isfinite(obs) & np.isfinite(lib[:, start:now + 1])
        k = np.maximum(ok.sum(1), 1)
        shift = np.where(ok, np.nan_to_num(obs) - ref, 0).sum(1) / k  # mean log-ratio per season/location
        scale = np.exp(np.clip(shift, -3, 3))
        fitted = np.log1p(np.nan_to_num(lib[:, start:now + 1]) * scale[:, None])
        distance = np.where(ok, (np.nan_to_num(obs) - fitted) ** 2, 0).sum(1) / k + 0.05 * shift ** 2
        weights = np.exp(-(distance - distance.min(0)) / recipe.tau)
        weights /= weights.sum(0)
    out = np.empty((n, W, L))
    for l in range(L):
        pick = rng.choice(S, size=n, p=weights[:, l])
        out[:, :, l] = np.nan_to_num(lib[pick, :, l]) * scale[pick, l][:, None]
    out *= np.exp(rng.normal(0, recipe.noise, (n, 1, 1)))
    return out


class FoldModels:
    """The fitted seeds of one held-out season: run recursively (four-week quantile models; one quantile level per
    4-week block, shared by targets and locations) or sampled directly (season-long sampled models)."""
    def __init__(self, folder, fallback, panel=None):
        import torch
        from chromantis.experiment.fit import ForecastSlice
        from chromantis.model.network import load_model
        from chromantis.model.scenario import Scenario
        self.models = []
        for path in sorted(Path(folder).glob('*/model.pt')):
            saved = torch.load(path, map_location='cpu', weights_only=False)
            scenario = Scenario.from_string(saved['metadata']['scenario'])
            # Fold models record their experiment's problem copy (on the cluster); the repository copy is identical.
            reference = saved['metadata']['problem']
            fold_problem = Problem.load(reference if Path(reference).exists() else fallback)
            model = load_model(saved)
            if scenario.reconstruction_labels:
                model = ForecastSlice(model, fold_problem.future_indices(scenario))
            model.eval()
            self.models.append((model, scenario, fold_problem))
        if not self.models:
            raise ValueError(f'No */model.pt under {folder}')
        self.episodes = {}
        self.panel = panel

    def trajectories(self, recipe, weeks, now, locations, rng):
        import torch
        from chromantis.dataset.episodes import episodes, calendar
        model, scenario, fold_problem = self.models[0]
        key = id(fold_problem)
        if key not in self.episodes:
            panel = self.panel if self.panel is not None else load(fold_problem.panel)
            mode = 'reported' if recipe.inputs == 'reported' else 'scheduled_final'
            self.episodes[key] = {e['context_dates'][-1]: e for e in episodes(
                panel, fold_problem, fold_problem.input_names(scenario.input_set), scenario.lookback, mode,
                fold_problem.covariate_names(scenario.covariate_set),
                horizons=fold_problem.horizons, require_labels=False)}
            if recipe.inputs == 'reported':
                self.episodes[key] = {day: without_truth_fallback(e) for day, e in self.episodes[key].items()}
        start = self.episodes[key][weeks[now]]
        k = fold_problem.target_units.index('count')  # the admission target (one count target per seasonal problem)
        per = -(-recipe.samples // len(self.models))
        model_locations = list(start['locations'])
        # A panel without a US series (ILI-converted): the US draw is the sum of the location draws.
        pick = lambda x: np.stack([x[..., model_locations.index(l)] if l in model_locations else x.sum(-1)
                                   for l in locations], -1)
        cols = None
        out = []
        if recipe.model == 'trajectory':
            for model, scenario, _ in self.models:
                with torch.no_grad():
                    draws = torch.cat([model(values=torch.as_tensor(start['values'][None]),
                                             available=torch.as_tensor(start['available'][None]),
                                             calendar=torch.as_tensor(calendar([weeks[now]])),
                                             covariates=torch.as_tensor(start['covariates'][None]) if 'covariates' in start else None,
                                             members=min(128, per - j), locations=list(start['locations']))
                                       for j in range(0, per, 128)]).numpy()[:, 0]  # [M, H, C, L]
                future = pick(np.maximum(draws[:, :len(weeks) - now - 1, k], 0))
                if future.shape[1] < len(weeks) - now - 1:
                    raise ValueError('The fold models do not forecast to the end of the season window')
                out.append(np.concatenate((np.zeros((per, now + 1, len(locations))), future), 1))
            return np.concatenate(out)[:recipe.samples]
        for model, scenario, _ in self.models:
            values = np.repeat(start['values'][None], per, 0)
            available = np.repeat(start['available'][None], per, 0)
            day, path = date.fromisoformat(weeks[now]), []
            while len(path) * 4 < len(weeks) - now - 1:
                with torch.no_grad():
                    q = model(values=torch.as_tensor(values), available=torch.as_tensor(available),
                              calendar=torch.as_tensor(calendar([day.isoformat()] * per)), covariates=None,
                              locations=list(start['locations'])).numpy()  # [Q, N, H, C, L]
                u = np.clip(rng.random(per), LEVELS[0], LEVELS[-1])
                i = np.clip(np.searchsorted(LEVELS, u) - 1, 0, len(LEVELS) - 2)
                w = ((u - LEVELS[i]) / (LEVELS[i + 1] - LEVELS[i]))[:, None, None, None]
                block = np.maximum(q[i, np.arange(per)] * (1 - w) + q[i + 1, np.arange(per)] * w, 0)
                for c, unit in enumerate(fold_problem.target_units):
                    if unit == 'proportion':
                        block[:, :, c] = np.minimum(block[:, :, c], 1)
                path.append(block[:, :, k])
                values = np.concatenate((values, block.astype(values.dtype)), 1)[:, -values.shape[1]:]
                available = np.concatenate((available, np.ones_like(block, dtype=bool)), 1)[:, -available.shape[1]:]
                day += timedelta(weeks=4)
            future = pick(np.concatenate(path, 1)[:, :len(weeks) - now - 1])
            out.append(np.concatenate((np.zeros((per, now + 1, len(locations))), future), 1))
        return np.concatenate(out)[:recipe.samples]


def peaks(paths, first):
    """Peak-week probabilities [W'] and peak-incidence quantiles from trajectories [N, W] (window from `first`)."""
    window = paths[:, first:]
    week = window.argmax(1)
    pmf = np.bincount(week, minlength=window.shape[1]) / len(window)
    return pmf, np.quantile(window.max(1), LEVELS)


def run(problem_path, recipe_string, out=None):
    problem = Problem.load(problem_path)
    if problem.evaluation_kind != 'season_peak':
        raise ValueError(f'{problem.id} is not a season_peak problem')
    recipe = Recipe.from_string(recipe_string)
    if recipe.model in ('recursive', 'trajectory'):
        import torch
        torch.manual_seed(20261011)
    folder = Path(out or OUT / problem.id / recipe.string.replace('/', '|'))
    folder.mkdir(parents=True, exist_ok=True)
    data = SeasonPanel(problem, recipe.inputs)
    locations = [l for l in data.locations]
    rng = np.random.default_rng(20261011)
    scored = []
    for held_out in problem.folds:
        if recipe.model in ('recursive', 'trajectory') and not any((Path(recipe.checkpoints) / held_out).glob('*/model.pt')):
            print(f'{held_out}: no fitted models yet, skipped', flush=True)  # partial results while folds are still training
            continue
        scored.append(held_out)
        weeks = window_weeks(int(held_out[:4]), problem.season_window)
        truth = data.curve(weeks, locations)  # [W, L]
        curves = library(problem, recipe, held_out, locations)
        recursive = FoldModels(Path(recipe.checkpoints) / held_out, recipe.fold_problem, data.panel) \
            if recipe.model in ('recursive', 'trajectory') else None
        origins = weeks[HISTORY_WEEKS:]
        pmf = np.zeros((len(origins), len(locations), len(weeks) - HISTORY_WEEKS))
        quantiles = np.zeros((len(origins), len(locations), len(LEVELS)))
        for o, reference in enumerate(origins):
            now = HISTORY_WEEKS + o - 1  # last observed week: the week ending r - 7 days
            observed = data.reported_curve(weeks, locations, reference) if recipe.inputs == 'reported' else truth
            # An unknown past maximum cannot be replaced with final truth or treated as zero.
            covered = np.isfinite(observed[HISTORY_WEEKS:now + 1]).all(0)
            if recipe.inputs == 'reported':
                issuance = (date.fromisoformat(reference) - timedelta(days=3)).isoformat()
                if issuance not in data.issuances:
                    pmf[o], quantiles[o] = np.nan, np.nan
                    continue
            if recursive is not None:
                paths = recursive.trajectories(recipe, weeks, now, locations, rng)
            else:
                paths = library_trajectories(recipe, curves, observed, now, rng)
            paths[:, :now + 1] = np.nan_to_num(observed[:now + 1])[None]
            for l in range(len(locations)):
                pmf[o, l], quantiles[o, l] = peaks(paths[:, :, l], HISTORY_WEEKS)
            if recipe.inputs == 'reported':
                pmf[o, ~covered], quantiles[o, ~covered] = np.nan, np.nan
        np.savez_compressed(folder / f'peaks_{held_out}.npz', pmf=pmf, quantiles=quantiles, truth=truth,
                            weeks=np.array(weeks), origins=np.array(origins), locations=np.array(locations),
                            quantile_levels=LEVELS)
        print(f'{problem.id} {recipe.string}: {held_out} done ({len(curves)} library seasons)', flush=True)
    (folder / 'manifest.json').write_text(json.dumps(dict(
        problem=problem.reference, problem_id=problem.id, problem_sha256=problem.hash, recipe=recipe.string,
        folds=scored, samples=recipe.samples, evaluation_inputs=recipe.inputs,
        observed_peak_policy='require complete reported window history' if recipe.inputs == 'reported' else 'finalized history',
        definition=__doc__.split('\n\n')[0]), indent=2) + '\n')
    return folder


def score(folder):
    """Per origin and location: peak-week log score and peak-incidence WIS (log and natural); writes scores.csv."""
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text())
    rows = []
    for held_out in manifest['folds']:
        f = np.load(folder / f'peaks_{held_out}.npz')
        truth = f['truth'][HISTORY_WEEKS:]  # [W', L]
        for l, loc in enumerate(map(str, f['locations'])):
            t = truth[:, l]
            if not np.isfinite(t).any():
                continue
            peak = np.nanmax(t)
            tie = (t == peak).sum() > 1
            week = int(np.nanargmax(t))
            q = f['quantiles'][:, l]
            wis = {s: quantile_scores(fn(q), fn(np.full(len(q), peak))).wis.to_numpy()
                   for s, fn in (('log', np.log1p), ('natural', lambda x: x))}
            for o, origin in enumerate(map(str, f['origins'])):
                if not (np.isfinite(f['pmf'][o, l]).all() and np.isfinite(q[o]).all()):
                    continue
                rows.append(dict(season=held_out, origin=origin, month=origin[:7], location=loc,
                                 geography='US' if loc == 'US' else 'states_dc',
                                 peak_week_log_score=np.nan if tie else -np.log(max(f['pmf'][o, l, week], FLOOR)),
                                 peak_week_probability=np.nan if tie else f['pmf'][o, l, week],
                                 peak_wis_log=wis['log'][o], peak_wis_natural=wis['natural'][o],
                                 weeks_to_true_peak=week - o))
    table = pd.DataFrame(rows)
    table.to_csv(folder / 'scores.csv', index=False)
    return table


def import_hub(model, problem_path='problems/us-flu-season-peak.json', hub='production/hubs/FluSight-forecast-hub', out=None):
    """A Hub model's submitted `peak week inc flu hosp` (pmf) and `peak inc flu hosp` (quantiles) as a run folder.

    Only reference dates and locations it submitted are filled; others stay NaN and are skipped by `score`.
    Its forecasts were made in real time from reported data; truth here is the panel's finalized values."""
    problem = Problem.load(problem_path)
    data = SeasonPanel(problem)
    locations = data.locations
    fips = pd.read_csv('data/metadata/locations.csv', dtype={'location': str}).set_index('location').abbreviation.to_dict()
    folder = Path(out or OUT / problem.id / f'hub={model}')
    folder.mkdir(parents=True, exist_ok=True)
    seasons = []
    files = sorted(Path(hub, 'model-output', model).glob('*.csv'))
    frames = [pd.read_csv(f, dtype={'location': str, 'output_type_id': str}) for f in files]
    frames = [f[f.target.isin(['peak week inc flu hosp', 'peak inc flu hosp'])] for f in frames]
    table = pd.concat([f for f in frames if len(f)], ignore_index=True) if any(len(f) for f in frames) else pd.DataFrame()
    for held_out in problem.folds:
        weeks = window_weeks(int(held_out[:4]), problem.season_window)
        origins = weeks[HISTORY_WEEKS:]
        part = table[table.reference_date.astype(str).isin(origins)] if len(table) else table
        if not len(part):
            continue
        pmf = np.full((len(origins), len(locations), len(origins)), np.nan)
        quantiles = np.full((len(origins), len(locations), len(LEVELS)), np.nan)
        for (reference, location, target), g in part.groupby(['reference_date', 'location', 'target']):
            loc = 'US' if location == 'US' else fips.get(location)
            if loc not in locations:
                continue
            o, l = origins.index(str(reference)), locations.index(loc)
            if target == 'peak week inc flu hosp':
                p = dict(zip(g.output_type_id.astype(str), g.value.astype(float)))
                pmf[o, l] = [p.get(w, 0.) for w in origins]
                pmf[o, l] /= max(pmf[o, l].sum(), 1e-12)
            else:
                q = dict(zip(g.output_type_id.astype(float).round(3), g.value.astype(float)))
                if all(round(x, 3) in q for x in LEVELS):
                    quantiles[o, l] = [q[round(x, 3)] for x in LEVELS]
        np.savez_compressed(folder / f'peaks_{held_out}.npz', pmf=pmf, quantiles=quantiles, truth=data.curve(weeks, locations),
                            weeks=np.array(weeks), origins=np.array(origins), locations=np.array(locations), quantile_levels=LEVELS)
        seasons.append(held_out)
    (folder / 'manifest.json').write_text(json.dumps(dict(problem=problem.reference, problem_id=problem.id, problem_sha256=problem.hash,
        recipe=f'hub={model}', folds=seasons, definition=import_hub.__doc__.split('\n\n')[0]), indent=2) + '\n')
    return folder


def summary(folders, common=False):
    """Mean scores per run: all origins, and origins before / after the true peak, states/DC and US.

    `common=True` keeps only (season, reference date, location, score) cells every run scored, so runs
    with partial coverage (Hub submissions) are compared on identical tasks."""
    rows = []
    tables = {}
    for folder in map(Path, folders):
        t = score(folder) if not (folder / 'scores.csv').exists() else pd.read_csv(folder / 'scores.csv')
        tables[json.loads((folder / 'manifest.json').read_text())['recipe']] = t
    if common:
        key = ['season', 'origin', 'location']
        shared = None
        for t in tables.values():
            cells = set(map(tuple, t.dropna(subset=['peak_week_log_score', 'peak_wis_log'])[key].values))
            shared = cells if shared is None else shared & cells
        tables = {r: t[[tuple(x) in shared for x in t[key].values]] for r, t in tables.items()}
    for recipe, t in tables.items():
        for geography, g in t.groupby('geography'):
            for when, part in (('all origins', g), ('8+ weeks before peak', g[g.weeks_to_true_peak >= 8]),
                               ('0-7 weeks before peak', g[g.weeks_to_true_peak.between(0, 7)])):
                rows.append(dict(recipe=recipe, geography=geography, origins=when,
                                 peak_week_log_score=part.peak_week_log_score.mean(),
                                 peak_week_probability=part.peak_week_probability.mean(),
                                 peak_wis_log=part.peak_wis_log.mean(), cells=len(part)))
    return pd.DataFrame(rows)


def convert_ili(history='data/processed/historical_ili.npz', panel='data/processed/panel.npz',
                out='data/processed/ili-converted-panel.npz', first=2010, last=2021):
    """ILINet state ILI (2010-11..2021-22) converted to weekly flu admissions, one factor per state.

    Excess ILI = ILI minus the season's summer baseline (median of epiweeks 31-39). The state's factor
    k = sum(NHSN admissions) / sum(excess ILI) over the window weeks of 2022-23..2025-26, where the
    panel holds both ILINet (covariate `ilinet_ili`, percent) and NHSN admissions. Converted
    admissions = k * excess ILI, floored at zero. The fit diagnostics are stored in the panel metadata."""
    p = load(panel)
    dates = [str(d) for d in p['dates']]
    locations = [str(l) for l in p['locations'] if str(l) != 'US']
    adm = p['targets'][..., list(map(str, p['target_names'])).index('nhsn_flu_admissions')]
    ili_now = p['covariates'][..., list(map(str, p['covariate_names'])).index('ilinet_ili')] / 100
    h = np.load(history, allow_pickle=True)
    hist_dates = [str(d) for d in h['dates']]
    hist = {str(l).upper(): h['values'][:, i] for i, l in enumerate(h['locations'])}

    def excess(series_dates, series, year):
        index = {d: i for i, d in enumerate(series_dates)}
        weeks = window_weeks(year, (40, 21))
        base = [series[index[d]] for d in weeks[:HISTORY_WEEKS] if d in index and epiweek(d) >= 31]
        b = np.nanmedian(base) if base else np.nan
        return weeks, np.array([series[index[d]] - b if d in index else np.nan for d in weeks])

    factors, fits = {}, {}
    for loc in locations:
        j = list(map(str, p['locations'])).index(loc)
        num = den = 0.
        pairs = []
        for year in (2022, 2023, 2024, 2025):
            weeks, x = excess(dates, ili_now[:, j], year)
            y = np.array([adm[dates.index(d), j] if d in dates else np.nan for d in weeks])
            ok = np.isfinite(x) & np.isfinite(y)
            ok[:HISTORY_WEEKS] = False
            num += y[ok].sum()
            den += np.maximum(x[ok], 0).sum()
            pairs.append((weeks[HISTORY_WEEKS:], np.maximum(x, 0)[HISTORY_WEEKS:], y[HISTORY_WEEKS:]))
        k = num / den if den > 0 else np.nan
        factors[loc] = float(k)
        same = [int(np.nanargmax(a) == np.nanargmax(b)) for _, a, b in pairs if np.isfinite(a).any() and np.isfinite(b).any()]
        close = [int(abs(int(np.nanargmax(a)) - int(np.nanargmax(b))) <= 2) for _, a, b in pairs if np.isfinite(a).any() and np.isfinite(b).any()]
        corr = [np.corrcoef(np.log1p(k * a[np.isfinite(a) & np.isfinite(b)]), np.log1p(b[np.isfinite(a) & np.isfinite(b)]))[0, 1]
                for _, a, b in pairs if (np.isfinite(a) & np.isfinite(b)).sum() > 5]
        fits[loc] = dict(factor=float(k), peak_week_same=float(np.mean(same)), peak_week_within_2=float(np.mean(close)),
                         log_correlation=float(np.nanmean(corr)))
    # Every week of the archive (a continuous weekly calendar, as episodes require), each converted with its
    # own CDC season's summer baseline; empty covariate arrays because the panel has no covariates.
    def baseline(series, year):
        index = {d: i for i, d in enumerate(hist_dates)}
        base = [series[index[d]] for d in window_weeks(year, (40, 21))[:HISTORY_WEEKS] if d in index and epiweek(d) >= 31]
        return np.nanmedian(base) if base else np.nan
    weeks_all = [d for d in hist_dates if first <= int(season(d)[:4]) <= last]
    values = np.full((len(weeks_all), len(locations), 1), np.nan, np.float32)
    for j, loc in enumerate(locations):
        if loc not in hist or not np.isfinite(factors[loc]):
            continue
        series = hist[loc]
        bases = {y: baseline(series, y) for y in range(first, last + 1)}
        for i, d in enumerate(weeks_all):
            v = series[hist_dates.index(d)] - bases[int(season(d)[:4])]
            values[i, j, 0] = factors[loc] * max(v, 0) if np.isfinite(v) else np.nan
    meta = dict(definition=convert_ili.__doc__, fits=fits, source_history=history, source_panel=panel,
                seasons=f'{first}-{first + 1}..{last}-{last + 1}')
    np.savez_compressed(out, dates=np.array(weeks_all, dtype='datetime64[D]'), locations=np.array(locations),
                        target_names=np.array(['flu_admissions_from_ili']), targets=values,
                        covariates=np.zeros((len(weeks_all), len(locations), 0), np.float32), covariate_names=np.array([], dtype=str),
                        covariates_national=np.zeros((len(weeks_all), 0), np.float32), covariate_national_names=np.array([], dtype=str),
                        metadata=np.array(json.dumps(meta)))
    return fits


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('convert-ili')
    r = sub.add_parser('run')
    r.add_argument('--problem', required=True)
    r.add_argument('--recipe', required=True)
    r.add_argument('--out')
    s = sub.add_parser('score')
    s.add_argument('folders', nargs='+')
    args = parser.parse_args(argv)
    if args.command == 'convert-ili':
        fits = pd.DataFrame(convert_ili()).T
        print(fits.describe().round(3).to_string())
    elif args.command == 'run':
        run(args.problem, args.recipe, args.out)
    else:
        print(summary(args.folders).round(4).to_string(index=False))


if __name__ == '__main__':
    main()
