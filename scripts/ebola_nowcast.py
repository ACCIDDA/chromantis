"""Release-to-release nowcast of BDBV weekly confirmed cases by health zone (onset weeks).

A week keeps gaining cases for about five releases after it ends. Between two weekly releases,
the cases added to health zone i for an onset week that was k weeks old at the first release are

    added ~ NegBin(mean = theta_k * (alpha * reported_i + (1 - alpha) * level_i + eps), size = phi)

where reported_i is the count at the first release, level_i the mean of the zone's three previous
onset weeks at that release, theta_k the release's growth for lag k (shared by every zone), alpha,
eps and phi fitted by maximum likelihood. Zones that report zero but had recent cases can therefore
gain cases (16 zones went from 0 to positive for the newest week between the 17 and 24 October
releases), and eps lets a quiet zone receive a case. theta_k varies a lot between releases (weeks
three weeks old gained 11 cases in one release pair and 41 in the next); a draw takes the geometric
mean over the two latest release pairs (RECENT_PAIRS) and multiplies it
by a shared lognormal factor, with a spread per lag: the standard deviation of log theta_k across
release pairs (at least 0.2), or lag 1's spread plus 0.15 for a lag seen in only one pair. A week is
final after lag 4. Provinces and the country are sums of their health zones.

The model runs on cases with an observed onset date only. The hub gives cases reported without one
an onset date drawn from its delay distribution (auxiliary-data/imputation-details.md), so a batch of
them lands in the newest weeks at once. Those already imputed are added unchanged; the cases still to
come get the usual share without onset date on top (Poisson, mean m times the observed cases added),
with m the imputed/observed ratio of weeks 5-12 weeks old at the release.

History: until 27 Oct the nowcast multiplied each zone's reported count by a chained national
completion factor with assumed spreads (sd 0.35 on the log scale for the newest week), so a zone
reporting zero always stayed at zero. The 31 October submission used one spread for all lags, 0.72,
pooled equally over lags 1-4. Lags 3-4 dominated it (disagreement 1.4 on the log scale, on few cases)
while lags 1-2 disagreed by 0.3, which put the newest week's 95th percentile at 1,130 national cases
from 91 reported, about twice the largest week so far (595). Until 3 Nov the model ran on all
cases, imputed onsets included: the report week ending 31 Oct carried 141 cases without onset date
(40-90 in other weeks), 59 of the newest week's 150 cases had imputed onsets (11 of 91 a week before),
and multiplying them as if they were early reports lifted the newest two weeks to 614 and 652 national
cases while cases by report week stayed at 400-500. Until 17 Nov theta_k was the geometric mean over
every release pair since 9 Oct (see RECENT_PAIRS).

    .venv/bin/python scripts/ebola_nowcast.py      # fit on the latest release pair, check on the first
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln

HUB = Path('production/hubs/BDBV-Modeling-Hub')
LAGS = range(5)          # lags (weeks since the onset week ended) that still grow
FIRST_RELEASE = '2026-10-09'   # consecutive releases from here on are compared; 18 Aug is too far back
MIN_SIGMA, NO_REPLICATE_MARGIN = .2, .15
RECENT_PAIRS = 2         # theta_k = geometric mean over this many latest release pairs (spread uses all pairs)


def releases(hub=HUB, imputed=False):
    """{release date: DataFrame index=onset week, columns=health-zone codes} for BDBV health zones,
    cases with an observed onset date (or, with imputed=True, those with an imputed one). The two sum
    to the hub's weekly target data."""
    t = pd.read_csv(Path(hub) / 'auxiliary-data/daily-confirmed-case.csv')
    t = t[(t.location.str.count('-') == 2) & (t.imputed == imputed)]   # health zones only: codes CD-XX-NN
    day = pd.to_datetime(t.target_end_date)
    t = t.assign(week=(day + pd.to_timedelta((5 - day.dt.weekday) % 7, 'D')).dt.strftime('%Y-%m-%d'))
    return {a: g.pivot_table(index='week', columns='location', values='observation', aggfunc='sum').fillna(0)
            for a, g in t.groupby('as_of')}


def lag(release, week):
    """Whole weeks between an onset week's end and a release (the Friday 9 Oct counts as 10 Oct)."""
    return int(round((pd.Timestamp(release) - pd.Timestamp(week)).days / 7))


def steps(rel, a, b, zones):
    """One row per (zone, onset week) with lag 0-4 at release a: reported, level, added by release b."""
    A, B = rel[a].reindex(columns=zones, fill_value=0), rel[b].reindex(columns=zones, fill_value=0)
    weeks = list(A.index)
    rows = []
    for j, w in enumerate(weeks):
        k = lag(a, w)
        if k not in LAGS or pd.Timestamp(w) > pd.Timestamp(a):   # the week must have ended at release a
            continue
        level = A.iloc[max(0, j - 3):j].mean(0) if j else A.iloc[0] * 0
        added = (B.loc[w] - A.loc[w]).clip(lower=0)             # a few downward revisions become 0
        rows.append(pd.DataFrame(dict(zone=zones, week=w, k=k, reported=A.loc[w].values, level=level.values,
                                      added=added.values)))
    return pd.concat(rows, ignore_index=True)


def nb_logpmf(y, mu, phi):
    p = phi / (phi + mu)
    return gammaln(y + phi) - gammaln(phi) - gammaln(y + 1) + phi * np.log(p) + y * np.log1p(-p + 1e-300)


def base(d, alpha, eps):
    return alpha * d.reported + (1 - alpha) * d.level + eps


def thetas(d, alpha, eps):
    """Realized growth per lag: cases added / base, i.e. theta_k that matches this release pair's total."""
    b = base(d, alpha, eps)
    return (d.added.groupby(d.k).sum() / b.groupby(d.k).sum()).reindex(LAGS)


def fit(d):
    """alpha, eps, phi by maximum likelihood with theta_k profiled to each lag's realized total."""
    def loss(x):
        alpha, eps, phi = 1 / (1 + np.exp(-x[0])), np.exp(x[1]), np.exp(x[2])
        mu = thetas(d, alpha, eps).loc[d.k].values * base(d, alpha, eps).values
        return -nb_logpmf(d.added.values, np.maximum(mu, 1e-9), phi).sum()
    x = minimize(loss, [0., np.log(.05), 0.], method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-4, fatol=1e-4)).x
    return dict(alpha=float(1 / (1 + np.exp(-x[0]))), eps=float(np.exp(x[1])), phi=float(np.exp(x[2])))


class Nowcast:
    """Fitted step model; `sample` turns one release into final health-zone counts."""

    def __init__(self, zones, hub=HUB, until=None):
        """Uses consecutive releases up to `until` (default all), so an old round can be rerun as it stood."""
        self.rel, self.imp, self.zones = releases(hub), releases(hub, imputed=True), list(zones)
        dates = [r for r in sorted(self.rel) if r >= FIRST_RELEASE and (until is None or r <= until)]
        self.pairs = list(zip(dates, dates[1:]))
        self.fit_pair = self.pairs[-1]
        d = {p: steps(self.rel, *p, self.zones) for p in self.pairs}
        self.params = fit(d[self.fit_pair])
        a, e = self.params['alpha'], self.params['eps']
        self.theta = pd.DataFrame({p[1]: thetas(d[p], a, e) for p in self.pairs})   # lag x release pair
        logs = np.log(self.theta.clip(lower=1e-3))
        # Growth: the latest RECENT_PAIRS pairs only. Until 17 Nov it averaged every pair since 9 Oct;
        # the 8 and 15 Nov pairs agree on much slower late growth (lag 2: 0.018 and 0.025, against
        # 0.09-0.20 before), and the all-pair average overshot the national count for weeks 1-2 weeks
        # old by 10-22% in the 7 and 14 Nov rounds. Rerun on the 24 Oct, 1 Nov and 8 Nov releases
        # against the 15 Nov counts, the last two pairs gave mean national WIS 35.1 against 36.1.
        self.mean_theta = np.exp(logs.iloc[:, -RECENT_PAIRS:].mean(1)).fillna(np.exp(logs.mean(1)))
        # Spread of the shared growth factor, per lag. A lag seen in one pair has no disagreement to
        # measure (lag 0 in the Friday 9 Oct release), so it takes lag 1's spread plus a margin.
        sd = logs.std(axis=1, ddof=1).clip(lower=MIN_SIGMA)
        self.sigma = {k: float(sd[k]) if np.isfinite(sd[k]) else float(sd[1]) + NO_REPLICATE_MARGIN for k in LAGS}
        self.steps = d

    def sample(self, release, weeks, draws, seed=1000, theta=None, sigma=None):
        """[draws, weeks, zones] final counts for onset `weeks` from `release` (lags 0-4 grow), imputed onsets included."""
        theta = self.mean_theta if theta is None else theta
        sigma = self.sigma if sigma is None else sigma
        R = self.rel[release].reindex(columns=self.zones, fill_value=0)
        all_weeks = list(R.index)
        imp = self.imp[release].reindex(index=all_weeks, columns=self.zones, fill_value=0)
        old = [w for w in all_weeks if 5 <= lag(release, w) <= 12]
        m = imp.loc[old].values.sum() / R.loc[old].values.sum()
        out = np.empty((draws, len(weeks), len(self.zones)))
        a, e, phi = self.params['alpha'], self.params['eps'], self.params['phi']
        for d in range(draws):
            rng = np.random.default_rng(seed + d)
            factor = {k: theta[k] * np.exp(sigma[k] * rng.standard_normal() - sigma[k] ** 2 / 2) for k in LAGS}
            for j, w in enumerate(weeks):
                i = all_weeks.index(w)
                c = R.loc[w].values.astype(float)
                level = R.iloc[max(0, i - 3):i].mean(0).values if i else 0 * c
                for k in range(lag(release, w), max(LAGS) + 1):
                    mu = np.maximum(factor[k] * (a * c + (1 - a) * level + e), 1e-9)
                    c = c + rng.negative_binomial(phi, phi / (phi + mu))
                added = c - R.loc[w].values
                out[d, j] = c + imp.loc[w].values + rng.poisson(m * added)
        return out


def check():
    """Fit on the latest release pair; predict the first pair's additions per zone and the national total."""
    t = pd.read_csv(HUB / 'target-data/time-series.csv')
    zones = sorted(t[(t.location.str.count('-') == 2) & (t.observation > 0)].location.unique())
    n = Nowcast(zones)
    held_out = n.pairs[0]
    print('fitted on', n.fit_pair, n.params, 'sigma per lag', {k: round(v, 2) for k, v in n.sigma.items()})
    print('growth per lag (cases added / base) by release pair:\n', n.theta.round(3).to_string())
    d = n.steps[held_out]
    a, e, phi = n.params['alpha'], n.params['eps'], n.params['phi']
    # Zone-level allocation and dispersion: theta fixed to the held-out pair's realized totals.
    rng = np.random.default_rng(0)
    mu = n.theta[held_out[1]].loc[d.k].values * base(d, a, e).values
    sims = rng.negative_binomial(phi, phi / (phi + np.maximum(mu, 1e-9)), size=(2000, len(d)))
    lo, hi = np.quantile(sims, .05, 0), np.quantile(sims, .95, 0)
    inside = (d.added.values >= lo) & (d.added.values <= hi)
    zero = d.reported.values == 0
    print(f'held-out {held_out}, {len(d)} zone-weeks: 90% interval covers {inside.mean():.1%} of zone additions; '
          f'{inside[zero].mean():.1%} where the zone reported 0')
    pz = 1 - (phi / (phi + np.maximum(mu, 1e-9))) ** phi
    print(f'zone-weeks reported 0 that gained cases: {int(((d.added > 0) & zero).sum())} observed, '
          f'{pz[zero].sum():.1f} expected')
    # National total for the held-out pair with theta from the fitted pair only (the prospective case).
    tot = []
    for s in range(2000):
        f = {k: n.theta[n.fit_pair[1]][k] * np.exp(n.sigma[k] * rng.standard_normal() - n.sigma[k] ** 2 / 2) for k in LAGS}
        m = np.array([f[k] for k in d.k]) * base(d, a, e).values
        tot.append(rng.negative_binomial(phi, phi / (phi + np.maximum(m, 1e-9))).sum())
    print(f'held-out national additions: observed {int(d.added.sum())}, predicted median {np.median(tot):.0f} '
          f'(90%: {np.quantile(tot, .05):.0f}-{np.quantile(tot, .95):.0f})')


if __name__ == '__main__':
    check()
