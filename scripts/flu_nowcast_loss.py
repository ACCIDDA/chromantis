"""How much flu forecast skill is lost to incomplete recent reports, by horizon; and how this season's revisions
compare with the revisions the models were trained on and with the correction trees.

Part 1 (inputs): the saved B7 (30 fits) and Bes (10 fits) checkpoints, no retraining, run on six 2026-27
issuances (7 Oct - 11 Nov; reference dates 10 Oct - 14 Nov) with
  - each Wednesday's reports, trees at strength 1, 0.5 and 0 (production/output/<issuance>/<release>/), and for B7
    "matched": trees at 1 for A_blocks3 and B5 (trained on tree-corrected histories), 0 for B_width256,
  - the same histories as known on 18 Nov 2026, trees off (scripts/flu_oracle_inputs.py).
Scored on the 50 states + DC, horizons 0-3, against (a) the 18 Nov data and (b) the 18 Nov data times each
state's median remaining revision in 2025-26 (scripts/flusight_revision_impact.py writes both truths).

Part 2 (revisions): state-level revision of the newest (lag 0) and second-newest (lag 1) reported weeks,
log((report + floor) / (final + floor)) with floor = max(5% of the state's 2025-26 peak, 1 admission or 0.0001):
the same scale as the training reporting errors (dataset/reporting_error.py). 2025-26 Nov-Jan reports are the
donor bank the models were trained on (B7 at strength 1, Bes at 1.5). 2026-27 is measured two weeks later (its
weeks are not final). Tree corrections are each fit's saved nowcaster applied to the 18 Nov panel's reports.

Usage: .venv/bin/python scripts/flu_nowcast_loss.py [out_dir]
"""
import glob, json, os, pickle, sys, warnings; warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else 'production/output/2026-11-20/nowcast-loss'
os.makedirs(OUT, exist_ok=True)
REV = 'production/output/2026-11-20/revisions'
HUB = 'production/hubs/FluSight-forecast-hub'
ISS = ['2026-10-07', '2026-10-14', '2026-10-21', '2026-10-28', '2026-11-04', '2026-11-11']
VARIANTS = {  # name: path pattern (iss, ref)
    'B7 reports, trees 1': 'production/output/{iss}/b7-20261009/{ref}-ACCIDDA-Chromantis.csv',
    'B7 reports, trees 0.5': 'production/output/{iss}/b7-cs050/{ref}-ACCIDDA-Chromantis.csv',
    'B7 reports, trees 0': 'production/output/{iss}/b7-cs000/{ref}-ACCIDDA-Chromantis.csv',
    'B7 reports, trees matched': 'production/output/{iss}/b7-matched/{ref}-ACCIDDA-Chromantis.csv',
    'B7 18-Nov inputs': 'production/output/2026-11-20/oracle-inputs/{iss}/b7-cs000/{ref}-ACCIDDA-Chromantis.csv',
    'Bes reports, trees 1': 'production/output/{iss}/bes-20261010/{ref}-ACCIDDA-Chromantis.csv',
    'Bes reports, trees 0.5': 'production/output/{iss}/bes-cs050/{ref}-ACCIDDA-Chromantis.csv',
    'Bes reports, trees 0': 'production/output/{iss}/bes-cs000/{ref}-ACCIDDA-Chromantis.csv',
    'Bes 18-Nov inputs': 'production/output/2026-11-20/oracle-inputs/{iss}/bes-cs000/{ref}-ACCIDDA-Chromantis.csv',
}
HUBM = {'Submitted (ACCIDDA-Chromantis)': 'ACCIDDA-Chromantis', 'FluSight-ensemble': 'FluSight-ensemble',
        'FluSight-baseline': 'FluSight-baseline'}
loc = pd.read_csv(f'{HUB}/auxiliary-data/locations.csv', dtype={'location': str})
STATES = [l for l in loc.location if l not in ('US', '72')]
AB = loc.set_index('location').abbreviation
pd.set_option('display.width', 250)
log = open(f'{OUT}/summary.txt', 'w')


def say(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n'); log.flush()


def read(p):
    f = pd.read_csv(p, dtype={'location': str})
    f = f[(f.output_type == 'quantile') & (pd.to_numeric(f.horizon, errors='coerce') >= 0)]
    f['location'] = f.location.str.zfill(2)
    f = f[f.location.isin(STATES)].copy()
    f['q'] = f.output_type_id.astype(float); f['horizon'] = f.horizon.astype(int)
    return f[['target', 'location', 'horizon', 'target_end_date', 'q', 'value']]


rows = []
for iss in ISS:
    ref = (pd.Timestamp(iss) + pd.Timedelta(days=3)).strftime('%Y-%m-%d')
    for name, pat in VARIANTS.items():
        rows.append(read(pat.format(iss=iss, ref=ref)).assign(model=name, ref=ref))
    for name, m in HUBM.items():
        rows.append(read(f'{HUB}/model-output/{m}/{ref}-{m}.csv').assign(model=name, ref=ref))
F = pd.concat(rows)


def scores(F, truth, target):
    g = F[F.target == target].merge(truth, left_on=['location', 'target_end_date'], right_on=['location', 'week'])
    g = g[g.groupby(['model', 'ref', 'location', 'horizon']).q.transform('size') == 23].sort_values('q')
    v, y = g.value.values.astype(float), g.y.values.astype(float)
    if target == 'wk inc flu hosp':
        v, y = np.log1p(np.maximum(v, 0)), np.log1p(y)
    else:
        v, y = np.log(np.maximum(v, 1e-5)), np.log(np.maximum(y, 1e-5))  # bias on log scale; WIS below on native
    g['lv'], g['ly'] = v, y
    g['pin'] = 2 * ((y <= v) - g.q.values) * (v - y)
    if target != 'wk inc flu hosp':
        vn, yn = g.value.values.astype(float), g.y.values.astype(float)
        g['pin'] = 2 * ((yn <= vn) - g.q.values) * (vn - yn)
    k = ['model', 'ref', 'location', 'horizon']
    s = g.groupby(k).agg(wis=('pin', 'mean')).join(
        g[g.q == .5].set_index(k).eval('lv - ly').rename('bias')).join(
        g[g.q == .25].set_index(k).eval('lv <= ly').rename('a')).join(
        g[g.q == .75].set_index(k).eval('lv >= ly').rename('b')).reset_index()
    s['in50'] = s.a & s.b
    return s.drop(columns=['a', 'b'])


TR = {'18 Nov data': 'asof-latest', '18 Nov data x expected remaining revision (2025-26)': '2025-26'}
res = {}
for tgt, short, nm in [('wk inc flu hosp', 'adm', 'log admissions'), ('wk inc flu prop ed visits', 'ed', 'ED share')]:
    for tl, tf in TR.items():
        truth = pd.read_csv(f'{REV}/truth-{short}-{tf}.csv', dtype={'location': str})
        s = scores(F, truth, tgt)
        w = s.pivot_table(index=['ref', 'location', 'horizon'], columns='model', values='wis').dropna()
        keep = set(w.index)
        s = s[[x in keep for x in zip(s.ref, s.location, s.horizon)]]
        res[(nm, tl)] = s
        say(f'\n== {nm}, truth: {tl}. States + DC, reference dates 10 Oct - 14 Nov, tasks every variant covers ({len(w)}).')
        say('WIS / FluSight-baseline WIS on the same tasks (lower is better); in brackets WIS / FluSight-ensemble WIS.')
        base = w['FluSight-baseline'].groupby('horizon').mean(); ens = w['FluSight-ensemble'].groupby('horizon').mean()
        tab = {}
        for m in list(HUBM)[:2] + list(VARIANTS):
            mm = w[m].groupby('horizon').mean()
            tot = w[m].mean() / w['FluSight-baseline'].mean(); tote = w[m].mean() / w['FluSight-ensemble'].mean()
            tab[m] = [f'{a / b:.3f} ({a / c:.2f})' for a, b, c in zip(mm, base, ens)] + [f'{tot:.3f} ({tote:.2f})']
        say(pd.DataFrame(tab, index=[f'h{h}' for h in base.index] + ['all']).T.to_string())
        b = s.groupby(['model', 'horizon']).bias.mean().unstack().round(3)
        c = s.groupby(['model', 'horizon']).in50.mean().unstack().round(2)
        say('Mean log(median / observed) by horizon (positive = too high):')
        say(b.loc[list(HUBM)[:2] + list(VARIANTS)].to_string())
        say('50% interval coverage by horizon:')
        say(c.loc[list(HUBM)[:2] + list(VARIANTS)].to_string())
        # loss attributable to incomplete reports: reports (submitted tree strength) vs 18-Nov inputs
        for mdl in ('B7', 'Bes'):
            r0 = w[f'{mdl} reports, trees 0'].groupby('horizon').mean()
            r5 = w[f'{mdl} reports, trees 0.5'].groupby('horizon').mean()
            o = w[f'{mdl} 18-Nov inputs'].groupby('horizon').mean()
            say(f'{mdl}: WIS with 18-Nov inputs / WIS with reports (trees 0; trees 0.5) by horizon: ' + ', '.join(
                f'h{h}: {o[h] / r0[h]:.2f}; {o[h] / r5[h]:.2f}' for h in o.index))
        if tl == '18 Nov data':
            byref = w.groupby(['ref', 'horizon']).mean()
            say('By reference date, horizon 0, WIS / baseline:')
            say((byref[[*list(HUBM)[:2], 'B7 reports, trees 0.5', 'B7 18-Nov inputs', 'Bes reports, trees 0.5', 'Bes 18-Nov inputs']]
                 .xs(0, level='horizon').div(byref['FluSight-baseline'].xs(0, level='horizon'), axis=0)).round(3).to_string())

# Figure: WIS / baseline by horizon
fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
sty = {'reports, trees 1': ('#eb6834', '-'), 'reports, trees 0.5': ('#c9a227', '-'), 'reports, trees 0': ('#7a7a74', '-'),
       'reports, trees matched': ('#2a78d6', '-'), '18-Nov inputs': ('#1baf7a', '-')}
for row, nm in enumerate(['log admissions', 'ED share']):
    for col, mdl in enumerate(['B7', 'Bes']):
        ax = axes[row, col]
        for (tl, ls) in zip(TR, ['-', '--']):
            s = res[(nm, tl)]
            w = s.pivot_table(index=['ref', 'location', 'horizon'], columns='model', values='wis')
            base = w['FluSight-baseline'].groupby('horizon').mean()
            for suf, (c, _) in sty.items():
                if f'{mdl} {suf}' not in w:
                    continue
                y = w[f'{mdl} {suf}'].groupby('horizon').mean() / base
                ax.plot(y.index, y.values, ls, color=c, marker='o', ms=4, lw=1.8, label=f'{mdl} {suf}' if ls == '-' else None)
            y = w['FluSight-ensemble'].groupby('horizon').mean() / base
            ax.plot(y.index, y.values, ls, color='k', marker='s', ms=4, lw=1.4, label='FluSight-ensemble' if ls == '-' else None)
        ax.set_title(f'{mdl}, {nm}: mean WIS / FluSight-baseline (solid: 18 Nov data; dashed: x expected revision)', fontsize=9)
        ax.set_xticks([0, 1, 2, 3]); ax.grid(alpha=.3); ax.legend(fontsize=8)
        if row == 1:
            ax.set_xlabel('horizon (weeks after the reference date; 0 = the not-yet-reported week)')
fig.suptitle('Saved fits on each Wednesday\'s reports (trees at strength 1, 0.5, 0) vs on the histories as known 18 Nov. '
             'States + DC, reference dates 10 Oct - 14 Nov 2026', fontsize=10)
fig.tight_layout(); fig.savefig(f'{OUT}/4-wis-by-horizon-inputs.png', dpi=120); plt.close(fig)


# ---------- Part 2: revisions vs training errors vs trees ----------
A = pd.read_csv(f'{REV}/vintages-admissions.csv.gz', dtype={'location': str})
E = pd.read_csv(f'{REV}/vintages-ed.csv.gz', dtype={'location': str})


def errors(V, unit_floor, later_k=None):
    """log((value at lag k + floor)/(reference + floor)); reference = latest value, or value later_k weeks later."""
    V = V[V.location.isin(STATES)].copy()
    peak = V[V.season == '2025-26'].groupby('location').final.max()
    V['floor'] = np.maximum(.05 * V.location.map(peak), unit_floor)
    if later_k:
        idx = V.set_index(['location', 'week', 'lag']).value
        V['ref'] = [idx.get((l, w, k + later_k), np.nan) for l, w, k in zip(V.location, V.week, V.lag)]
    else:
        V['ref'] = V.final
    V['e'] = np.log((V.value + V.floor) / (V.ref + V.floor))
    return V.dropna(subset=['e'])


cats, NOW2 = {}, {}
for short, V, uf in [('adm', A, 1.0), ('ed', E, 1e-4)]:
    fin, two = errors(V, uf), errors(V, uf, 2)
    bank = fin[(fin.season == '2025-26') & (fin.week >= '2025-11-08') & (fin.week <= '2026-01-31')]
    bank2 = two[(two.season == '2025-26') & (two.week >= '2025-11-08') & (two.week <= '2026-01-31')]
    now2 = two[two.season == '2026-27']
    NOW2[short] = now2
    nowf = fin[fin.season == '2026-27']
    for lag in (0, 1):
        cats[(short, lag)] = {
            '2025-26 Nov-Jan vs final\n(training errors, x1: B7)': -bank[bank.lag == lag].e.values,
            '2025-26 Nov-Jan vs final\nx1.5 (Bes)': -1.5 * bank[bank.lag == lag].e.values,
            '2025-26 Nov-Jan\nvs 2 weeks later': -bank2[bank2.lag == lag].e.values,
            '2026-27 so far\nvs 2 weeks later': -now2[now2.lag == lag].e.values,
            '2026-27 so far\nvs 18 Nov (incomplete)': -nowf[nowf.lag == lag].e.values,
        }

# trees: each fit's saved nowcaster on the 18 Nov panel's reports, 2026-27 issuances
sys.path.insert(0, 'src')
from chromantis.dataset.build import load, for_hub
from chromantis.dataset.episodes import episodes
from chromantis.model.scenario import Scenario
from chromantis.problem import Problem
panel = for_hub(load('data/operational-20261118/processed/panel.npz'), 'flusight')
cache, trows = {}, []
ABSET = {AB[s] for s in STATES}
# same floor as the revisions above: max(5% of the state's 2025-26 peak, unit floor)
FLOOR = {short: {AB[l]: max(.05 * v, uf) for l, v in V[(V.season == '2025-26') & V.location.isin(STATES)].groupby('location').final.max().items()}
         for short, V, uf in [('adm', A, 1.0), ('ed', E, 1e-4)]}
for mdl, path in [('B7', 'production/releases/b7-20261009.json'), ('Bes', 'production/releases/bes-20261010.json')]:
    r = json.load(open(path)); problem = Problem.load(r['problem'])
    for recipe, members in r['recipes'].items():
        for m in members:
            ck = Path(m['checkpoint'])
            sc = Scenario.from_string(json.loads((ck / 'manifest.json').read_text())['scenario'])
            key = (problem.reference, sc.lookback, sc.input_set, sc.covariate_set)
            if key not in cache:
                e = episodes(panel, problem, problem.input_names(sc.input_set), sc.lookback, 'reported',
                             problem.covariate_names(sc.covariate_set), horizons=problem.horizons, require_labels=False)
                cache[key] = [x for x in e if '2026-10-01' <= x['issuance'] <= '2026-11-18']
            eps = cache[key]
            nc = pickle.load(open(ck / 'nowcaster.pkl', 'rb'))
            for e, c in zip(eps, nc.apply_batch([dict(x) for x in eps])):
                locs = list(e['locations'])
                for lag in (0, 1):
                    for ch, short in ((0, 'adm'), (1, 'ed')):
                        a, b = e['values'][-1 - lag, ch], c['values'][-1 - lag, ch]
                        for i, l in enumerate(locs):
                            if l in ABSET and e['available'][-1 - lag, ch, i] and a[i] > 0:
                                trows.append(dict(model=mdl, recipe=recipe, issuance=e['issuance'], location=l, lag=lag,
                                                  target=short, f=np.log((b[i] + FLOOR[short][l]) / (a[i] + FLOOR[short][l]))))
T = pd.DataFrame(trows).groupby(['model', 'recipe', 'issuance', 'location', 'lag', 'target']).f.mean().reset_index()
T = T.groupby(['model', 'issuance', 'location', 'lag', 'target']).f.mean().reset_index()  # equal weight per recipe
for (short, lag) in cats:
    for mdl in ('B7', 'Bes'):
        cats[(short, lag)][f'{mdl} trees on 2026-27\nreports (strength 1)'] = T[(T.model == mdl) & (T.lag == lag) & (T.target == short)].f.values

say('\n== Revision of the newest reported weeks, states + DC: final/report factor, exp of the log revision with floor '
    '(see docstring). Median [10th-90th percentile] (n state-weeks) ==')
for (short, lag), d in cats.items():
    say(f'-- {"admissions" if short == "adm" else "ED share"}, lag {lag} ({"newest" if lag == 0 else "second-newest"} week)')
    for k, v in d.items():
        q = np.exp(np.quantile(v, [.1, .5, .9]))
        say(f'   {k.replace(chr(10), " "):55s} x{q[1]:.3f} [{q[0]:.3f}-{q[2]:.3f}] (n={len(v)})  share > x1.10: {np.mean(np.exp(v) > 1.10):.2f}')

say('\n== Do the trees know WHICH states will be revised? 2026-27 state-weeks, tree log-correction vs actual log revision '
    'two weeks later (same floor) ==')
for short in ('adm', 'ed'):
    act = NOW2[short].assign(location=lambda d: d.location.map(AB))[['report', 'location', 'lag', 'e']]
    for mdl in ('B7', 'Bes'):
        m = T[(T.model == mdl) & (T.target == short)].merge(act, left_on=['issuance', 'location', 'lag'], right_on=['report', 'location', 'lag'])
        for lag in (0, 1):
            x = m[m.lag == lag]; rev = -x.e
            r2 = 1 - ((rev - x.f) ** 2).mean() / ((rev - rev.mean()) ** 2).mean()
            r2h = 1 - ((rev - .5 * x.f) ** 2).mean() / ((rev - rev.mean()) ** 2).mean()
            say(f'  {short} {mdl} lag {lag}: n={len(x)}, Spearman {x.f.corr(rev, method="spearman"):.2f}, '
                f'R2 of tree as prediction {r2:.2f} (strength 0.5: {r2h:.2f}); mean tree {np.exp(x.f.mean()):.3f} vs mean actual {np.exp(rev.mean()):.3f}; '
                f'RMSE tree {np.sqrt(((rev - x.f) ** 2).mean()):.3f}, no correction {np.sqrt((rev ** 2).mean()):.3f}')

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
colors = ['#7a7a74', '#b9b8b0', '#a3c4e6', '#1baf7a', '#8fd9bd', '#2a78d6', '#eb6834']
for ax, ((short, lag), d) in zip(axes.flat, cats.items()):
    ks = list(d)
    bp = ax.boxplot([np.exp(d[k]) for k in ks], whis=(10, 90), showfliers=False, patch_artist=True, widths=.6)
    for patch, c in zip(bp['boxes'], colors):
        patch.set_facecolor(c); patch.set_alpha(.8)
    ax.set_xticklabels(ks, fontsize=7, rotation=0)
    ax.axhline(1, color='k', lw=.8); ax.grid(alpha=.3, axis='y')
    ax.set_ylim(.9, 1.45 if short == 'adm' else 1.2)
    ax.set_title(f'{"Admissions" if short == "adm" else "ED share"}, {"newest" if lag == 0 else "second-newest"} reported week '
                 f'(lag {lag}): later value / reported value, per state-week (box 25-75%, whiskers 10-90%)', fontsize=9)
fig.tight_layout(); fig.savefig(f'{OUT}/5-revisions-vs-training-and-trees.png', dpi=120); plt.close(fig)
log.close()
