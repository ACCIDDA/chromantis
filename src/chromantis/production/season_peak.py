"""Operational season-peak forecasts for FluSight (`peak week inc flu hosp`, `peak inc flu hosp`), 2026-10-14.

The fitted season-long sampled models (one folder per seed, `*/model.pt`, trained on all completed seasons)
are run exactly as in the retrospective peak scoring (`chromantis.seasonal`, recipe `model=trajectory,
inputs=reported`): the issuance's Wednesday-report history with no finalized fallback, one joint path per
member over the rest of the season window. Weeks already reported are kept as reported. Each path's maximum
and its week give one peak draw; peak-week probabilities and the 23 peak-incidence quantiles follow.

    python -m chromantis.production.season_peak --checkpoints DIR --dataset PANEL --issuance 2026-10-14 --out DIR
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.dataset.build import load, for_hub
from chromantis.evaluation.quantiles import LEVELS
from chromantis.seasonal import FoldModels, Recipe, window_weeks, peaks, HISTORY_WEEKS

WINDOW = (40, 21)
LOCATIONS_CSV = 'production/hubs/FluSight-forecast-hub/auxiliary-data/locations.csv'


def forecast(checkpoints, dataset, issuance, problem, samples):
    panel = for_hub(load(dataset), 'flusight')
    reference = (date.fromisoformat(issuance) + timedelta(days=3)).isoformat()
    last = (date.fromisoformat(issuance) - timedelta(days=4)).isoformat()
    year = int(reference[:4]) if int(reference[5:7]) >= 8 else int(reference[:4]) - 1
    weeks = window_weeks(year, WINDOW)
    now = weeks.index(last)
    locations = [str(l) for l in panel['locations']]
    w = [str(d) for d in panel['issuance_dates']].index(issuance)
    k = list(map(str, panel['target_names'])).index('nhsn_flu_admissions')
    index = {str(d): i for i, d in enumerate(panel['dates'])}
    observed = np.stack([panel['asof_targets'][w, index[d], :, k] for d in weeks[:now + 1]])  # [now+1, L]
    if not np.isfinite(observed[HISTORY_WEEKS:]).all():
        raise ValueError('A reported in-window week is missing; the peak so far would be unknown')
    recipe = Recipe(model='trajectory', inputs='reported', samples=samples, checkpoints=str(checkpoints), fold_problem=problem)
    models = FoldModels(checkpoints, problem, panel)
    paths = models.trajectories(recipe, weeks, now, locations, np.random.default_rng(20261011))
    paths[:, :now + 1] = np.nan_to_num(observed)[None]
    return weeks, now, locations, paths, len(models.models)


def hub_rows(reference, weeks, locations, paths):
    fips = pd.read_csv(LOCATIONS_CSV, dtype=str).set_index('abbreviation').location
    rows = []
    for l, loc in enumerate(locations):
        pmf, q = peaks(paths[:, :, l], HISTORY_WEEKS)
        code = 'US' if loc == 'US' else fips[loc]
        rows += [(reference, 'peak week inc flu hosp', '', '', code, 'pmf', d, p) for d, p in zip(weeks[HISTORY_WEEKS:], pmf)]
        rows += [(reference, 'peak inc flu hosp', '', '', code, 'quantile', lev, v) for lev, v in zip(LEVELS, np.maximum.accumulate(q))]
    return pd.DataFrame(rows, columns=['reference_date', 'target', 'horizon', 'target_end_date', 'location',
                                       'output_type', 'output_type_id', 'value'])


def plot(path, reference, weeks, now, locations, paths, history):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    names = pd.read_csv(LOCATIONS_CSV, dtype=str).set_index('abbreviation').location_name.to_dict()
    days = pd.to_datetime(weeks)
    order = ['US'] + sorted(l for l in locations if l != 'US')
    with PdfPages(path) as pdf:
        for start in range(0, len(order), 6):
            fig, axes = plt.subplots(3, 2, figsize=(11, 8.5))
            for ax, loc in zip(axes.flat, order[start:start + 6]):
                l = locations.index(loc)
                x = paths[:, :, l]
                bands = np.quantile(x[:, now:], [.05, .25, .5, .75, .95], 0)
                ax.fill_between(days[now:], bands[0], bands[4], color='tab:blue', alpha=.15, lw=0, label='90%')
                ax.fill_between(days[now:], bands[1], bands[3], color='tab:blue', alpha=.3, lw=0, label='50%')
                ax.plot(days[now:], bands[2], color='tab:blue', lw=1.2, label='median path')
                ax.plot(days[:now + 1], x[0, :now + 1], 'k.-', ms=3, lw=1, label='reported')
                if loc in history:
                    ax.plot(history[loc].index, history[loc].values, color='0.6', lw=.8, ls='--', label='2025-26')
                pmf, q = peaks(x, HISTORY_WEEKS)
                twin = ax.twinx()
                twin.bar(days[HISTORY_WEEKS:], pmf, width=5, color='tab:orange', alpha=.6)
                twin.set_ylim(0, max(pmf.max() * 3, .05))
                twin.set_yticks([])
                ax.axhspan(q[LEVELS.tolist().index(.25)], q[LEVELS.tolist().index(.75)], color='tab:red', alpha=.08)
                ax.axhline(q[LEVELS.tolist().index(.5)], color='tab:red', lw=.8, ls=':')
                mode = days[HISTORY_WEEKS:][pmf.argmax()]
                ax.set_title(f'{names.get(loc, loc)}: peak {q[11]:,.0f} (50%: {q[6]:,.0f}-{q[16]:,.0f}), '
                             f'most likely week {mode:%b %d}', fontsize=8, loc='left')
                ax.tick_params(labelsize=7)
                ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
            axes.flat[0].legend(fontsize=6, loc='upper left')
            fig.suptitle(f'Chromantis season-peak forecast, reference date {reference}. Blue: season paths; orange bars: '
                         'peak-week probabilities; red band/line: peak-size 50% interval and median', fontsize=9)
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--checkpoints', required=True, help='Folder with one */model.pt per fitted seed')
    p.add_argument('--dataset', required=True)
    p.add_argument('--issuance', required=True)
    p.add_argument('--problem', default='problems/us-flu-long-horizon-production.json')
    p.add_argument('--samples', type=int, default=4000)
    p.add_argument('--out', required=True)
    args = p.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    reference = (date.fromisoformat(args.issuance) + timedelta(days=3)).isoformat()
    weeks, now, locations, paths, n_models = forecast(args.checkpoints, args.dataset, args.issuance, args.problem, args.samples)
    rows = hub_rows(reference, weeks, locations, paths)
    rows.to_csv(out / f'{reference}-peaks.csv', index=False)
    np.savez_compressed(out / 'paths.npz', paths=paths.astype(np.float32), weeks=np.array(weeks), locations=np.array(locations))
    hub = pd.read_csv('production/hubs/FluSight-forecast-hub/target-data/target-hospital-admissions.csv', dtype={'location': str})
    fips = pd.read_csv(LOCATIONS_CSV, dtype=str).set_index('location').abbreviation.to_dict()
    hub['date'] = pd.to_datetime(hub['date'])
    last = hub[(hub.date >= pd.Timestamp(weeks[0]) - pd.Timedelta(weeks=52)) & (hub.date <= pd.Timestamp(weeks[-1]) - pd.Timedelta(weeks=52))]
    history = {('US' if c == 'US' else fips.get(c)): pd.Series(g.value.values, g.date + pd.Timedelta(weeks=52)) for c, g in last.groupby('location')}
    plot(out / f'{reference}-peaks.pdf', reference, weeks, now, locations, paths, history)
    (out / 'manifest.json').write_text(json.dumps(dict(
        checkpoints=str(Path(args.checkpoints).resolve()), models=n_models, dataset=str(Path(args.dataset).resolve()),
        issuance=args.issuance, reference_date=reference, samples=args.samples, last_reported_week=weeks[now],
        definition=__doc__.split('\n\n')[0]), indent=2) + '\n')
    print(out / f'{reference}-peaks.csv')


if __name__ == '__main__':
    main()
