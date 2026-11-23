"""Where would a candidate mixture have ranked among this season's FluSight models? (flu search, 23 Nov 2026)

Post-selection check only: the candidate was chosen on 2023-24..2025-26 without any 2026-27 data (experiments/
flu-search-20261120/protocol.json); this scores it once, afterwards, at the user's request.

Candidate forecasts: the all-season release fits of each member (production problem, refit on 2022-23..2025-26), run
on each 2026-27 Wednesday report exactly as production would (eval_2026-2027/corrected), combined as an equal-weight
mixture (evaluation.ensembles.combine, rule `mixture`, seeds common to every member). They are added as one more model
to every FluSight model-output file for the same reference dates. Truth: the Hub's latest target data. Every model is
scored on WIS of log(1 + value) for admissions (CDC's log scale) and natural-scale WIS for the ED share, and ranked by
pairwise relative WIS (geometric mean over other models of mean-WIS ratios on common tasks, divided by
FluSight-baseline's), counting models with at least half of the baseline's tasks. Lower is better.

    PYTHONPATH=src .venv/bin/python scripts/flu_live_rank.py --hub production/hubs/FluSight-forecast-hub \
        --candidate "Masked A=flu-s-release4+flu-s-release5:Bq.smp.ll1.nm10,ref.B.nm10,Ar.peak.nokinsa.nm10"
"""
import argparse
import csv
import glob
from pathlib import Path

import numpy as np
import pandas as pd

from chromantis.evaluation.ensembles import combine

TARGETS = {'hosp': ('wk inc flu hosp', 'nhsn_flu_admissions', 'target-hospital-admissions.csv'),
           'ed': ('wk inc flu prop ed visits', 'nssp_flu_proportion', 'target-ed-visits-prop.csv')}


def wis_long(df):
    """Mean WIS per (model, reference_date, horizon, location) from quantile rows with columns level, value, truth."""
    df = df.copy()
    df['pin'] = 2 * ((df.truth <= df.value).astype(float) - df.level) * (df.value - df.truth)
    return df.groupby(['model', 'reference_date', 'horizon', 'location']).pin.mean().rename('wis').reset_index()


def pairwise(scores, baseline='FluSight-baseline'):
    """Relative WIS per model (Cramer et al. pairwise), lower is better; models with >= half the baseline's tasks."""
    w = scores.pivot_table(index=['reference_date', 'horizon', 'location'], columns='model', values='wis')
    n = w.notna().sum()
    keep = n[n >= 0.5 * n.get(baseline, n.max())].index
    w = w[keep]
    models = list(w.columns)
    theta = {}
    for i in models:
        ratios = []
        for j in models:
            if i == j:
                continue
            both = w[i].notna() & w[j].notna()
            if both.sum() > 0:
                ratios.append(w.loc[both, i].mean() / w.loc[both, j].mean())
        theta[i] = np.exp(np.mean(np.log(ratios)))
    rel = pd.Series(theta) / theta[baseline]
    out = pd.DataFrame({'relative_wis': rel, 'tasks': n[keep]}).sort_values('relative_wis')
    out['rank'] = np.arange(1, len(out) + 1)
    return out


def candidate(spec, channel, to_fips):
    label, rest = spec.split('=')
    exps, recipes = rest.split(':')
    forecasts, meta = {}, {}  # recipe -> seed -> (reference dates, q)
    for e in exps.split('+'):
        root = Path('data/experiments') / e
        for r in csv.DictReader(open(root / 'runs.csv')):
            if r['name'] not in recipes.split(',') or r['status'] != 'complete':
                continue
            z = np.load(root / r['attempt'] / 'eval_2026-2027' / 'corrected' / 'forecasts.npz')
            k = list(z['target_names']).index(channel)
            forecasts.setdefault(r['name'], {})[r['seed']] = ([str(d) for d in z['target_dates'][:, 0]], z['quantiles'][..., k, :])
            meta = ([to_fips[str(l)] for l in z['locations']], z['quantile_levels'])
    seeds = sorted(set.intersection(*[set(v) for v in forecasts.values()]))
    # Members can start a week apart at the season edge: keep the reference dates every member forecasts.
    refs = sorted(set.intersection(*[set(d) for v in forecasts.values() for d, _ in v.values()]))
    pick = lambda d, q: q[:, [d.index(x) for x in refs]]
    q = combine([dict(channels=[0], values=np.stack([pick(*forecasts[m][s]) for s in seeds])[..., None, :]) for m in forecasts], 0, 'mixture')
    locs, lv = meta
    rows = [(label, refs[i], h, loc, float(lv[l]), float(q[l, i, h, j]))
            for i in range(len(refs)) for h in range(4) for j, loc in enumerate(locs) for l in range(len(lv))]
    print(f'{label}: {len(forecasts)} recipes x {len(seeds)} seeds')
    return pd.DataFrame(rows, columns=['model', 'reference_date', 'horizon', 'location', 'level', 'value'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hub', required=True)
    ap.add_argument('--candidate', action='append', required=True, help='LABEL=exp1+exp2:recipe,recipe,...')
    ap.add_argument('--target', choices=list(TARGETS), default='hosp')
    ap.add_argument('--out', default='output/flu-search/live-rank')
    a = ap.parse_args()
    hub = Path(a.hub)
    hub_target, channel, truth_file = TARGETS[a.target]
    loc = pd.read_csv(hub / 'auxiliary-data/locations.csv', dtype=str)
    to_fips = dict(zip(loc.abbreviation, loc.location))
    cands = pd.concat([candidate(c, channel, to_fips) for c in a.candidate])
    cands = cands[cands.reference_date >= '2026-10-01']  # the FluSight season (the fits also forecast from August)
    refs = sorted(cands.reference_date.unique())
    files = [f for ref in refs for f in glob.glob(str(hub / 'model-output' / '*' / f'{ref}-*.csv'))]
    hubdf = []
    for f in files:
        d = pd.read_csv(f, dtype={'location': str, 'output_type_id': str})
        d = d[(d.target == hub_target) & (d.output_type == 'quantile') & (d.horizon.between(0, 3))]
        if d.empty:
            continue
        d['model'] = Path(f).parent.name
        d['level'] = d.output_type_id.astype(float).round(3)
        hubdf.append(d[['model', 'reference_date', 'horizon', 'location', 'level', 'value']])
    hubdf = pd.concat(hubdf)
    allf = pd.concat([hubdf, cands])
    allf['level'] = allf.level.round(3)
    t = pd.read_csv(hub / 'target-data' / truth_file, dtype={'location': str})
    truth = t.set_index(['date', 'location']).value
    allf['target_end_date'] = (pd.to_datetime(allf.reference_date) + pd.to_timedelta(7 * allf.horizon, 'D')).dt.strftime('%Y-%m-%d')
    allf['truth'] = [truth.get((d, l), np.nan) for d, l in zip(allf.target_end_date, allf.location)]
    allf = allf.dropna(subset=['truth', 'value'])
    nq = allf.groupby(['model', 'reference_date', 'horizon', 'location'])['level'].transform('count')
    allf = allf[nq == 23]  # complete 23-level quantile sets only
    if a.target == 'hosp':
        allf['value'], allf['truth'] = np.log1p(allf.value.clip(lower=0)), np.log1p(allf.truth)
    scores = wis_long(allf)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    print(f'Truth: {truth_file} (latest date {t.date.max()}); reference dates {refs[0]}..{refs[-1]}; '
          f'{scores.model.nunique()} models; {"WIS of log(1+admissions)" if a.target == "hosp" else "natural WIS of ED share"}')
    ours = [c.split('=')[0] for c in a.candidate] + ['ACCIDDA-Chromantis', 'FluSight-ensemble', 'FluSight-baseline']
    for geo, sel in (('states_dc + US', scores), ('states_dc', scores[scores.location != 'US'])):
        r = pairwise(sel)
        r.to_csv(Path(a.out) / f'{a.target}-{geo.replace(" + ", "_").replace(" ", "")}.csv')
        print(f'\n== {geo}: {len(r)} models ranked; top 10 and ours')
        print(r.head(10).round(3).to_string())
        print(r.loc[[m for m in ours if m in r.index]].round(3).to_string())
    by = scores[scores.model.isin(ours)].groupby(['model', 'reference_date']).wis.mean().unstack()
    print('\nMean WIS by reference date (all locations, tasks each model covers):')
    print(by.round(3).to_string())


if __name__ == '__main__':
    main()
