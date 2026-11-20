"""How much do data revisions change FluSight scores? Revision curves to 30 weeks and Hub rescoring by truth vintage.

1. Revision curves: for every state and week of 2024-25, 2025-26 and 2026-27, the value reported k weeks after its
   first report (lag k = 0..30) divided by its value in the latest report (18 Nov 2026 = "final"). Admissions
   (NHSN, sum over 50 states + DC for national) and ED share (NSSP).
2. Rescoring 2024-25 and 2025-26: every Hub model's forecasts (quantiles, horizons 0-3, 50 states + DC) scored
   against the truth as it stood k weeks after the target week was first reported, k = 0, 1, 2, 4, 8, and final.
   The CDC weekly report scores the newest target weeks at k = 0 and 1. Pairwise relative WIS on log(1+admissions).
3. 2026-27 so far: the same scoring against the 18 Nov data, and against that data multiplied by the median
   remaining revision (final / value at the same lag) observed in 2025-26 and in 2024-25, per lag.

Truth vintages: Delphi's NHSN and NSSP archives, one report per week (Wednesday, else Thursday, else Tuesday),
labelled by that week's Wednesday; the hub's values equal Delphi's for the same Wednesday (checked in
scripts/report_reporting_delays.py). ED share for 2026-27 vintages comes from the hub's time-series.

Usage: .venv/bin/python scripts/flusight_revision_impact.py [out_dir]
"""
import glob, os, sys, warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else 'production/output/2026-11-20/revisions'
os.makedirs(OUT, exist_ok=True)
HUB = 'production/hubs/FluSight-forecast-hub'
NHSN = sorted(glob.glob('data/raw/delphi_nhsn/snapshots/*/'))[-1]
NSSP = sorted(glob.glob('data/raw/delphi_nssp/snapshots/*/'))[-1]
SEASONS = ['2024-25', '2025-26', '2026-27']
COL = {'2024-25': '#2a78d6', '2025-26': '#d6612a', '2026-27': '#1baf7a'}
MAXLAG = 30
pd.set_option('display.width', 250)
log = open(f'{OUT}/summary.txt', 'w')


def say(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n'); log.flush()


loc = pd.read_csv(f'{HUB}/auxiliary-data/locations.csv', dtype={'location': str})
STATES = [l for l in loc.location if l not in ('US', '72')]
AB = dict(zip(loc.abbreviation.str.lower(), loc.location))


def season(w):
    w = pd.to_datetime(pd.Series(w))
    y = np.where(w.dt.month >= 8, w.dt.year, w.dt.year - 1)
    return pd.Series([f'{a}-{str(a + 1)[2:]}' for a in y], index=w.index).values


def delphi(path, scale=1.0):
    d = pd.read_csv(path)
    d['rday'] = pd.to_datetime(d.report_time).dt.tz_convert('America/New_York').dt.date.astype(str)
    d['location'] = d.geo_value.map(AB).fillna(d.geo_value.str.upper())
    d['value'] = d.value * scale
    return d[['rday', 'location', 'reference_time', 'value']].rename(columns={'reference_time': 'week'})


def asof(d, rday):
    return d[d.rday <= rday].sort_values('rday').groupby(['location', 'week']).value.last().reset_index()


def slot_reports(d):
    """One report per week: Wednesday if there is one, else Thursday, else Tuesday; keyed by that week's Wednesday."""
    r = pd.Series(sorted(d.rday.unique())); dt = pd.to_datetime(r)
    r = r[dt.dt.dayofweek.isin([1, 2, 3])]; dt = pd.to_datetime(r)
    pref = dt.dt.dayofweek.map({2: 0, 3: 1, 1: 2})
    wk = (dt - pd.to_timedelta((dt.dt.dayofweek - 2) % 7, 'D')).dt.strftime('%Y-%m-%d')
    s = pd.DataFrame(dict(rday=r.values, wed=wk.values, pref=pref.values)).sort_values('pref').drop_duplicates('wed')
    return dict(zip(s.wed, s.rday))


# ---------- vintages: value[report, location, week] ----------
dadm = delphi(f'{NHSN}signal=confirmed_admissions_flu_ew/geo_type=state/archive.csv.gz')
dadm = dadm[dadm.location.isin(STATES)]
adm = pd.concat([asof(dadm, r).assign(report=w) for w, r in slot_reports(dadm).items()])
nat = adm.groupby(['report', 'week']).agg(value=('value', 'sum'), n=('value', 'size')).reset_index()
adm = pd.concat([adm, nat[nat.n == len(STATES)].drop(columns='n').assign(location='US')])

ned = pd.concat([delphi(f'{NSSP}signal=pct_ed_visits_influenza/geo_type={g}/archive.csv.gz', 0.01) for g in ('state', 'nation')])
ned = ned[ned.location.isin(STATES + ['US'])]
nus = ned[ned.location == 'US'].sort_values('rday')
keep, seen = {}, set()
for r in nus.rday.unique():  # each NSSP release that first carries a new week ending <= 6 days earlier
    w = nus[nus.rday <= r].week.max()
    if w not in seen and (pd.Timestamp(r) - pd.Timestamp(w)).days <= 6:
        keep[(pd.Timestamp(w) + pd.Timedelta(days=4)).strftime('%Y-%m-%d')] = r
    seen.add(w)
ed = pd.concat([asof(ned, r).assign(report=w) for w, r in keep.items()])
ts = pd.read_csv(f'{HUB}/target-data/time-series.csv', dtype={'location': str})
ts = ts.drop_duplicates(['target', 'as_of', 'location', 'target_end_date'], keep='last')
hed = ts[(ts.target == 'wk inc flu prop ed visits') & ts.location.isin(STATES + ['US'])]
hed = hed.rename(columns={'as_of': 'report', 'target_end_date': 'week', 'observation': 'value'})[['report', 'location', 'week', 'value']]
ed = pd.concat([ed[~ed.report.isin(hed.report.unique())], hed])


def with_lag(v):
    v = v.copy()
    v['lag'] = ((pd.to_datetime(v.report) - pd.Timedelta(days=4) - pd.to_datetime(v.week)).dt.days // 7).astype(int)
    last = v.report.max()
    fin = v[v.report == last][['location', 'week', 'value']].rename(columns={'value': 'final'})
    v = v[v.lag.between(0, MAXLAG)].merge(fin, on=['location', 'week'])
    m = pd.to_datetime(v.week).dt.month
    v['season'] = season(v.week)
    return v[v.season.isin(SEASONS) & ((m >= 10) | (m <= 5))], last


A, lastA = with_lag(adm)
E, lastE = with_lag(ed)
A.to_csv(f'{OUT}/vintages-admissions.csv.gz', index=False); E.to_csv(f'{OUT}/vintages-ed.csv.gz', index=False)
say(f'Vintages: admissions {adm.report.min()}..{lastA} ({adm.report.nunique()} reports), '
    f'ED share {ed.report.min()}..{lastE} ({ed.report.nunique()} reports). "final" = latest report.')


# ---------- 1. revision curves ----------
def ratio_table(V, locs):
    x = V[V.location.isin(locs) & (V.final > 0) & (V.value > 0)].copy()
    x['r'] = x.value / x.final
    return x


for name, V, unit in [('admissions', A, 'admissions'), ('ED share', E, 'ED share')]:
    say(f'\n== {name}: value at lag k / final value, median [10th-90th percentile] over in-season weeks ==')
    for where, locs in [('national', ['US']), ('states+DC (pooled state-weeks)', STATES)]:
        x = ratio_table(V, locs)
        if where.startswith('states') and name == 'admissions':
            x = x[x.final >= 20]  # drop near-zero state-weeks whose ratios are noise
        tab = x.groupby(['season', 'lag']).r.quantile([.1, .5, .9]).unstack()
        say(f'-- {where}' + (' (final >= 20 admissions)' if where.startswith('states') and name == 'admissions' else ''))
        rows = []
        for s in SEASONS:
            if s not in tab.index.get_level_values(0):
                continue
            t = tab.loc[s]
            rows.append([s] + [f'{t.loc[k, .5]:.3f} [{t.loc[k, .1]:.2f}-{t.loc[k, .9]:.2f}]' if k in t.index else '-'
                               for k in (0, 1, 2, 4, 8, 12, 20)])
        say(pd.DataFrame(rows, columns=['season', 'k=0', 'k=1', 'k=2', 'k=4', 'k=8', 'k=12', 'k=20']).to_string(index=False))

# Figure 1: national curves at several vintages
fig, axes = plt.subplots(2, 3, figsize=(17, 8.5))
for row, (V, lab, sc) in enumerate([(A, 'flu admissions, sum of 50 states + DC', 1), (E, 'flu ED share, national (%)', 100)]):
    for col, s in enumerate(SEASONS):
        ax = axes[row, col]
        x = V[(V.location == 'US') & (V.season == s)]
        f = x.drop_duplicates('week').sort_values('week')
        ax.plot(pd.to_datetime(f.week), f.final * sc, color='k', lw=2.2, label=f'latest ({lastA if row == 0 else lastE})')
        for k, c in zip([0, 1, 2, 4, 8], ['#d62a2a', '#e8892b', '#c9b52a', '#2a9fd6', '#7b4fd6']):
            y = x[x.lag == k].sort_values('week')
            ax.plot(pd.to_datetime(y.week), y.value * sc, 'o-', ms=2.5, lw=1, color=c, label=f'{k} wk after first report' if k else 'first report')
        ax.set_title(f'{s}: {lab}', fontsize=10)
        ax.tick_params(labelsize=8); ax.grid(alpha=.3)
        if col == 0 and row == 0:
            ax.legend(fontsize=8)
fig.suptitle('Each week as reported in successive Wednesday releases vs the latest release', fontsize=12)
fig.tight_layout(); fig.savefig(f'{OUT}/1-national-vintages.png', dpi=130); plt.close(fig)

# Figure 2: revision factor final / value at lag k, out to 30 weeks
fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
for row, (V, lab) in enumerate([(A, 'admissions'), (E, 'ED share')]):
    for col, (where, locs) in enumerate([('national', ['US']), ('states + DC', STATES)]):
        ax = axes[row, col]
        x = ratio_table(V, locs)
        if col == 1 and row == 0:
            x = x[x.final >= 20]
        x['f'] = 1 / x.r
        for s in SEASONS:
            q = x[x.season == s].groupby('lag').f.quantile([.1, .25, .5, .75, .9]).unstack()
            if q.empty:
                continue
            if col == 0:  # one thin line per week
                for w, g in x[x.season == s].groupby('week'):
                    ax.plot(g.lag, g.f, color=COL[s], alpha=.12, lw=.7)
            else:
                ax.fill_between(q.index, q[.1], q[.9], color=COL[s], alpha=.12)
                ax.fill_between(q.index, q[.25], q[.75], color=COL[s], alpha=.2)
            ax.plot(q.index, q[.5], color=COL[s], lw=2.2, label=f'{s} median' + (' (not final yet)' if s == '2026-27' else ''))
        ax.axhline(1, color='k', lw=.8); ax.axvline(4, color='gray', ls='--', lw=.8)
        ax.set_title(f'{lab}, {where}: latest value / value k weeks after first report'
                     + (' (bands 10-90%, 25-75% of state-weeks; final >= 20)' if col == 1 and row == 0 else
                        ' (bands 10-90%, 25-75% of state-weeks)' if col == 1 else ' (thin: each week)'), fontsize=9)
        ax.set_ylim(0.85, 1.35 if row == 0 else 1.25); ax.grid(alpha=.3); ax.legend(fontsize=8)
        if row == 1:
            ax.set_xlabel('k = weeks since the week was first reported')
fig.tight_layout(); fig.savefig(f'{OUT}/2-revision-factor-by-lag.png', dpi=130); plt.close(fig)


# ---------- 2. rescoring Hub models by truth vintage ----------
def read_forecasts(seasons):
    rows = []
    for p in glob.glob(f'{HUB}/model-output/*/20*'):
        ref = os.path.basename(p)[:10]
        if season([ref])[0] not in seasons:
            continue
        f = pd.read_parquet(p) if p.endswith('.parquet') else pd.read_csv(p, dtype={'location': str})
        f = f[(f.output_type == 'quantile') & f.target.isin(['wk inc flu hosp', 'wk inc flu prop ed visits'])]
        f = f[pd.to_numeric(f.horizon, errors='coerce').between(0, 3)]
        f['location'] = f.location.astype(str).str.zfill(2)
        f = f[f.location.isin(STATES)]
        if len(f):
            rows.append(f.assign(model=os.path.basename(os.path.dirname(p)), ref=ref)[
                ['model', 'ref', 'target', 'location', 'horizon', 'target_end_date', 'output_type_id', 'value']])
    f = pd.concat(rows)
    f['q'] = f.output_type_id.astype(float); f['horizon'] = f.horizon.astype(int)
    f['target_end_date'] = pd.to_datetime(f.target_end_date).dt.strftime('%Y-%m-%d')
    return f


def wis_table(f, truth):
    """truth: location, week, y. Returns model, ref, location, horizon, wis on log1p (hosp) or native (ED)."""
    g = f.merge(truth, left_on=['location', 'target_end_date'], right_on=['location', 'week'])
    g = g[g.groupby(['model', 'ref', 'location', 'horizon']).q.transform('size') == 23]
    v, y = g.value.values.astype(float), g.y.values.astype(float)
    if g.target.iloc[0] == 'wk inc flu hosp':
        v, y = np.log1p(np.maximum(v, 0)), np.log1p(y)
    g['pin'] = 2 * ((y <= v) - g.q.values) * (v - y)
    return g.groupby(['model', 'ref', 'location', 'horizon']).agg(wis=('pin', 'mean')).reset_index()


def pairwise(w, base='FluSight-baseline', min_frac=.5):
    w = w.pivot_table(index=['ref', 'location', 'horizon'], columns='model', values='wis')
    w = w.loc[:, w.notna().mean() >= min_frac * w[base].notna().mean()]
    M = w.values; n = M.shape[1]; th = np.zeros(n)
    for i in range(n):
        rr = []
        for j in range(n):
            if i != j:
                m = ~np.isnan(M[:, i]) & ~np.isnan(M[:, j])
                if m.any() and M[m, j].mean() > 0:
                    rr.append(M[m, i].mean() / M[m, j].mean())
        th[i] = np.exp(np.mean(np.log(rr)))
    s = pd.Series(th, index=w.columns)
    return s / s[base]


def vintage_truth(V, k):
    """Truth for each week as it stood k weeks after its first report; k='final' for the latest report."""
    if k == 'final':
        return V.drop_duplicates(['location', 'week'])[['location', 'week', 'final']].rename(columns={'final': 'y'})
    return V[V.lag == k][['location', 'week', 'value']].rename(columns={'value': 'y'})


VINT = [0, 1, 2, 4, 8, 'final']
say('\n== Rescoring Hub models (states + DC, horizons 0-3, quantile forecasts) against each truth vintage ==')
say('Relative WIS = pairwise (geometric mean of mean-WIS ratios over opponents on shared tasks) / baseline\'s; '
    'lower is better. Admissions scored on log(1+count), ED share on its native scale.')
say('Only tasks whose target week has every vintage (k=0..8 and final) are scored, so the task set is identical.')
F = read_forecasts(['2024-25', '2025-26'])
res = {}
for tgt, V, nm in [('wk inc flu hosp', A, 'log admissions'), ('wk inc flu prop ed visits', E, 'ED share')]:
    for s in ['2024-25', '2025-26']:
        f = F[(F.target == tgt) & (season(F.ref) == s)]
        if f.empty:
            continue
        Vs = V[V.location.isin(STATES)]
        weeks = None
        for k in VINT:
            t = vintage_truth(Vs, k); ok = set(map(tuple, t[['location', 'week']].values))
            weeks = ok if weeks is None else weeks & ok
        T = {}
        for k in VINT:
            t = vintage_truth(Vs, k)
            t = t[[x in weeks for x in map(tuple, t[['location', 'week']].values)]]
            T[k] = pairwise(wis_table(f, t))
        R = pd.DataFrame(T)
        med = f[f.q == .5].merge(vintage_truth(Vs, 'final'), left_on=['location', 'target_end_date'], right_on=['location', 'week'])
        med = med.groupby('model').apply(lambda g: g.value.sum() / g.y.sum())
        R['median/final'] = med.reindex(R.index)
        res[(nm, s)] = R
        rk = R[VINT].rank()
        say(f'\n-- {nm}, {s}: {len(R)} models, {len(weeks)} location-weeks')
        say('Spearman rank correlation of relative WIS with the final-truth ranking: ' +
            ', '.join(f'k={k}: {rk[k].corr(rk["final"]):.3f}' for k in VINT[:-1]))
        d = (rk[0] - rk['final'])
        say(f'Rank change from k=0 truth to final truth: median |change| {d.abs().median():.0f}, '
            f'90th pct {d.abs().quantile(.9):.0f}, max {d.abs().max():.0f} (of {len(R)})')
        say('Correlation between a model\'s median/final (bias against final truth) and its rank gain from k=0 to final: '
            f'{(rk[0] - rk["final"]).corr(R["median/final"]):.2f}')
        show = R.sort_values('final').copy()
        for k in VINT:
            show[f'rank k={k}'] = rk[k].reindex(show.index).astype(int)
        say(show.round(3).to_string())

# Figure 3: rel WIS against k=0 truth vs final truth, per model
pan = [k for k in res]
fig, axes = plt.subplots(1, len(pan), figsize=(5.2 * len(pan), 5))
for ax, key in zip(np.atleast_1d(axes), pan):
    R = res[key]
    sc = ax.scatter(R[0], R['final'], c=R['median/final'], cmap='coolwarm', vmin=.8, vmax=1.2, s=22)
    for m in ['FluSight-ensemble', 'FluSight-baseline']:
        if m in R.index:
            ax.annotate(m.replace('FluSight-', ''), (R.loc[m, 0], R.loc[m, 'final']), fontsize=8)
    lo, hi = np.nanmin(R[[0, 'final']].values) * .97, min(1.3, np.nanmax(R[[0, 'final']].values) * 1.03)
    ax.plot([lo, hi], [lo, hi], 'k-', lw=.7); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel('rel. WIS vs truth as first reported (k=0)'); ax.set_ylabel('rel. WIS vs latest truth')
    ax.set_title(f'{key[0]}, {key[1]}', fontsize=10); ax.grid(alpha=.3)
plt.colorbar(sc, ax=axes, label='median forecast / latest truth (red = forecasts high)')
fig.suptitle('Hub models scored against first-reported vs latest truth (one dot per model; below the diagonal = revisions helped it)', fontsize=11)
fig.savefig(f'{OUT}/3-hub-rescoring-first-vs-final.png', dpi=130, bbox_inches='tight'); plt.close(fig)


# ---------- 3. 2026-27 so far: scored now vs with expected remaining revisions ----------
say('\n== 2026-27 (reference dates 10 Oct - 14 Nov 2026): current truth vs current truth x expected remaining revision ==')
say('Expected remaining revision for a week now at lag k = median over in-season state-weeks of final / value at lag k, '
    'computed per state from the named season (pooled median when the state has < 5 weeks), applied to the current value.')
F26 = read_forecasts(['2026-27'])
F26 = F26[F26.ref >= '2026-10-10']
for tgt, V, nm in [('wk inc flu hosp', A, 'log admissions'), ('wk inc flu prop ed visits', E, 'ED share')]:
    cur = V[(V.season == '2026-27') & (V.report == V[V.season == '2026-27'].report.max()) & V.location.isin(STATES)]
    cur = cur[['location', 'week', 'lag', 'value']]
    f = F26[F26.target == tgt]
    out, meds = {}, {}
    for lab, src in [('as of 18 Nov', None), ('x 2025-26 remaining revision', '2025-26'), ('x 2024-25 remaining revision', '2024-25')]:
        t = cur.copy()
        if src:
            h = V[(V.season == src) & V.location.isin(STATES) & (V.value > 0)]
            h = h.assign(f=h.final / h.value)
            if tgt == 'wk inc flu hosp':
                h = h[h.final >= 20]
            ps = h.groupby(['location', 'lag']).f.agg(['median', 'size'])
            pool = h.groupby('lag').f.median()
            t['fac'] = [ps.loc[(l, k), 'median'] if (l, k) in ps.index and ps.loc[(l, k), 'size'] >= 5 else pool.get(k, 1.0)
                        for l, k in zip(t.location, t.lag)]
            t['value'] = t.value * t.fac
            say(f'{nm}, {src} factors applied by lag (median over states): ' +
                ', '.join(f'k={k}: x{v:.3f}' for k, v in t.groupby('lag').fac.median().items()))
        t = t.rename(columns={'value': 'y'})[['location', 'week', 'y']]
        t.to_csv(f"{OUT}/truth-{'adm' if tgt == 'wk inc flu hosp' else 'ed'}-{src or 'asof-latest'}.csv", index=False)
        w = wis_table(f, t)
        out[f'{lab} | all'] = pairwise(w)
        out[f'{lab} | 7-14 Nov refs'] = pairwise(w[w.ref.isin(['2026-11-07', '2026-11-14'])])
        mm = f[f.q == .5].merge(t, left_on=['location', 'target_end_date'], right_on=['location', 'week'])
        meds[lab] = mm.groupby('model').apply(lambda g: g.value.sum() / g.y.sum())
    R = pd.DataFrame(out)
    for c in list(R.columns):
        R[c.replace('|', 'rank |')] = R[c].rank().astype('Int64')
    keep = ['ACCIDDA-Chromantis', 'FluSight-ensemble', 'FluSight-baseline', 'NU-EMBERS', 'UMass-flusion', 'Gatech-ensemble_prob',
            'LUcompUncertLab-puca', 'CMU-TimeSeries', 'Google_SAI-FluBoostQR', 'ACCIDDA-insightcast']
    say(f'\n-- {nm}: {len(R)} models (covering >= half the baseline\'s tasks). Relative WIS (rank):')
    show = R.loc[[m for m in keep if m in R.index]]
    for per in ['all', '7-14 Nov refs']:
        cols = [c for c in R.columns if c.endswith(f'| {per}') and 'rank' not in c]
        say(f'   reference dates: {per}')
        say(pd.DataFrame({c.split(' |')[0]: [f'{v:.3f} ({int(r)}/{R[c].notna().sum()})' for v, r in zip(show[c], show[c.replace("|", "rank |")])]
                          for c in cols}, index=show.index).to_string())
    say('   median forecast / truth (all observed tasks): ' + '; '.join(
        f'{lab}: ours {meds[lab].get("ACCIDDA-Chromantis", np.nan):.3f}, ensemble {meds[lab].get("FluSight-ensemble", np.nan):.3f}'
        for lab in meds))
log.close()
