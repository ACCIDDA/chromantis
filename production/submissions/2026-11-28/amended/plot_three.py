"""Three lines per location: amended, not amended (masked A, PR 4244) and the median of the 71 other models.
Medians with dots, observed Hub target data in black; admissions on the left, ED share on the right."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
H = 'production/hubs/FluSight-forecast-hub'; A = 'production/submissions/2026-11-28/amended'
loc = pd.read_csv(f'{H}/auxiliary-data/locations.csv', dtype=str).set_index('location')
files = {'Amended': (f'{A}/2026-11-28-ACCIDDA-Chromantis.csv', 'C3'),
         'Not amended (masked A)': ('production/submissions/2026-11-28/2026-11-28-ACCIDDA-Chromantis.csv', 'C0'),
         'Median of the 71 other models': (f'{A}/2026-11-28-HubMedian-standin.csv', '0.35')}
F = {}
for k, (f, _) in files.items():
    d = pd.read_csv(f, dtype={'location': str, 'output_type_id': str})
    d = d[d.target.str.startswith('wk inc') & (d.output_type_id == '0.5')]
    F[k] = d.assign(date=pd.to_datetime(d.target_end_date))
obs = {'wk inc flu hosp': pd.read_csv(f'{H}/target-data/target-hospital-admissions.csv', dtype={'location': str}),
       'wk inc flu prop ed visits': pd.read_csv(f'{H}/target-data/target-ed-visits-prop.csv', dtype={'location': str})}
for o in obs.values(): o['date'] = pd.to_datetime(o.date)
used = pd.read_csv(f'{A}/decision-flusight.csv', index_col=0)
choice = {**{s: 'other models' for s in 'AK AL CO FL GA HI ID KY LA MS MT NV RI TN UT WY'.split()},
          **{s: '50/50' for s in 'CA DE MA ME NE OR TX WA'.split()}}
order = ['US'] + sorted(l for l in F['Amended'].location.unique() if l != 'US')
with PdfPages(f'{A}/2026-11-28-flusight-amended-vs-not-vs-other-models.pdf') as pdf:
    for i in range(0, len(order), 4):
        fig, axes = plt.subplots(4, 2, figsize=(8.5, 11))
        for r, l in enumerate(order[i:i + 4]):
            ab = loc.loc[l, 'abbreviation']
            for c, t in enumerate(['wk inc flu hosp', 'wk inc flu prop ed visits']):
                ax = axes[r, c]; scale = 100 if c else 1
                o = obs[t][(obs[t].location == l) & (obs[t].date >= '2026-09-01')].sort_values('date')
                ax.plot(o.date, o.value * scale, 'k.-', ms=3, lw=1, label='observed')
                for k, (_, col) in files.items():
                    d = F[k][(F[k].location == l) & (F[k].target == t)].sort_values('date')
                    ax.plot(d.date, d.value * scale, '-o', color=col, ms=3, lw=1.6 if k == 'Amended' else 1.2, label=k)
                ax.set_title(f"{loc.loc[l, 'location_name']} ({ab}): {'admissions' if c == 0 else '% ED visits'}"
                             + (f" - used: {choice.get(ab, 'masked A')}" if c == 0 else ''), fontsize=8)
                ax.tick_params(labelsize=7); ax.set_ylim(0, None)
                ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d %b'))
        for ax in axes.flat[2 * len(order[i:i + 4]):]: ax.axis('off')
        axes[0, 0].legend(fontsize=6, loc='upper left')
        fig.tight_layout(); pdf.savefig(fig); plt.close(fig)
print('done')
