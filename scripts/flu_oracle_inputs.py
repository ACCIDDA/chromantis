"""Replay saved flu fits on input histories as known later (the 18 Nov 2026 data) instead of each Wednesday's reports.

Question (20 Nov 2026): how much forecast skill is lost because the newest reported weeks are incomplete? The
same fitted models (no retraining) are given, for each 2026-27 issuance, the admission and ED histories as they
stood in the 18 November 2026 data instead of as reported that Wednesday. Run them with correction strength 0
(trees off: the inputs are already revised). Kinsa and other covariates stay as reported.

    .venv/bin/python scripts/flu_oracle_inputs.py build            # writes the oracle panel
    .venv/bin/python scripts/flu_oracle_inputs.py run RELEASE ISSUANCE

The oracle panel is the 18 Nov panel with every 2026-27 issuance's as-of admissions/ED replaced by the 18 Nov
values. The production check that future outcomes are absent is disabled (the 18 Nov panel already holds them;
they are labels, never inputs).
"""
import sys
import numpy as np

SRC = 'data/operational-20261118/processed/panel.npz'
ORACLE = 'data/operational-20261118-oracle/processed/panel.npz'

if sys.argv[1] == 'build':
    from chromantis.dataset.build import load, save, _visible_like
    p = load(SRC)
    rows = p['issuance_dates'] >= np.datetime64('2026-10-01')
    vis = np.broadcast_to(_visible_like(p, 'asof_targets'), p['asof_targets'].shape)
    a = p['asof_targets'].copy()
    a[rows] = np.where(vis[rows], p['targets'][None], np.nan)
    p['asof_targets'] = a
    save(p, ORACLE)
    print('wrote', ORACLE, int(rows.sum()), 'issuances replaced')
else:
    import chromantis.production.forecast as F
    from chromantis.production.__main__ import run
    original = F.episodes

    def episodes(*a, **k):
        out = original(*a, **k)
        for e in out:
            e['target_available'] = np.zeros_like(e['target_available'])
            e['target_values'] = np.zeros_like(e['target_values'])
            e['Y'] = np.stack((e['target_values'], e['target_available']), axis=2)
        return out
    F.episodes = episodes
    release, iss = sys.argv[2], sys.argv[3]
    run(['--release', f'production/releases/{release}.json', '--dataset', ORACLE, '--issuance', iss,
         '--out', f'production/output/2026-11-20/oracle-inputs/{iss}/{release}', '--no-plots', '--jobs', '4'])
