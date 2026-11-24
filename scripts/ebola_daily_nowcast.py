"""Daily-delay nowcast of BDBV weekly confirmed cases, and a backtest of its formulations against the
release-pair nowcast.

The release-pair nowcast (`ebola_nowcast.py`) learns how much each onset week grows between two weekly
releases, from 4-6 release pairs. This one estimates the onset-to-report delay in days from every case
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
F(a - L), with L (days) fitted on earlier release pairs: least squares on the log ratio of realized to
predicted next-release counts of the two newest weeks (cases with an observed onset). `lag_pairs='all'`
uses every pair since 17 Oct, 'last' only the latest one.

Formulations (`DailyNowcast` options):
- days='uniform': week completeness F_w is the mean of F(C - d - L) over the week's days up to C (cases
  taken as spread evenly over the week); the cases still to come are c_w (1 - F_w) / F_w.
- days='trend': the final daily counts N_d follow a log-linear trend over the last TREND_DAYS days,
  fitted as negative binomial c_d ~ NB(exp(b0 + b1 t) F(C - d - L), k). Each day's final count is drawn
  from its gamma posterior, N_d ~ Gamma(k + c_d, k / mu_d + F_d), and its unreported part as
  Poisson(N_d (1 - F_d)): days with little reported get pulled to the trend, well-reported days keep
  their own count. Trend parameters are drawn from their Laplace approximation.
- by='province': uniform days with a delay per province (Ituri, Nord Kivu, Haut Uele; the national delay
  for provinces with fewer than MIN_ROWS delay rows in the window); by='country': one national delay.
History: dividing each day by its own completeness (c_d / F_d, the obvious use of daily data) was worse in
the first backtest (17 Nov, national WIS 34 against 26 for uniform days, both without entry lag): the
newest days carry a handful of cases and a near-zero F. 'trend' is the shrunk version of that.

Zones. The cases still to come in a province (or the country) are shared across its health zones in
proportion to the release-pair model's base (alpha * reported + (1 - alpha) * level + eps, with its
fitted alpha, eps and dispersion phi), drawn negative binomial. Uncertainty in the delay: each draw shifts
the entry lag by TAU * z days and stretches the delay by exp(SIGMA * z'), shared by all zones and weeks.
Imputed-onset cases are handled as in `ebola_nowcast.py`.

    .venv/bin/python scripts/ebola_daily_nowcast.py     # backtest on past releases, scored on the latest
"""
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln

sys.path.insert(0, str(Path(__file__).parent))
from ebola_nowcast import HUB, Nowcast, lag

DMAX = 42        # delays above this many days count as DMAX (2% are above 28 days)
WINDOW = 8       # onset weeks ending in the last WINDOW weeks before the cutoff estimate the delay
SIGMA = 0.15     # log-sd of the shared delay stretch per draw
TAU = 1.         # sd in days of the shared entry-lag shift per draw
TREND_DAYS = 35  # days of onset counts the trend formulation fits
MIN_ROWS = 300   # delay rows in the window a province needs for its own delay
FIRST_DELAYS = '2026-10-17'   # first release with an archived delay file
Q = np.array([.01, .025] + list(np.arange(.05, .951, .05).round(2)) + [.975, .99])
GRID = np.arange(DMAX + 1)


@lru_cache
def table(name, hub=HUB):
    return pd.read_csv(Path(hub) / 'auxiliary-data' / name)


@lru_cache
def province_names(hub=HUB):
    t = table('locations.csv', hub)
    return dict(zip(t[t.location_type == 'province'].location, t[t.location_type == 'province'].location_name))


def cutoff(release, hub=HUB):
    """Last report date in a release."""
    m = table('daily-missing-symptom-by-report-date.csv', hub)
    return pd.Timestamp(m[m.as_of == release].report_date.max())


@lru_cache
def delays(release, hub=HUB):
    """One row per case with an observed onset: onset week end, province name, delay in days, at `release`."""
    f = Path(hub) / f'auxiliary-data/archived-delay-data/weekly-reporting-delays-by-province-{release}.csv'
    d = pd.read_csv(f) if f.exists() else table('weekly-reporting-delays-by-province.csv', hub)
    if d.as_of.iloc[0] != release:
        raise ValueError(f'No delay file for release {release}')
    return pd.DataFrame(dict(week=pd.to_datetime(d.week_ending), province=d.location_name,
                             delay=d.days_sym_to_report.clip(0, DMAX)))


def daily(release, hub=HUB, location='CD'):
    """Counts by onset day at `release` for a location code, observed onsets only."""
    t = table('daily-confirmed-case.csv', hub)
    t = t[(t.location == location) & (t.as_of == release) & ~t.imputed]
    return t.groupby(pd.to_datetime(t.target_end_date)).observation.sum()


def week_end(day):
    return day + pd.Timedelta(days=(5 - day.weekday()) % 7)


@lru_cache
def fit_delay(release, hub=HUB, window=WINDOW, province=None, iters=200):
    """Delay CDF F[0..DMAX] corrected for right truncation, and the release's cutoff (country, or a province code)."""
    C = cutoff(release, hub)
    rows = delays(release, hub)
    if province:
        rows = rows[rows.province == province_names(hub)[province]]
    first_week = week_end(C) - pd.Timedelta(weeks=window - 1)
    rows = rows[rows.week >= first_week]
    c = daily(release, hub, province or 'CD').reindex(pd.date_range(first_week - pd.Timedelta(days=6), C), fill_value=0)
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
        p /= max(p.sum(), 1e-12)
        N = np.maximum(c.values / np.cumsum(p)[np.minimum(age, DMAX)], 1e-3)
    return np.cumsum(p), C, len(rows)


def shifted(F, a, shift=0., stretch=1.):
    return np.interp((np.asarray(a, float) - shift) / stretch, GRID, F, left=0, right=1.)


def week_days(w, C):
    w = pd.Timestamp(w)
    return pd.date_range(w - pd.Timedelta(days=6), min(w, C))


def completeness(F, C, weeks, shift=0., stretch=1.):
    """F_w per onset week at cutoff C: mean of F((C - d - shift) / stretch) over the week's days up to C."""
    return np.maximum(np.array([shifted(F, [(C - d).days for d in week_days(w, C)], shift, stretch).mean()
                                for w in weeks]), 1e-3)


def releases_with_delays(until, hub=HUB):
    t = table('daily-confirmed-case.csv', hub)
    return [r for r in sorted(t.as_of.unique()) if FIRST_DELAYS <= r <= until]


@lru_cache
def entry_lag(release, hub=HUB, window=WINDOW, pairs='all'):
    """L in days from the release pairs up to `release`: next-release counts of the two newest weeks."""
    rs = releases_with_delays(release, hub)
    pairs = list(zip(rs, rs[1:]))[-1:] if pairs == 'last' else list(zip(rs, rs[1:]))
    if not pairs:
        return 1.
    cands, loss = np.arange(0, 3.01, .25), []
    for L in cands:
        e = []
        for r1, r2 in pairs:
            F, C1, _ = fit_delay(r1, hub, window)
            C2 = cutoff(r2, hub)
            c1, c2 = daily(r1, hub), daily(r2, hub)
            for k in range(2):
                w = week_end(C1) - pd.Timedelta(weeks=k)
                days = week_days(w, C1)
                ratio = completeness(F, C2, [w], L)[0] / completeness(F, C1, [w], L)[0]
                e.append(np.log(c2.reindex(days, fill_value=0).sum() / (c1.reindex(days, fill_value=0).sum() * ratio)))
        loss.append(np.sum(np.square(e)))
    return float(cands[int(np.argmin(loss))])


def nb_loglik(y, mu, k):
    return gammaln(y + k) - gammaln(k) - gammaln(y + 1) + k * np.log(k / (k + mu)) + y * np.log(mu / (k + mu))


def fit_trend(c, F_d, t):
    """Negative-binomial log-linear trend c_d ~ NB(exp(b0 + b1 t) F_d, k): estimate and Laplace covariance."""
    def loss(x):
        return -nb_loglik(c, np.exp(x[0] + x[1] * t) * np.maximum(F_d, .01), np.exp(x[2])).sum()
    x0 = [np.log(max(c[F_d > .5].mean() if (F_d > .5).any() else c.mean(), 1.)), 0., np.log(5.)]
    r = minimize(loss, x0, method='BFGS')
    return r.x, np.atleast_2d(r.hess_inv)[:2, :2]


class DailyNowcast:
    """Release-pair zone model (alpha, eps, phi) with the cases still to come from daily delays."""

    def __init__(self, base, hub=HUB, window=WINDOW, sigma=SIGMA, tau=TAU, lag_days=None, lag_pairs='all',
                 days='uniform', by='country', mix=0.):
        self.base, self.hub, self.window, self.sig, self.tau, self.mix = base, hub, window, sigma, tau, mix
        self.lag_days, self.lag_pairs, self.days, self.by = lag_days, lag_pairs, days, by

    def groups(self, release):
        """[(zone indices, delay CDF, daily counts)] per province, or one national group."""
        zones = self.base.zones
        F_nat, C, _ = fit_delay(release, self.hub, self.window)
        if self.by == 'country':
            return [(np.arange(len(zones)), F_nat, daily(release, self.hub))], C
        out = []
        for p in sorted({z.rsplit('-', 1)[0] for z in zones}):
            F, _, n = fit_delay(release, self.hub, self.window, p)
            out.append((np.array([i for i, z in enumerate(zones) if z.rsplit('-', 1)[0] == p]), F if n >= MIN_ROWS else F_nat,
                        daily(release, self.hub, p)))
        return out, C

    def sample(self, release, weeks, draws, seed=1000):
        """[draws, weeks, zones]; with mix > 0 that share of the draws comes from the release-pair model."""
        n_pairs = int(round(self.mix * draws))
        own = self.daily_sample(release, weeks, draws - n_pairs, seed)
        if not n_pairs:
            return own
        return np.concatenate([own, self.base.sample(release, weeks, n_pairs, seed + draws)])

    def daily_sample(self, release, weeks, draws, seed=1000):
        groups, C = self.groups(release)
        L = entry_lag(release, self.hub, self.window, self.lag_pairs) if self.lag_days is None else self.lag_days
        R = self.base.rel[release].reindex(columns=self.base.zones, fill_value=0)
        all_weeks = list(R.index)
        imp = self.base.imp[release].reindex(index=all_weeks, columns=self.base.zones, fill_value=0)
        old = [w for w in all_weeks if 5 <= lag(release, w) <= 12]
        m = imp.loc[old].values.sum() / R.loc[old].values.sum()
        a, e, phi = self.base.params['alpha'], self.base.params['eps'], self.base.params['phi']
        if self.days == 'trend':
            gi, F, cd = groups[0]
            tdays = pd.date_range(C - pd.Timedelta(days=TREND_DAYS - 1), C)
            age = np.array([(C - d).days for d in tdays])
            cnt = cd.reindex(tdays, fill_value=0).values.astype(float)
            tt = -age / 7.
            x, cov = fit_trend(cnt, shifted(F, age, L), tt)
            k = np.exp(x[2])
        out = np.empty((draws, len(weeks), len(self.base.zones)))
        for d in range(draws):
            rng = np.random.default_rng(seed + d)
            shift, stretch = max(0., L + self.tau * rng.standard_normal()), np.exp(self.sig * rng.standard_normal())
            if self.days == 'trend':
                b = rng.multivariate_normal(x[:2], cov)
                mu = np.exp(b[0] + b[1] * tt)
                Fd = shifted(F, age, shift, stretch)
                U = pd.Series(rng.poisson(rng.gamma(k + cnt, 1 / (k / mu + Fd)) * (1 - Fd)), index=tdays)
                remaining = [{0: U.reindex(week_days(w, C), fill_value=0).sum()} for w in weeks]
            else:
                remaining = []
                for w in weeks:
                    rw = {}
                    for g, (gi, F, _) in enumerate(groups):
                        Fw = completeness(F, C, [w], shift, stretch)[0]
                        rw[g] = R.loc[w].values[gi].sum() * (1 - Fw) / Fw
                    remaining.append(rw)
            for j, w in enumerate(weeks):
                i = all_weeks.index(w)
                c = R.loc[w].values.astype(float)
                level = R.iloc[max(0, i - 3):i].mean(0).values if i else 0 * c
                bz = a * c + (1 - a) * level + e
                mu = np.zeros_like(c)
                for g, (gi, _, _) in enumerate(groups):
                    mu[gi] = remaining[j][g] * bz[gi] / bz[gi].sum()
                if self.days == 'trend':   # the national total is already a draw: share it out
                    added = rng.multinomial(int(remaining[j][0]), bz / bz.sum())
                else:
                    mu = np.maximum(mu, 1e-9)
                    added = rng.negative_binomial(phi, phi / (phi + mu))
                out[d, j] = c + added + imp.loc[w].values + rng.poisson(m * added)
        return out


def wis(samples, y):
    q = np.quantile(samples, Q, axis=0)
    return 2 * np.mean(np.maximum(Q[:, None] * (y - q), (Q[:, None] - 1) * (y - q)), 0)


VARIANTS = {
    'A release pairs (current submission nowcast)': None,
    'B daily, uniform days, no entry lag': dict(lag_days=0., tau=0.),
    'C daily, uniform days, entry lag from all pairs': dict(),
    'D daily, uniform days, entry lag from last pair': dict(lag_pairs='last'),
    'E daily, uniform days, entry lag, province delays': dict(by='province'),
    'F daily, trend days, entry lag': dict(days='trend'),
    'G daily, trend days, entry lag, no delay spread': dict(days='trend', tau=0., sigma=0.),
    'H half C, half A': dict(mix=.5),
    'I half F, half A': dict(days='trend', mix=.5),
    'J daily, uniform days, entry lag, wider delay spread': dict(tau=1.5, sigma=.25),
    'K half J, half A': dict(tau=1.5, sigma=.25, mix=.5),
}


def backtest(origins=('2026-10-24', '2026-11-01', '2026-11-08', '2026-11-15'), variants=VARIANTS, draws=200, hub=HUB):
    """Each origin: the five newest onset weeks at that release, scored on the latest release's counts."""
    t = pd.read_csv(Path(hub) / 'target-data/time-series.csv')
    latest = t.as_of.max()
    truth = t[t.as_of == latest].pivot(index='target_end_date', columns='location', values='observation')
    zones = sorted(t[(t.location.str.count('-') == 2) & (t.observation > 0)].location.unique())
    rows = []
    for r in origins:
        weeks = [w for w in sorted(truth.index) if 0 <= lag(r, w) <= 4 and pd.Timestamp(w) <= pd.Timestamp(r)]
        base = Nowcast(zones, hub, until=r)
        print(r, 'entry lag all pairs', entry_lag(r, hub), 'last pair', entry_lag(r, hub, pairs='last'), flush=True)
        for name, opt in variants.items():
            s = (base if opt is None else DailyNowcast(base, hub, **opt)).sample(r, weeks, draws)
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
    return d.assign(inside=inside, err=d['median'] - d.truth, width=d.q95 - d.q05).groupby('model').agg(
        national_wis=('national_wis', 'mean'), zone_wis=('zone_wis', 'mean'), cover90=('inside', 'mean'),
        median_error=('err', 'mean'), width90=('width', 'mean'), n=('truth', 'size')).round(3)


if __name__ == '__main__':
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'data/ebola/daily-nowcast-backtest')
    out.mkdir(parents=True, exist_ok=True)
    d, latest = backtest()
    d.to_csv(out / f'backtest-{latest}.csv', index=False)
    old = str((pd.Timestamp(latest) - pd.Timedelta(weeks=2)).date())
    print(f'\nall origin-weeks, scored on {latest} counts: mean WIS (lower is better), 90% interval coverage')
    print(summarize(d).to_string())
    print(f'\nonly weeks ending on or before {old} (nearly complete at {latest})')
    print(summarize(d[d.week <= old]).to_string())
    print('\nnational WIS by origin')
    print(d.pivot_table(index='origin', columns='model', values='national_wis').round(1).to_string())
    print('\nby lag at the origin, national WIS')
    print(d.pivot_table(index='lag', columns='model', values='national_wis').round(1).to_string())
    print(d.pivot_table(index=['origin', 'week', 'truth'], columns='model', values='median').round(0).to_string())
