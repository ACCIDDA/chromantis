"""Where is our MetroCast median in the bottom 10% of the other models' medians (any week 0-3, or -1..3 for California)?
Usage: python lowest_metrocast.py FILE.parquet"""
import glob, sys, pandas as pd
hub = '../../../hubs/flu-metrocast'
rows = []
for f in glob.glob(f'{hub}/model-output/*/2026-11-28-*.parquet'):
    m = f.split('/')[-2]
    if 'Chromantis' in m: continue
    d = pd.read_parquet(f); d['date'] = pd.to_datetime(d.target_end_date)
    rows.append(d.groupby(['target', 'location', 'date']).value.median().rename(m))
p = pd.concat(rows, axis=1)
o = pd.read_parquet(sys.argv[1]); o['date'] = pd.to_datetime(o.target_end_date)
o = o.groupby(['target', 'location', 'date']).value.median().rename('ours')
x = p.join(o, how='inner')
x = x[x.index.get_level_values('date') <= '2026-12-19']
models = p.columns
pct = x[models].lt(x.ours, axis=0).sum(1) / x[models].notna().sum(1)
n = x[models].notna().sum(1)
low = pct[(pct < 0.10) & (n >= 3)]
print('tasks:', len(x), '| bottom 10%:', len(low))
print(low.reset_index().groupby(['target', 'location']).date.apply(lambda s: [str(d.date())[5:] for d in s]).to_string())
