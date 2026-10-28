"""BDBV projection for one hub round: nowcast of the incomplete weeks, then a Chromantis ensemble.

1. Nowcast (`ebola_nowcast.py`). Weeks ending 26 Sep-24 Oct are still growing between hub
   releases. Each health zone's final count is drawn release step by release step from a
   negative-binomial model fitted to the 17 -> 24 Oct release pair, so zones reporting zero can
   gain cases; provinces and the country are sums of their health zones. The draws are seeded,
   so every fit job sees the same 100 nowcast draws.
2. Models (`fit`). Each recipe x seed is retrained on West Africa 2014-15, Kivu 2018-20 and BDBV
   weeks through 19 Sep (latest values), with no held-out window, and samples weeks ending
   31 Oct-21 Nov (1-4 weeks after the last data week) from every nowcast draw.
3. Trajectories (`merge`). Trajectory i = nowcast draw i + the forecast that model (i mod n_models)
   sampled from draw i, so all models contribute equally and every trajectory has its own
   nowcast. Future weeks are reconciled top-down within each trajectory: the national value is
   kept, provinces are scaled to sum to it and health zones to their province (rounded so the
   sums stay exact). Writes the hub CSV (100 samples per location) and a summary.

History: until 27 Oct this script fitted one recipe (r027_child12, 4 seeds x 25 draws) in one
process; the five-window rescoring then favoured a three-recipe ensemble. The first ensemble
(27 Oct) used a fixed completion multiplier per lag, which kept zones reporting zero at zero,
and left future weeks unreconciled (national about 96 cases above the sum of health zones).

    .venv/bin/python scripts/ebola_project.py fit --recipe top035_r020_child09 --seeds 42 43 44 45 --out DIR --device cuda
    .venv/bin/python scripts/ebola_project.py merge --out DIR --model-id UNC-Chromantis
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from chromantis.dataset.cv import masked
from chromantis.dataset.episodes import calendar, episodes
from chromantis.experiment import training
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
from ebola_nowcast import Nowcast

# Selected by the five-window rescoring (experiments/ebola-20261026/rescore-multi-rank.csv):
# the best recipe (pools locations, no outbreak-total input), the best with the outbreak-total
# summaries, and the best without pooling across locations (outbreak-total growth input).
RECIPES = {
    'top035_r020_child09': 'growth_anchor=1,lookback=6,count_transform=sqrt,geography=0,spatial=pooled,decoder=residual2,'
                           'noise=local,latent=32,width=256,epochs=160,members=32,lr=0.0003,annual_calendar=0,'
                           'weight_decay=0.0001,covariate_encoder=summary,log_loss_weight=0.25,covariate_dropout=0.25,'
                           'forecast_view=raw',
    'top004_r026_child20': 'growth_anchor=1,lookback=6,count_transform=sqrt,geography=0,spatial=pooled,decoder=residual2,'
                           'decoder_blocks=2,noise=local,latent=4,width=128,epochs=160,batch_size=32,members=16,'
                           'annual_calendar=0,weight_decay=0.0001,covariate_encoder=summary,covariate_set=outbreak,'
                           'log_loss_weight=1.0,covariate_dropout=0.25,forecast_view=raw',
    'top045_r017_child03': 'growth_anchor=1,lookback=6,count_transform=sqrt,geography=0,dynamics=0,decoder=residual2,'
                           'noise=local,latent=4,epochs=160,batch_size=32,members=16,annual_calendar=0,weight_decay=0.0001,'
                           'covariate_encoder=growth,covariate_set=outbreak,log_loss_weight=1.0,forecast_view=raw',
}
REFERENCE_DATE = '2026-10-31'
LAST = '2026-10-24'          # latest release and last data week
TRAIN_UNTIL = '2026-09-19'   # BDBV weeks after this one are still growing
DRAWS = 100


class Setup:
    """Panel, BDBV metadata, latest release and the nowcast draws shared by fit and merge."""

    def __init__(self, hub):
        self.problem = Problem.load('problems/ebola-bdbv-screen.json')
        with np.load(self.problem.panel) as d:
            self.panel = {k: d[k] for k in d.files}
        self.dates = self.panel['dates'].astype(str)
        self.locations = self.panel['locations'].astype(str)
        self.meta = pd.read_csv(self.problem.locations).set_index('location').loc[self.locations]
        self.bdbv = (self.meta.outbreak == 'bdbv-2026').to_numpy()
        t = pd.read_csv(Path(hub) / 'target-data/time-series.csv')
        self.reported = t[t.as_of == LAST].pivot(index='target_end_date', columns='location', values='observation')
        self.recent = [str(w) for w in self.dates if '2026-09-26' <= w <= LAST]
        self.hz = [c for c in self.locations if self.meta.outbreak[c] == 'bdbv-2026' and self.meta.level[c] == 'local']
        self.provinces = [c for c in self.locations if self.meta.outbreak[c] == 'bdbv-2026' and self.meta.level[c] == 'middle']
        # Children by code (CD-TO-15 belongs to CD-TO), never by name.
        self.kids = {p: [h for h in self.hz if h.rsplit('-', 1)[0] == p] for p in self.provinces}
        if not all(self.kids.values()):
            raise ValueError(f'Provinces without health zones: {[p for p, k in self.kids.items() if not k]}')
        self.draws = Nowcast(self.hz, hub).sample(LAST, self.recent, DRAWS)

    def full_panel(self, hz_values):
        """Panel copy with the BDBV incomplete weeks replaced by one draw; parents are sums."""
        p, meta, locations = dict(self.panel), self.meta, list(self.locations)
        y = self.panel['targets'][..., 0].copy()
        rows = [list(self.dates).index(w) for w in self.recent]
        frame = pd.DataFrame(hz_values, columns=self.hz)
        for c in self.hz:
            y[rows, locations.index(c)] = frame[c]
        for c in self.provinces:
            y[rows, locations.index(c)] = frame[self.kids[c]].sum(1)
        y[rows, locations.index('CD')] = frame.sum(1)
        p['targets'] = y[..., None]
        parent = [meta.parent[c] if isinstance(meta.parent[c], str) and meta.parent[c] else c for c in locations]
        idx = {c: i for i, c in enumerate(locations)}
        top = {o: meta.index[(meta.outbreak == o) & (meta.level == 'top')][0] for o in meta.outbreak.unique()}
        p['covariates'] = np.stack([y[:, [idx[c] for c in parent]], y[:, [idx[top[meta.outbreak[c]]] for c in locations]]],
                                   -1).astype(np.float32)
        return p


def fit(args):
    s = Setup(args.hub)
    problem, scenario = s.problem, Scenario.from_string(RECIPES[args.recipe])
    names = problem.input_names(scenario.input_set), problem.covariate_names(scenario.covariate_set)
    keep = s.dates <= TRAIN_UNTIL
    train = [e for e in episodes(masked(s.panel, keep), problem, names[0], scenario.lookback, 'scheduled_final', names[1],
                                 horizons=problem.model_horizons(scenario)) if e['context_dates'][-1] in set(s.dates[keep])]
    pop = problem.populations(train[0]['locations'])
    origins = [next(e for e in episodes(s.full_panel(d), problem, names[0], scenario.lookback, 'scheduled_final', names[1],
                                        horizons=problem.horizons, require_labels=False) if e['context_dates'][-1] == LAST)
               for d in s.draws]
    device = torch.device(args.device)
    for seed in args.seeds:
        torch.manual_seed(seed)
        model, _ = training.fit_models(train, None, train, problem, scenario, seed, device, pop)
        # Sample on the CPU: fitted input scales stay CPU tensors, and 100 forward passes are cheap.
        model = model.cpu().eval()
        samples = []
        for e in origins:
            tensor = lambda x: torch.as_tensor(x[None])
            with torch.no_grad():
                out = model(values=tensor(e['values']), available=tensor(e['available']),
                            calendar=torch.as_tensor(calendar([e['context_dates'][-1]])),
                            covariates=tensor(e['covariates']) if 'covariates' in e else None, members=1,
                            locations=list(e['locations'])).numpy()[0, 0]
            samples.append(out[:, 0, :])
        np.savez_compressed(Path(args.out) / f'samples-{args.recipe}-s{seed}.npz', samples=np.array(samples),
                            target_dates=np.array(origins[0]['target_dates']), locations=s.locations,
                            recipe=RECIPES[args.recipe], seed=seed)
        print(f'{args.recipe} seed {seed} done', flush=True)


def split(total, weights, fallback):
    """Integers summing exactly to `total`, proportional to `weights` (else `fallback`, else equal)."""
    w = weights if weights.sum() > 0 else fallback if fallback.sum() > 0 else np.ones_like(weights)
    raw = total * w / w.sum()
    out = np.floor(raw)
    out[np.argsort(raw - out)[::-1][:int(round(total - out.sum()))]] += 1   # largest remainders
    return out


def reconcile(future, recent, s, idx):
    """Top-down within one trajectory: keep the national count, provinces sum to it, zones to their province.

    future: [horizons, locations] model samples; recent: [locations] sum of the trajectory's last three
    nowcast weeks, used as shares where the model puts zero on every child."""
    out = np.round(future)
    for h in range(len(out)):
        total = out[h, idx['CD']]
        p = [idx[c] for c in s.provinces]
        out[h, p] = split(total, future[h, p], recent[p])
        for c in s.provinces:
            z = [idx[k] for k in s.kids[c]]
            out[h, z] = split(out[h, idx[c]], future[h, z], recent[z])
    return out


def merge(args):
    s = Setup(args.hub)
    out = Path(args.out)
    files = sorted(out.glob('samples-*.npz'))
    models = [np.load(f) for f in files]
    target_dates = list(models[0]['target_dates'].astype(str))
    rows = [list(s.dates).index(w) for w in s.recent]
    idx = {c: i for i, c in enumerate(s.locations)}
    paths = []
    for i, draw in enumerate(s.draws):
        now = s.full_panel(draw)['targets'][rows, :, 0]
        future = reconcile(np.maximum(models[i % len(models)]['samples'][i], 0), now[-3:].sum(0), s, idx)
        paths.append(np.concatenate([now, future], 0)[:, s.bdbv])
    paths = np.array(paths)                          # [100 trajectories, weeks, BDBV locations]
    weeks, locations = s.recent + target_dates, s.locations[s.bdbv]
    np.savez_compressed(out / 'trajectories.npz', paths=paths, weeks=np.array(weeks), locations=locations,
                        model_for_trajectory=np.array([files[i % len(files)].stem for i in range(DRAWS)]))
    summary, hub = [], []
    for j, w in enumerate(weeks):
        for i, c in enumerate(locations):
            v = paths[:, j, i]
            summary.append(dict(week=w, location=c, kind='nowcast' if w <= LAST else 'forecast',
                                reported=s.reported[c].get(w) if c in s.reported else None,
                                q05=np.quantile(v, .05), q25=np.quantile(v, .25), median=np.median(v),
                                q75=np.quantile(v, .75), q95=np.quantile(v, .95)))
            hub += [(REFERENCE_DATE, 'wk inc confirmed cases', w, c, 'sample', k + 1, float(v[k])) for k in range(DRAWS)]
    pd.DataFrame(summary).to_csv(out / 'summary.csv', index=False)
    team = args.model_id
    sub = out / 'hub' / 'model-output' / team
    sub.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(hub, columns=['reference_date', 'target', 'target_end_date', 'location', 'output_type', 'output_type_id',
                               'value']).to_csv(sub / f'{REFERENCE_DATE}-{team}.csv', index=False)
    (out / 'settings.json').write_text(json.dumps(dict(models=[f.stem for f in files], recipes=RECIPES,
                                                       nowcast='ebola_nowcast.py', train_until=TRAIN_UNTIL, last=LAST,
                                                       reference_date=REFERENCE_DATE, draws=DRAWS), indent=2) + '\n')
    print(sub / f'{REFERENCE_DATE}-{team}.csv', len(hub), 'rows,', len(files), 'models')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['fit', 'merge'])
    parser.add_argument('--recipe', choices=list(RECIPES))
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 43, 44, 45])
    parser.add_argument('--out', required=True)
    parser.add_argument('--hub', default='../hubs/BDBV-Modeling-Hub')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--model-id', default='UNC-Chromantis')
    args = parser.parse_args()
    Path(args.out).mkdir(parents=True, exist_ok=True)
    fit(args) if args.command == 'fit' else merge(args)


if __name__ == '__main__':
    main()
