"""Amended 28 Nov MetroCast ED: location-by-location choice between the spliced file and the full-season model.

Only locations where the spliced file's week-3 median is below its week-0 median are changed. Evidence: the
location's own newest-week ED growth (Hub data of 25 Nov) plus its state's NHSN admissions (x 1.05), wastewater,
ILINet and lab positivity growth (the same evidence table as the FluSight amendment); rising = growth > 1.05.
  share rising > 0.6 -> all weeks from full_season_finalist_1 (its 100 trajectories, cut at 12 June 2027);
  0.4..0.6           -> 50 trajectories from each (random, seed 0), renumbered S1-S100;
  < 0.4              -> spliced file unchanged.
Usage: python amend_ed.py EVIDENCE_CSV
"""
import sys
import numpy as np, pandas as pd
hub = '../../../hubs/flu-metrocast'
ev = pd.read_csv(sys.argv[1]).set_index('state')
ev['adm'] = ev.adm_raw * 1.05
ev.loc[ev.lab_pos < 0.6, 'lab_pos'] = np.nan
meta = pd.read_csv(f'{hub}/auxiliary-data/locations.csv').drop_duplicates('location').set_index('location')
t = pd.read_csv(f'{hub}/target-data/latest-data.csv').query("target == 'Flu ED visits pct'")
o = t.pivot_table(index='location', columns='target_end_date', values='observation')
sp = pd.read_parquet('spliced/2026-11-28-ACCIDDA-Chromantis.parquet')
fs = pd.read_parquet('fullseason/2026-11-28-ACCIDDA-Chromantis-fullseason.parquet')
fs = fs[pd.to_datetime(fs.target_end_date) <= '2027-06-12']
for d in (sp, fs):
    d['target_end_date'] = pd.to_datetime(d.target_end_date).dt.date; d['reference_date'] = pd.to_datetime(d.reference_date).dt.date
med = sp.groupby(['location', 'target_end_date']).value.median().unstack()
w0, w3 = pd.Timestamp('2026-11-28').date(), pd.Timestamp('2026-12-19').date()
rows = []
for loc in med.index:
    st = meta.loc[loc, 'state_abb']
    s = {'local_ed': o.loc[loc, '2026-11-21'] / o.loc[loc, '2026-11-14'] if '2026-11-21' in o and o.loc[loc, '2026-11-14'] > 0 else np.nan}
    s.update({k: ev.loc[st, k] for k in ('adm', 'wastewater', 'ilinet', 'lab_pos')})
    v = pd.Series(s).dropna()
    share = (v > 1.05).mean() if len(v) else np.nan
    falls = med.loc[loc, w3] < med.loc[loc, w0]
    choice = 'spliced'
    if falls and share > 0.6: choice = 'full-season'
    elif falls and 0.4 <= share <= 0.6: choice = '50/50'
    rows.append({'location': loc, 'state': st, **s, 'share_rising': share, 'falls': falls,
                 'w0': med.loc[loc, w0], 'w3': med.loc[loc, w3], 'choice': choice})
dec = pd.DataFrame(rows).set_index('location')
dec.to_csv('ed-decision.csv')
rng = np.random.default_rng(0)
parts = []
for loc, c in dec.choice.items():
    a, b = sp[sp.location == loc], fs[fs.location == loc]
    if c == 'spliced': parts.append(a)
    elif c == 'full-season': parts.append(b[sp.columns])
    else:
        ids_a = rng.choice(sorted(a.output_type_id.unique()), 50, replace=False)
        ids_b = rng.choice(sorted(b.output_type_id.unique()), 50, replace=False)
        aa = a[a.output_type_id.isin(ids_a)].copy(); bb = b[b.output_type_id.isin(ids_b)].copy()
        aa['output_type_id'] = aa.output_type_id.map({x: f'S{i + 1}' for i, x in enumerate(sorted(ids_a))})
        bb['output_type_id'] = bb.output_type_id.map({x: f'S{i + 51}' for i, x in enumerate(sorted(ids_b))})
        parts.append(pd.concat([aa, bb[sp.columns]]))
out = pd.concat(parts)[sp.columns].sort_values(['location', 'output_type_id', 'target_end_date'])
assert out.groupby(['location', 'target_end_date']).output_type_id.nunique().eq(100).all()
assert len(out) == len(sp) and set(out.output_type_id) <= {f'S{i}' for i in range(1, 101)}
out.to_parquet('spliced/2026-11-28-ACCIDDA-Chromantis-amended.parquet', index=False)
print(dec.choice.value_counts().to_dict())
for c in ('full-season', '50/50'):
    print(c, sorted(dec.index[dec.choice == c]))
print(dec[dec.falls].sort_values('share_rising')[['state', 'local_ed', 'adm', 'wastewater', 'ilinet', 'lab_pos', 'share_rising', 'w0', 'w3', 'choice']].round(2).to_string())
