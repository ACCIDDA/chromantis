"""Release-to-release nowcast of BDBV weekly confirmed cases by health zone (onset weeks).

A week keeps gaining cases for about five releases after it ends. Between two weekly releases,
the cases added to health zone i for an onset week that was k weeks old at the first release are

    added ~ NegBin(mean = theta_k * (alpha * reported_i + (1 - alpha) * level_i + eps), size = phi)

where reported_i is the count at the first release, level_i the mean of the zone's three previous
onset weeks at that release, theta_k the release's growth for lag k (shared by every zone), alpha,
eps and phi fitted by maximum likelihood. Zones that report zero but had recent cases can therefore
gain cases (16 zones went from 0 to positive for the newest week between the 17 and 24 October
releases), and eps lets a quiet zone receive a case. theta_k varies a lot between releases (weeks
three weeks old gained 11 cases in one release pair and 41 in the next), so each draw multiplies it
by a shared lognormal factor whose spread is the disagreement between the two release pairs.
A week is final after lag 4. Provinces and the country are sums of their health zones.

History: until 27 Oct the nowcast multiplied each zone's reported count by a chained national
completion factor with assumed spreads (sd 0.35 on the log scale for the newest week), so a zone
reporting zero always stayed at zero.

    .venv/bin/python scripts/ebola_nowcast.py      # fit on 17->24 Oct, check on 9->17 Oct
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln

HUB = Path('../hubs/BDBV-Modeling-Hub')
LAGS = range(5)          # lags (weeks since the onset week ended) that still grow
PAIRS = [('2026-10-09', '2026-10-17'), ('2026-10-17', '2026-10-24')]   # (earlier, later) releases
FIT = PAIRS[1]           # the only Saturday-to-Saturday pair; 9 Oct was a Friday release


def releases(hub=HUB):
    """{release date: DataFrame index=onset week, columns=health-zone codes} for BDBV health zones."""
    t = pd.read_csv(Path(hub) / 'target-data/time-series.csv')
    t = t[t.location.str.count('-') == 2]            # health zones only: codes CD-XX-NN
    return {a: g.pivot(index='target_end_date', columns='location', values='observation').fillna(0)
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

    def __init__(self, zones, hub=HUB):
        self.rel, self.zones = releases(hub), list(zones)
        d = {p: steps(self.rel, *p, self.zones) for p in PAIRS}
        self.params = fit(d[FIT])
        a, e = self.params['alpha'], self.params['eps']
        self.theta = pd.DataFrame({p[1]: thetas(d[p], a, e) for p in PAIRS})   # lag x release pair
        logs = np.log(self.theta.clip(lower=1e-3))
        # Spread of the shared growth factor: disagreement between the two release pairs, pooled over
        # lags 1-4 (lag 0 has no comparable value in the Friday 9 Oct release); never below 0.35.
        diff = (logs.iloc[:, 1] - logs.iloc[:, 0]).loc[1:4]
        self.sigma = float(max(np.sqrt((diff ** 2).mean() / 2), .35))
        self.mean_theta = np.exp(logs.mean(1)).fillna(self.theta[FIT[1]])   # lag 0: the 17->24 Oct pair only
        self.steps = d

    def sample(self, release, weeks, draws, seed=1000, theta=None, sigma=None):
        """[draws, weeks, zones] final counts for onset `weeks` from `release` (lags 0-4 grow)."""
        theta = self.mean_theta if theta is None else theta
        sigma = self.sigma if sigma is None else sigma
        R = self.rel[release].reindex(columns=self.zones, fill_value=0)
        all_weeks = list(R.index)
        out = np.empty((draws, len(weeks), len(self.zones)))
        a, e, phi = self.params['alpha'], self.params['eps'], self.params['phi']
        for d in range(draws):
            rng = np.random.default_rng(seed + d)
            factor = {k: theta[k] * np.exp(sigma * rng.standard_normal() - sigma ** 2 / 2) for k in LAGS}
            for j, w in enumerate(weeks):
                i = all_weeks.index(w)
                c = R.loc[w].values.astype(float)
                level = R.iloc[max(0, i - 3):i].mean(0).values if i else 0 * c
                for k in range(lag(release, w), max(LAGS) + 1):
                    mu = np.maximum(factor[k] * (a * c + (1 - a) * level + e), 1e-9)
                    c = c + rng.negative_binomial(phi, phi / (phi + mu))
                out[d, j] = c
        return out


def check():
    """Fit on 17->24 Oct; predict the 9->17 Oct additions per zone and the national total."""
    t = pd.read_csv(HUB / 'target-data/time-series.csv')
    zones = sorted(t[(t.location.str.count('-') == 2) & (t.observation > 0)].location.unique())
    n = Nowcast(zones)
    print('fitted on', FIT, n.params, 'sigma', round(n.sigma, 3))
    print('growth per lag (cases added / base) by release pair:\n', n.theta.round(3).to_string())
    d = n.steps[PAIRS[0]]
    a, e, phi = n.params['alpha'], n.params['eps'], n.params['phi']
    # Zone-level allocation and dispersion: theta fixed to the held-out pair's realized totals.
    rng = np.random.default_rng(0)
    mu = n.theta[PAIRS[0][1]].loc[d.k].values * base(d, a, e).values
    sims = rng.negative_binomial(phi, phi / (phi + np.maximum(mu, 1e-9)), size=(2000, len(d)))
    lo, hi = np.quantile(sims, .05, 0), np.quantile(sims, .95, 0)
    inside = (d.added.values >= lo) & (d.added.values <= hi)
    zero = d.reported.values == 0
    print(f'held-out 9->17 Oct, {len(d)} zone-weeks: 90% interval covers {inside.mean():.1%} of zone additions; '
          f'{inside[zero].mean():.1%} where the zone reported 0')
    pz = 1 - (phi / (phi + np.maximum(mu, 1e-9))) ** phi
    print(f'zone-weeks reported 0 that gained cases: {int(((d.added > 0) & zero).sum())} observed, '
          f'{pz[zero].sum():.1f} expected')
    # National total for the held-out pair with theta from the fitted pair only (the prospective case).
    tot = []
    for s in range(2000):
        f = {k: n.theta[FIT[1]][k] * np.exp(n.sigma * rng.standard_normal() - n.sigma ** 2 / 2) for k in LAGS}
        m = np.array([f[k] for k in d.k]) * base(d, a, e).values
        tot.append(rng.negative_binomial(phi, phi / (phi + np.maximum(m, 1e-9))).sum())
    print(f'held-out national additions: observed {int(d.added.sum())}, predicted median {np.median(tot):.0f} '
          f'(90%: {np.quantile(tot, .05):.0f}-{np.quantile(tot, .95):.0f})')


if __name__ == '__main__':
    check()
