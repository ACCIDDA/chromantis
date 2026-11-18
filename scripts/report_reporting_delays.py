"""Reporting delays of flu admissions and ED share in 2026-27 against 2023-24, 2024-25 and 2025-26, matched on incidence.

For every weekly report (Wednesday release), the newest week (first report, lag 0) and the second-newest week
(second report, lag 1) are followed in later reports: revision factor = value k weeks later / value at that report,
for k = 1, 2, 4 and "about final" (first report 10-16 weeks later).

Sources (all local):
- NHSN flu admissions by state, as of each report: FluSight hub `target-data/time-series.csv`. In 2023-24 and
  2024-25 the hub labels each report with the Saturday ending its newest week; the data are those released the
  following Wednesday (checked: state values equal Delphi's Wednesday archive), so report date = label + 4 days.
- Hospitals reporting (Delphi NHSN archive, `hosprep_confirmed_admissions_flu_ew`, from 19 Nov 2024): coverage =
  hospitals reporting the week at that report / median hospitals reporting weeks 3-5 earlier in the same report.
- NSSP flu ED share: Delphi NSSP archive (state and nation, reports from April 2024 to 29 Sep 2026; values as known
  on each Wednesday equal the hub's) and the hub's `wk inc flu prop ed visits` (from 17 Dec 2025, covers 2026-27).
- Populations: hub `auxiliary-data/locations.csv`.

Usage: .venv/bin/python scripts/report_reporting_delays.py [out_dir]
"""
import glob, sys, warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else 'docs/experiments/reporting-delays-2026-27'
HUB = 'production/hubs/FluSight-forecast-hub'
NHSN = sorted(glob.glob('data/raw/delphi_nhsn/snapshots/*/'))[-1]
NSSP = sorted(glob.glob('data/raw/delphi_nssp/snapshots/*/'))[-1]
STEPS = {'1 week': 1, '2 weeks': 2, '4 weeks': 4, 'final': 10}
SEASONS = ['2023-24', '2024-25', '2025-26', '2026-27']
COL = {'2023-24': '#b9b8b0', '2024-25': '#2a78d6', '2025-26': '#7a7a74', '2026-27': '#1baf7a'}
BINS = [0, 1, 2, 4, 8, np.inf]; BIN_LAB = ['<1', '1-2', '2-4', '4-8', '8+']
pd.set_option('display.width', 250)

loc = pd.read_csv(f'{HUB}/auxiliary-data/locations.csv', dtype={'location': str})
STATES = [l for l in loc.location if l not in ('US', '72')]  # 50 states + DC
POP = loc.set_index('location').population
POP_US = POP[STATES].sum()
AB = dict(zip(loc.abbreviation.str.lower(), loc.location))


def season(week):
    w = pd.DatetimeIndex(pd.to_datetime(week))
    y = np.where(w.month >= 8, w.year, w.year - 1)
    return pd.Series([f'{a}-{str(a + 1)[2:]}' for a in y], index=getattr(week, 'index', None))


def in_season(week):
    m = pd.DatetimeIndex(pd.to_datetime(week)).month
    return (m >= 10) | (m <= 5)


# ---------- as-of tables: value[(report, location, week)] ----------
ts = pd.read_csv(f'{HUB}/target-data/time-series.csv', dtype={'location': str})
ts = ts.drop_duplicates(['target', 'as_of', 'location', 'target_end_date'], keep='last')  # 27 May 2026 is stored twice
adm = ts[(ts.target == 'wk inc flu hosp') & ts.location.isin(STATES)].copy()
ao = pd.to_datetime(adm.as_of)
adm['report'] = np.where(ao.dt.dayofweek == 5, ao + pd.Timedelta(days=4), ao)
adm['report'] = pd.to_datetime(adm.report).dt.strftime('%Y-%m-%d')
adm = adm.rename(columns={'target_end_date': 'week', 'observation': 'value'})[['report', 'location', 'week', 'value']]


def delphi(path, scale=1.0):
    d = pd.read_csv(path)
    d['rday'] = pd.to_datetime(d.report_time).dt.tz_convert('America/New_York').dt.date.astype(str)
    d['location'] = d.geo_value.map(AB).fillna(d.geo_value.str.upper())
    d['value'] = d.value * scale
    return d[['rday', 'location', 'reference_time', 'value']].rename(columns={'reference_time': 'week'})


def asof_by_wednesday(d, wednesdays):
    """Value known on each Wednesday (archive stores changes only, so carry forward)."""
    out = []
    d = d.sort_values('rday')
    for w in wednesdays:
        x = d[d.rday <= w].groupby(['location', 'week']).value.last().reset_index()
        out.append(x.assign(report=w))
    return pd.concat(out)


def slot_reports(d):
    """One report per week: Wednesday if there is one, else Thursday, else Tuesday (holiday weeks)."""
    r = pd.Series(sorted(d.rday.unique())); dt = pd.to_datetime(r)
    r = r[dt.dt.dayofweek.isin([1, 2, 3])]; dt = pd.to_datetime(r)
    pref = dt.dt.dayofweek.map({2: 0, 3: 1, 1: 2})
    wk = (dt - pd.to_timedelta((dt.dt.dayofweek - 2) % 7, 'D')).dt.strftime('%Y-%m-%d')  # that week's Wednesday
    s = pd.DataFrame(dict(rday=r.values, wed=wk.values, pref=pref.values)).sort_values('pref').drop_duplicates('wed')
    return dict(zip(s.wed, s.rday))


# hospitals reporting, value at each weekly slot report, labelled by that week's Wednesday
hos = delphi(f'{NHSN}signal=hosprep_confirmed_admissions_flu_ew/geo_type=state/archive.csv.gz')
dadm = delphi(f'{NHSN}signal=confirmed_admissions_flu_ew/geo_type=state/archive.csv.gz')
slots = slot_reports(dadm)
hos = pd.concat([asof_by_wednesday(hos, [r]).assign(report=w) for w, r in slots.items()])
dadm = pd.concat([asof_by_wednesday(dadm, [r]).assign(report=w) for w, r in slots.items()])
hos = hos[hos.location.isin(STATES)]
# check: hub admissions equal Delphi's slot report for the same Wednesday
chk = adm.merge(dadm, on=['report', 'location', 'week'], suffixes=('', '_d'))
chk = chk[chk.report >= '2024-12-01']
print(f'hub vs Delphi admissions, same report: {(chk.value == chk.value_d).mean():.3%} of {len(chk)} state-week values equal')

# ED share (percent): Delphi NSSP up to its last report, hub where it exists (from 17 Dec 2025)
ned = pd.concat([delphi(f'{NSSP}signal=pct_ed_visits_influenza/geo_type={g}/archive.csv.gz') for g in ('state', 'nation')])
ned = ned[ned.location.isin(STATES + ['US'])]
# NSSP released on Thursdays in 2024-25 and Tuesdays from mid-2025: keep each release that first carries a new week
# ending at most 6 days earlier, labelled with the Wednesday after that week (the hub's report day)
nus = ned[ned.location == 'US'].sort_values('rday')
newest = {r: nus[nus.rday <= r].week.max() for r in nus.rday.unique()}
keep, seen = {}, set()
for r, w in newest.items():
    if w not in seen and (pd.Timestamp(r) - pd.Timestamp(w)).days <= 6:
        keep[(pd.Timestamp(w) + pd.Timedelta(days=4)).strftime('%Y-%m-%d')] = r
    seen.add(w)
ed = pd.concat([asof_by_wednesday(ned, [r]).assign(report=w) for w, r in keep.items()])
hed = ts[(ts.target == 'wk inc flu prop ed visits') & ts.location.isin(STATES + ['US'])]
hed = hed.assign(value=hed.observation * 100).rename(columns={'as_of': 'report', 'target_end_date': 'week'})[['report', 'location', 'week', 'value']]
chk = ed.merge(hed, on=['report', 'location', 'week'], suffixes=('', '_h'))
dif = np.abs(chk.value - chk.value_h)
print(f'Delphi NSSP vs hub ED share, same Wednesday: {(dif < 1e-6).mean():.3%} of {len(chk)} values equal; '
      f'newest 2 weeks: {(dif[pd.to_datetime(chk.report) - pd.to_datetime(chk.week) <= pd.Timedelta(days=11)] < 1e-6).mean():.3%} equal')
ed = pd.concat([ed[~ed.report.isin(hed.report.unique())], hed])


# ---------- revision factors ----------
def revisions(tab, national):
    """Rows: report, location, lag, week, value at report, factor after each step. national: 'sum' or a location."""
    tab = tab.copy()
    if national == 'sum':
        n = tab.groupby(['report', 'week']).agg(value=('value', 'sum'), n=('value', 'size')).reset_index()
        tab = pd.concat([tab, n[n.n == len(STATES)].drop(columns='n').assign(location='US')])
    v = tab.set_index(['report', 'location', 'week']).value
    reports = sorted(tab.report.unique()); rset = set(reports)
    rows = []
    for r in reports:
        x = tab[tab.report == r]
        newest = x.week.max()
        if (pd.Timestamp(r) - pd.Timestamp(newest)).days != 4:  # newest week must end the Saturday before
            continue
        later = {k: (pd.Timestamp(r) + pd.Timedelta(weeks=k)).strftime('%Y-%m-%d') for k in range(1, 17)}
        fin = next((later[k] for k in range(10, 17) if later[k] in rset), None)
        for lag in (0, 1):
            wk = (pd.Timestamp(newest) - pd.Timedelta(weeks=lag)).strftime('%Y-%m-%d')
            y = x[x.week == wk].set_index('location').value
            for l, val in y.items():
                row = dict(report=r, location=l, lag=lag, week=wk, value=val)
                for name, k in STEPS.items():
                    rr = fin if name == 'final' else later[k]
                    row[name] = v.get((rr, l, wk), np.nan) / val if rr in rset and val > 0 else np.nan
                rows.append(row)
    d = pd.DataFrame(rows)
    d['season'] = season(d.week).values
    return d[in_season(d.week) & d.season.isin(SEASONS)]


def phase(d, curve_tab):
    """Rising = week on or before the location's season peak in the latest data of that season; falling = after."""
    c = curve_tab.copy(); c['season'] = season(c.week).values
    c = c[in_season(c.week) & c.season.isin(SEASONS)]
    last = c.groupby('season').report.max()  # latest report inside each season's own run of reports
    c = c[c.report.isin(last.values) & (c.season.map(last) == c.report)].dropna(subset=['value']).reset_index(drop=True)
    peak = c.loc[c.groupby(['season', 'location']).value.idxmax(), ['season', 'location', 'week']].rename(columns={'week': 'peak'})
    d = d.merge(peak, on=['season', 'location'], how='left')
    d['phase'] = np.where(d.week <= d.peak, 'rising', 'falling')
    return d


# admissions: latest report within each season = its own latest report before the next season's (Aug) start
adm_curve = adm[pd.to_datetime(adm.report) < pd.to_datetime(season(adm.week).str[:4].astype(int).astype(str) + '-08-15') + pd.DateOffset(years=1)]
nat = adm_curve.groupby(['report', 'week']).value.sum().reset_index().assign(location='US')
A = phase(revisions(adm, 'sum'), pd.concat([adm_curve, nat]))
A['pop'] = A.location.map(lambda l: POP_US if l == 'US' else POP[l])
A['per100k'] = A.value / A['pop'] * 1e5
A['bin'] = pd.cut(A.per100k, BINS, labels=BIN_LAB, right=False)

ed_curve = ed[pd.to_datetime(ed.report) < pd.to_datetime(season(ed.week).str[:4].astype(int).astype(str) + '-08-15') + pd.DateOffset(years=1)]
E = phase(revisions(ed, None), ed_curve)
E['bin'] = pd.cut(E.value, [0, 1, 2, 4, 8, np.inf], labels=['<1%', '1-2%', '2-4%', '4-8%', '8%+'], right=False)

# coverage at the report (national = sum over states of hospitals reporting / sum of reference counts)
H = hos.set_index(['report', 'location', 'week']).value
cov = []
for r in sorted(A.report.unique()):
    if r not in set(hos.report):
        continue
    x = A[(A.report == r) & (A.location != 'US')]
    for row in x.itertuples():
        newest = pd.Timestamp(row.week) + pd.Timedelta(weeks=row.lag)
        ref = np.nanmedian([H.get((r, row.location, (newest - pd.Timedelta(weeks=k)).strftime('%Y-%m-%d')), np.nan) for k in (3, 4, 5)])
        cov.append(dict(report=r, location=row.location, lag=row.lag, hosp=H.get((r, row.location, row.week), np.nan), ref=ref))
cov = pd.DataFrame(cov)
cn = cov.dropna().groupby(['report', 'lag']).agg(hosp=('hosp', 'sum'), ref=('ref', 'sum'), n=('ref', 'size')).reset_index()
cn = cn[cn.n == len(STATES)].assign(location='US').drop(columns='n')
cov = pd.concat([cov, cn])
A = A.merge(cov, on=['report', 'location', 'lag'], how='left')
A['coverage'] = A.hosp / A.ref

# ---------- known checks ----------
x = A[(A.location == 'US') & (A.lag == 0) & (A.week == '2026-10-24')]
print('\nCheck: 2026-27 week ending 24 Oct, sum over states, factor after 2 weeks:', x['2 weeks'].round(4).tolist())
x = A[(A.location == 'US') & (A.lag == 0) & (A.season == '2025-26') & A.report.between('2025-11-01', '2026-03-31')]
print('Check: 2025-26 newest week, Nov-Mar reports, median final factor:', round(x.final.median(), 4), f'({x.final.notna().sum()} reports)')


# ---------- tables ----------
def q(s):
    s = s.dropna()
    return f'×{s.median():.3f} [{s.quantile(.1):.2f}–{s.quantile(.9):.2f}] (n={len(s)})' if len(s) else ''


def table(d, lag, by, min_n=1):
    rows = []
    for key, w in d[d.lag == lag].groupby(by, observed=True):
        if len(w) < min_n:
            continue
        rows.append(dict(zip(by, key if isinstance(key, tuple) else (key,))) | {k: q(w[k]) for k in STEPS})
    return pd.DataFrame(rows)


def md(df):
    cols = list(df.columns)
    return '\n'.join(['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)] +
                     ['| ' + ' | '.join(str(v) for v in r) + ' |' for r in df.itertuples(index=False)])


us = A[A.location == 'US']
print('\n## National admissions (sum of 50 states + DC), by season, phase and national admissions per 100k at the report')
for lag in (0, 1):
    print(f'\n### lag {lag}\n' + md(table(us, lag, ['phase', 'bin', 'season'])))
st = A[(A.location != 'US') & (A.value >= 10)]
print('\n## State-weeks with >=10 admissions at the report, by state admissions per 100k at the report')
for lag in (0, 1):
    print(f'\n### lag {lag}\n' + md(table(st, lag, ['phase', 'bin', 'season'], min_n=10)))
print('\n## 2026-27 national, each report')
print(md(us[us.season == '2026-27'][['report', 'week', 'lag', 'per100k', 'coverage'] + list(STEPS)].round(3)))

print('\n## National, rising phase, under 4 per 100k at the report: every report, all seasons')
m = us[(us.phase == 'rising') & (us.per100k < 4)].sort_values(['lag', 'report'])
print(md(m[['lag', 'season', 'report', 'week', 'per100k', 'coverage'] + list(STEPS)].round(3)))
print(md(m.groupby(['lag', 'season'])[list(STEPS)].median().round(3).reset_index()))

print('\n## Coverage at the report (national: sum over states), median by season, phase, bin')
c = us.dropna(subset=['coverage'])
print(md(c.groupby(['lag', 'phase', 'bin', 'season'], observed=True).coverage.agg(['median', 'size']).round(3).reset_index()))
sc = st.dropna(subset=['coverage']).copy()
sc['cov_bin'] = pd.cut(sc.coverage, [0, .7, .8, .9, .95, 1.0, 9], labels=['<70%', '70-80%', '80-90%', '90-95%', '95-100%', '>100%'])
print('\n## State-weeks: revision by coverage at the report, season')
for lag in (0, 1):
    print(f'\n### lag {lag}\n' + md(table(sc, lag, ['cov_bin', 'season'], min_n=10)))
print('\n## State-weeks: share of state-weeks per coverage bin, rising phase, state 1-4 per 100k')
w = sc[(sc.phase == 'rising') & sc.bin.isin(['1-2', '2-4'])]
print(md((pd.crosstab([w.lag, w.season], w.cov_bin, normalize='index') * 100).round(0).reset_index()))
eu = E[E.location == 'US']
print('\n## ED share, national, by season, phase, national ED share at the report')
for lag in (0, 1):
    print(f'\n### lag {lag}\n' + md(table(eu, lag, ['phase', 'bin', 'season'])))
es = E[E.location != 'US']
print('\n## ED share, states, by state ED share at the report')
for lag in (0, 1):
    print(f'\n### lag {lag}\n' + md(table(es, lag, ['phase', 'bin', 'season'], min_n=10)))
print('\n## 2026-27 ED national, each report')
print(md(eu[eu.season == '2026-27'][['report', 'week', 'lag', 'value'] + list(STEPS)].round(3)))


# ---------- figures ----------
def style(a):
    for sp in ('top', 'right'):
        a.spines[sp].set_visible(False)
    a.grid(color='#ecebe6', lw=.8); a.axhline(1, color='#9a9992', lw=1)


def scatter(d, xcol, xlab, fname, title, logx=True):
    fig, ax = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True)
    for i, lag in enumerate((0, 1)):
        for j, k in enumerate(('2 weeks', 'final')):
            a = ax[i, j]; style(a)
            for s in SEASONS:
                for ph, mk in (('rising', 'o'), ('falling', 'o')):
                    w = d[(d.lag == lag) & (d.season == s) & (d.phase == ph)].dropna(subset=[k])
                    if not len(w):
                        continue
                    a.scatter(w[xcol], w[k], s=42 if s == '2026-27' else 26, marker=mk,
                              facecolor=COL[s] if ph == 'rising' else 'none', edgecolor=COL[s], lw=1.3,
                              label=f'{s} {ph} ({len(w)})', zorder=3 if s == '2026-27' else 2)
            if logx:
                a.set_xscale('log')
            a.set_title(f"{'Newest week (first report)' if lag == 0 else 'Second-newest week (second report)'}: "
                        f"{'2 weeks later' if k == '2 weeks' else 'about final (10-16 weeks later)'}", fontsize=10, loc='left')
            if j == 0:
                a.set_ylabel('later value / value at the report')
            if i == 1:
                a.set_xlabel(xlab)
            a.legend(frameon=False, fontsize=7.5, ncol=2, loc='upper right')
    fig.suptitle(title, x=.01, ha='left', fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .96))
    fig.savefig(f'{OUT}/{fname}', dpi=110); plt.close(fig)


scatter(us, 'per100k', 'National admissions per 100k at the report (log scale)', 'national-admissions.png',
        'Flu admissions, sum of 50 states + DC: revision of each Wednesday report against incidence at that report\n'
        'Filled = before the season\'s national peak, hollow = after; 2026-27 has no final values yet')
scatter(eu, 'value', 'National flu ED share at the report, % (log scale)', 'national-ed-share.png',
        'Flu ED share, national (NSSP): revision of each Wednesday report against the ED share at that report\n'
        'Filled = before the season\'s national peak, hollow = after; 2026-27 has no final values yet')

# state-weeks: median by per-100k bin, rising phase, one panel per step
fig, ax = plt.subplots(2, 3, figsize=(13, 7.5), sharey='row')
for i, lag in enumerate((0, 1)):
    for j, k in enumerate(('1 week', '2 weeks', 'final')):
        a = ax[i, j]; style(a)
        for si, s in enumerate(SEASONS):
            w = st[(st.lag == lag) & (st.season == s) & (st.phase == 'rising')].dropna(subset=[k])
            g = w.groupby('bin', observed=False)[k]
            med, lo, hi, n = g.median(), g.quantile(.25), g.quantile(.75), g.size()
            xs = np.arange(len(BIN_LAB)) + (si - 1.5) * .17
            ok = (n >= 10).values
            a.errorbar(xs[ok], med[ok], yerr=[(med - lo)[ok], (hi - med)[ok]], fmt='o', color=COL[s], ms=6, lw=1.2,
                       label=s if i == 0 and j == 0 else None)
        a.set_xticks(range(len(BIN_LAB)), BIN_LAB)
        a.set_title(f"{'Newest week' if lag == 0 else 'Second-newest week'}: {'about final' if k == 'final' else k + ' later'}", fontsize=10, loc='left')
        if i == 1:
            a.set_xlabel('State admissions per 100k at the report')
        if j == 0:
            a.set_ylabel('later value / value at the report')
fig.legend(frameon=False, loc='upper right', ncol=4, fontsize=9)
fig.suptitle('Flu admissions by state, weeks before each state\'s peak, state-weeks with at least 10 admissions at the report\n'
             'Dot = median over state-weeks, bar = middle half (25th-75th percentile); bins with fewer than 10 state-weeks hidden',
             x=.01, ha='left', fontsize=11)
fig.tight_layout(rect=(0, 0, 1, .92)); fig.savefig(f'{OUT}/state-admissions-by-incidence.png', dpi=110); plt.close(fig)

# coverage
fig, ax = plt.subplots(1, 3, figsize=(14, 4.6))
a = ax[0]; style(a); a.axhline(1, color='none')
for s in SEASONS[1:]:
    w = us[(us.lag == 0) & (us.season == s)].dropna(subset=['coverage']).sort_values('week')
    a.plot(pd.to_datetime(w.week).apply(lambda t: t.replace(year=2000 + (t.month < 8))), w.coverage, 'o-', color=COL[s], ms=4, label=s)
a.set_ylabel('hospitals reporting newest week /\nusual number (weeks 3-5 earlier)'); a.legend(frameon=False, fontsize=8)
a.set_title('National coverage at first report, by week of season', fontsize=10, loc='left')
import matplotlib.dates as mdates; a.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
for a, k in zip(ax[1:], ('2 weeks', 'final')):
    style(a)
    for s in SEASONS[1:]:
        w = sc[(sc.lag == 0) & (sc.season == s)].dropna(subset=[k])
        g = w.groupby('cov_bin', observed=False)[k]; n = g.size()
        xs = np.arange(6) + (SEASONS.index(s) - 2) * .2; ok = (n >= 10).values
        med, lo, hi = g.median(), g.quantile(.25), g.quantile(.75)
        a.errorbar(xs[ok], med[ok], yerr=[(med - lo)[ok], (hi - med)[ok]], fmt='o', color=COL[s], ms=6, label=s)
    a.set_xticks(range(6), ['<70%', '70-80', '80-90', '90-95', '95-100', '>100%'], fontsize=8)
    a.set_xlabel('State coverage at first report'); a.legend(frameon=False, fontsize=8)
    a.set_title(f"State newest weeks (>=10 admissions): {'about final' if k == 'final' else k + ' later'}", fontsize=10, loc='left')
ax[1].set_ylabel('later value / value at first report')
fig.tight_layout(); fig.savefig(f'{OUT}/coverage.png', dpi=110); plt.close(fig)

# small summary table for the page folder
summ = pd.concat([table(us, lag, ['phase', 'bin', 'season']).assign(series='admissions national', lag=lag) for lag in (0, 1)] +
                 [table(st, lag, ['phase', 'bin', 'season'], 10).assign(series='admissions state-weeks', lag=lag) for lag in (0, 1)] +
                 [table(eu, lag, ['phase', 'bin', 'season']).assign(series='ED share national', lag=lag) for lag in (0, 1)])
summ.to_csv(f'{OUT}/summary.csv', index=False)
