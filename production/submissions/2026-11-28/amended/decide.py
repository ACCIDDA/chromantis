"""State-by-state decision for the 28 Nov FluSight file: keep masked A, or use the median of the other Hub models."""
import glob, numpy as np, pandas as pd
S = '/private/tmp/claude-504/-Users-chadi-Research-chromantis/128c604f-5d47-4d21-bd33-eef1d23eba7d/scratchpad'
H = 'production/hubs/FluSight-forecast-hub'
ab = pd.read_csv(f'{H}/auxiliary-data/locations.csv', dtype=str).set_index('location').abbreviation
ev = pd.read_csv(f'{S}/evidence-20261125.csv').set_index('state')
ev['adm'] = ev.adm_raw * 1.05                     # median upward revision of a first report
ev.loc[ev.lab_pos < 0.6, 'lab_pos'] = np.nan       # one-week drop >40%: incomplete first report
SIG = ['ed', 'adm', 'wastewater', 'ilinet', 'lab_pos']
ev['n'] = ev[SIG].notna().sum(1)
ev['rising'] = (ev[SIG] > 1.05).sum(1)
ev['still_rising'] = ev.rising >= 0.6 * ev.n
def med(f):
    d = pd.read_csv(f, dtype={'location': str, 'output_type_id': str})
    d = d[(d.target == 'wk inc flu hosp') & (d.output_type_id == '0.5') & d.horizon.isin([0, 3])]
    t = d.pivot_table(index='location', columns='horizon', values='value'); t.index = [ab[i] for i in t.index]; return t
ours = med('production/output/2026-11-25/masked-a-20261122/2026-11-28-ACCIDDA-Chromantis.csv')
peer = []
for f in glob.glob(f'{H}/model-output/*/2026-11-28-*.csv') + glob.glob(f'{H}/model-output/*/2026-11-28-*.parquet'):
    if f.split('/')[-2] in ('ACCIDDA-Chromantis', 'FluSight-baseline', 'FluSight-ensemble'): continue
    d = pd.read_parquet(f) if f.endswith('parquet') else pd.read_csv(f, dtype={'location': str, 'output_type_id': str})
    d['output_type_id'] = d.output_type_id.astype(str)
    peer.append(d[(d.target == 'wk inc flu hosp') & (d.output_type == 'quantile') & (d.output_type_id == '0.5') & d.horizon.isin([0, 3])])
pm = pd.concat(peer).groupby(['location', 'horizon']).value.median().unstack(); pm.index = [ab[i] for i in pm.index]
t = ev.join(ours.rename(columns={0: 'ours0', 3: 'ours3'})).join(pm.rename(columns={0: 'peer0', 3: 'peer3'}))
t['ours_falls'] = t.ours3 < t.ours0
t['decision'] = np.where(t.ours_falls & t.still_rising, 'peer median', 'masked A')
t.to_csv(f'{S}/decision-flusight.csv')
pd.set_option('display.width', 250)
show = t[['ed', 'adm', 'wastewater', 'ilinet', 'lab_pos', 'rising', 'n', 'ours0', 'ours3', 'peer0', 'peer3', 'decision']]
print(show.round(2).sort_values(['decision', 'rising']).to_string())
print(t.decision.value_counts().to_dict())
