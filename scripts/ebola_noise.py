"""Artificial reporting noise on the newest Ebola input weeks, for training (and backtest inputs).

At submission the five newest BDBV weeks the models read are nowcast draws, not final counts,
and the newest week is the least certain (68 reported cases became a median of 392 on
8 Nov 2026). The models were trained on final counts only, so they trusted the last week
fully: across a file's 100 trajectories a newest week 10% higher gave a national forecast
about 17% higher four weeks ahead, and earlier weeks entered with negative weight (forecast
from the change into the last week). This perturbs the last five history weeks of every
training episode the way a nowcast error would; labels are never changed.

Noise on week age k (0 = newest), on the log scale of (count + 1):
- one shared factor per episode and age, sd SHARED[k], applied to every location and to the
  outbreak-total covariate (the nowcast's growth factor is shared by all health zones);
- an independent term per location, sd SHARED[k] for health zones, half for provinces, none
  for the outbreak total (provinces and the country are sums of zones).
SHARED is set from the 31 Oct and 7 Nov national nowcasts against the 8 Nov release (error of
the median 0 to +0.21 at ages 0-1, +0.03 to +0.15 at age 2, draws' spread 0.17-0.49 at age 0).
`strength` multiplies every sd. The respiratory hubs' `ReportingErrors` bootstraps archived
reports instead; the Ebola panel has none for West Africa or Kivu and six releases for BDBV.
"""
import numpy as np
import pandas as pd

SHARED = np.array([.35, .2, .12, .06, .03])   # age 0 (newest) .. 4


class InputNoise:
    transport_missingness = False   # read by training.fit_component

    def __init__(self, problem, strength=1.):
        meta = pd.read_csv(problem.locations).set_index('location')
        self.strength = strength
        self.level_scale = {c: {'local': 1., 'middle': .5}.get(meta.level[c], 0.) for c in meta.index}

    def draw(self, episode, rng):
        if self.strength == 0:
            return episode
        sd = self.strength * SHARED
        ages = len(sd)
        v = episode['values'].copy()                      # [lookback, channels, locations]
        scale = np.array([self.level_scale.get(c, 0.) for c in episode['locations']])
        shared = rng.normal(0, sd)                        # [ages]
        own = rng.normal(0, 1, (ages, v.shape[2])) * sd[:, None] * scale[None]
        log_factor = (shared[:, None] + own)[::-1]        # rows ordered oldest -> newest
        tail = v[-ages:]
        v[-ages:] = np.where(episode['available'][-ages:], np.maximum(0, (tail + 1) * np.exp(log_factor[:, None, :]) - 1), tail)
        out = dict(episode, values=v.astype(np.float32))
        if 'covariates' in episode:
            cov = episode['covariates'].copy()            # [lookback, K, 2 (value, available), locations]
            cov[-ages:, :, 0, :] = np.maximum(0, (cov[-ages:, :, 0, :] + 1) * np.exp(shared[::-1])[:, None, None] - 1)
            out['covariates'] = cov.astype(np.float32)
        return out

    def batch(self, episodes_, rng):
        return [self.draw(e, rng) for e in episodes_]
