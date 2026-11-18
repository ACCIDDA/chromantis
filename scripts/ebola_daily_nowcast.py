"""Daily-delay nowcast of BDBV weekly confirmed cases, and a backtest against the release-pair nowcast.

The release-pair nowcast (`ebola_nowcast.py`) learns how much each onset week grows between two weekly
releases, from 4-5 release pairs. This one estimates the onset-to-report delay in days from every case
with an observed onset date (`auxiliary-data/weekly-reporting-delays-by-province*.csv`, one row per
case: onset week, province, days from onset to report), as that file stood at the release.

Delay. Onset day d, delay delta, data cutoff C (the last report date in the release). A case is in the
release only if d + delta <= C, so recent onset days show only their short delays. The delay file gives
the onset week, not the day, and the daily file (`daily-confirmed-case.csv`) gives the onset-day counts
c_d. The joint table x[d, delta] is filled by expectation-maximization under x ~ N_d * p_delta on the
support delta <= C - d, kept consistent with both margins (day counts and week x delay histogram); then
p_delta = sum_d x[d, delta] / sum_{d: C - d >= delta} N_d and N_d = c_d / F(C - d). Only onset weeks
ending in the last WINDOW weeks before C are used, so the delay can drift. Delays above DMAX days count
as DMAX, the few negative ones as 0.

Entry lag. A case reported on day t is not always in the release cut at t: with the delay alone, the
national count of the newest onset week at the next release came out 1.10-1.75 times the prediction
(releases 17 Oct to 8 Nov), the week before 1.04-1.37 times. So the completeness at age a is
F(a - L), with L (days) fitted per release on the earlier release pairs: least squares on the log ratio
of realized to predicted next-release counts of the two newest weeks (cases with an observed onset).

Week completeness. F_w is the mean of F(C - d - L) over the week's days up to C: cases are taken as
spread evenly over the week. Dividing each day by its own completeness instead (c_d / F, the obvious
use of daily data) was worse in the backtest (national WIS 34 against 26 before the entry lag), because
the newest days carry a handful of cases and a near-zero F. The national cases still to come for week
w are c_w (1 - F_w) / F_w.

Zones. The national cases still to come are shared across health zones in proportion to the
release-pair model's base (alpha * reported + (1 - alpha) * level + eps, its fitted alpha, eps and
dispersion phi), drawn negative binomial. Uncertainty in the delay: each draw shifts the entry lag by
TAU * z days and stretches the delay by exp(SIGMA * z'), shared by all zones and weeks. Imputed-onset
cases are handled as in `ebola_nowcast.py`.

    .venv/bin/python scripts/ebola_daily_nowcast.py     # backtest on past releases, scored on the latest
"""
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from ebola_nowcast import HUB, Nowcast, lag

DMAX = 42        # delays above this many days count as DMAX (2% are above 28 days)
WINDOW = 8       # onset weeks ending in the last WINDOW weeks before the cutoff estimate the delay
SIGMA = 0.15     # log-sd of the shared delay stretch per draw
TAU = 1.         # sd in days of the shared entry-lag shift per draw
FIRST_DELAYS = '2026-10-17'   # first release with an archived delay file
Q = np.array([.01, .025] + list(np.arange(.05, .951, .05).round(2)) + [.975, .99])
GRID = np.arange(DMAX + 1)


@lru_cache
def table(name, hub=HUB):
    return pd.read_csv(Path(hub) / 'auxiliary-data' / name)


def cutoff(release, hub=HUB):
    """Last report date in a release."""
    m = table('daily-missing-symptom-by-report-date.csv', hub)
    return pd.Timestamp(m[m.as_of == release].report_date.max())


def delays(release, hub=HUB):
    """One row per case with an observed onset: onset week end, delay in days, as the file stood at `release`."""
    f = Path(hub) / f'auxiliary-data/archived-delay-data/weekly-reporting-delays-by-province-{release}.csv'
    d = pd.read_csv(f) if f.exists() else table('weekly-reporting-delays-by-province.csv', hub)
    if d.as_of.iloc[0] != release:
        raise ValueError(f'No delay file for release {release}')
    return pd.DataFrame(dict(week=pd.to_datetime(d.week_ending), delay=d.days_sym_to_report.clip(0, DMAX)))


def daily(release, hub=HUB):
    """National counts by onset day at `release`, observed onsets only."""
    t = table('daily-confirmed-case.csv', hub)
    t = t[(t.location == 'CD') & (t.as_of == release) & ~t.imputed]
    return t.groupby(pd.to_datetime(t.target_end_date)).observation.sum()


def week_end(day):
    return day + pd.Timedelta(days=(5 - day.weekday()) % 7)


@lru_cache
def fit_delay(release, hub=HUB, window=WINDOW, iters=200):
    """Delay CDF F[0..DMAX] corrected for right truncation, and the release's cutoff."""
    C = cutoff(release, hub)
    rows = delays(release, hub)
    first_week = week_end(C) - pd.Timedelta(weeks=window - 1)
    rows = rows[rows.week >= first_week]
    c = daily(release, hub).reindex(pd.date_range(first_week - pd.Timedelta(days=6), C), fill_value=0)
    age = np.array([(C - d).days for d in c.index])
    wk = np.array([week_end(d) for d in c.index])
    weeks = sorted(set(wk))
    h = rows.groupby(['week', 'delay']).size().unstack(fill_value=0).reindex(index=weeks, columns=GRID, fill_value=0)
    support = GRID[None, :] <= age[:, None]          # [day, delay]
    p = np.full(DMAX + 1, 1 / (DMAX + 1))
    N = c.values.astype(float) + .5
    for _ in range(iters):
        x = np.zeros((len(c), DMAX + 1))
        for w in weeks:
            i = wk == w
            m = N[i, None] * p[None, :] * support[i]
            for _ in range(3):   # rows to the day counts, columns to the week's delay histogram
                m *= (c.values[i] / np.maximum(m.sum(1), 1e-12))[:, None]
                m *= (h.loc[w].values / np.maximum(m.sum(0), 1e-12))[None, :]
            x[i] = m
        p = x.sum(0) / np.maximum((N[:, None] * support).sum(0), 1e-12)
        p /= p.sum()
        N = np.maximum(c.values / np.cumsum(p)[np.minimum(age, DMAX)], 1e-3)
    return np.cumsum(p), C


def completeness(F, C, weeks, shift=0., stretch=1.):
    """F_w per onset week at cutoff C: mean of F((C - d - shift) / stretch) over the week's days up to C."""
    out = []
    for w in weeks:
        w = pd.Timestamp(w)
        a = np.array([(C - d).days for d in pd.date_range(w - pd.Timedelta(days=6), min(w, C))], float)
        out.append(np.interp((a - shift) / stretch, GRID, F, left=0, right=1.).mean())
    return np.maximum(np.array(out), 1e-3)


def releases_with_delays(until, hub=HUB):
    t = table('daily-confirmed-case.csv', hub)
    return [r for r in sorted(t.as_of.unique()) if FIRST_DELAYS <= r <= until]


@lru_cache
def entry_lag(release, hub=HUB, window=WINDOW):
    """L in days from the release pairs up to `release`: next-release counts of the two newest weeks."""
    rs = releases_with_delays(release, hub)
    pairs = list(zip(rs, rs[1:]))
    if not pairs:
        return 1.
    cands, loss = np.arange(0, 3.01, .25), []
    for L in cands:
        e = []
        for r1, r2 in pairs:
            F, C1 = fit_delay(r1, hub, window)
            C2 = cutoff(r2, hub)
            c1, c2 = daily(r1, hub), daily(r2, hub)
            for k in range(2):
                w = week_end(C1) - pd.Timedelta(weeks=k)
                days = pd.date_range(w - pd.Timedelta(days=6), min(w, C1))
                ratio = completeness(F, C2, [w], L)[0] / completeness(F, C1, [w], L)[0]
                e.append(np.log(c2.reindex(days, fill_value=0).sum() / (c1.reindex(days, fill_value=0).sum() * ratio)))
        loss.append(np.sum(np.square(e)))
    return float(cands[int(np.argmin(loss))])


class DailyNowcast(Nowcast):
    """Release-pair zone model (alpha, eps, phi) with the national cases still to come from daily delays."""

    def __init__(self, zones, hub=HUB, until=None, window=WINDOW, sigma=SIGMA, tau=TAU, lag_days=None):
        super().__init__(zones, hub, until)
        self.hub, self.window, self.sig, self.tau, self.lag_days = hub, window, sigma, tau, lag_days

    def sample(self, release, weeks, draws, seed=1000):
        F, C = fit_delay(release, self.hub, self.window)
        L = entry_lag(release, self.hub, self.window) if self.lag_days is None else self.lag_days
        R = self.rel[release].reindex(columns=self.zones, fill_value=0)
        all_weeks = list(R.index)
        imp = self.imp[release].reindex(index=all_weeks, columns=self.zones, fill_value=0)
        old = [w for w in all_weeks if 5 <= lag(release, w) <= 12]
        m = imp.loc[old].values.sum() / R.loc[old].values.sum()
        a, e, phi = self.params['alpha'], self.params['eps'], self.params['phi']
        out = np.empty((draws, len(weeks), len(self.zones)))
        for d in range(draws):
            rng = np.random.default_rng(seed + d)
            Fw = completeness(F, C, weeks, max(0., L + self.tau * rng.standard_normal()), np.exp(self.sig * rng.standard_normal()))
            for j, w in enumerate(weeks):
                i = all_weeks.index(w)
                c = R.loc[w].values.astype(float)
                level = R.iloc[max(0, i - 3):i].mean(0).values if i else 0 * c
                b = a * c + (1 - a) * level + e
                mu = np.maximum(c.sum() * (1 - Fw[j]) / Fw[j] * b / b.sum(), 1e-9)
                added = rng.negative_binomial(phi, phi / (phi + mu))
                out[d, j] = c + added + imp.loc[w].values + rng.poisson(m * added)
        return out


def wis(samples, y):
    q = np.quantile(samples, Q, axis=0)
    return 2 * np.mean(np.maximum(Q[:, None] * (y - q), (Q[:, None] - 1) * (y - q)), 0)


def backtest(origins=('2026-10-24', '2026-11-01', '2026-11-08'), draws=200, hub=HUB):
    """Each origin: the five newest onset weeks at that release, scored on the latest release's counts."""
    t = pd.read_csv(Path(hub) / 'target-data/time-series.csv')
    latest = t.as_of.max()
    truth = t[t.as_of == latest].pivot(index='target_end_date', columns='location', values='observation')
    zones = sorted(t[(t.location.str.count('-') == 2) & (t.observation > 0)].location.unique())
    models = {'release pairs (current)': lambda r: Nowcast(zones, hub, until=r),
              'daily delay, no entry lag': lambda r: DailyNowcast(zones, hub, until=r, lag_days=0., tau=0.),
              'daily delay, fitted entry lag': lambda r: DailyNowcast(zones, hub, until=r),
              'daily delay, fitted entry lag, 4-week window': lambda r: DailyNowcast(zones, hub, until=r, window=4)}
    rows = []
    for r in origins:
        weeks = [w for w in sorted(truth.index) if 0 <= lag(r, w) <= 4 and pd.Timestamp(w) <= pd.Timestamp(r)]
        print(r, 'entry lag', entry_lag(r, hub), 'days', flush=True)
        for name, make in models.items():
            s = make(r).sample(r, weeks, draws)
            nat = s.sum(2)
            y = truth.loc[weeks, 'CD'].values
            z = wis(s.reshape(draws, -1), truth.loc[weeks].reindex(columns=zones).fillna(0).values.ravel()).reshape(len(weeks), -1)
            for j, w in enumerate(weeks):
                q5, q50, q95 = np.quantile(nat[:, j], [.05, .5, .95])
                rows.append(dict(origin=r, week=w, lag=lag(r, w), model=name, truth=y[j], median=q50, q05=q5, q95=q95,
                                 national_wis=wis(nat[:, [j]], y[j:j + 1])[0], zone_wis=z[j].mean()))
    return pd.DataFrame(rows), latest


def summarize(d):
    inside = (d.truth >= d.q05) & (d.truth <= d.q95)
    return d.assign(inside=inside).groupby('model').agg(national_wis=('national_wis', 'mean'), zone_wis=('zone_wis', 'mean'),
                                                        cover90=('inside', 'mean'), n=('truth', 'size')).round(3)


if __name__ == '__main__':
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'data/ebola/daily-nowcast-backtest')
    out.mkdir(parents=True, exist_ok=True)
    d, latest = backtest()
    d.to_csv(out / f'backtest-{latest}.csv', index=False)
    print(f'\nall 15 origin-weeks, scored on {latest} counts: mean WIS (lower is better), 90% interval coverage')
    print(summarize(d).to_string())
    print('\nwithout the newest week of the 8 Nov origin (still incomplete at the latest release)')
    print(summarize(d[~((d.origin == '2026-11-08') & (d.lag == 0))]).to_string())
    print('\nby lag at the origin, national WIS')
    print(d.pivot_table(index='lag', columns='model', values='national_wis').round(1).to_string())
    print(d.pivot_table(index=['origin', 'week', 'truth'], columns='model', values='median').round(0).to_string())
