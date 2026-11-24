"""National series from the INSP daily situation reports (data/ebola/insp-sitreps.csv), by reporting day.

    .venv/bin/python scripts/plot_insp_sitreps.py   # -> data/ebola/insp-sitreps.png

Four panels, one measure each: new confirmed cases per reporting day (difference of the cumulative
national count, the sum of the report's province rows) beside the Hub's confirmed cases by week of
symptom onset (latest release, divided by 7 to be per day); the contact follow-up rate (contacts seen /
under follow-up); suspected cases validated from alerts; laboratory positivity. The newest upload of each
report number is used.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

BLUE, ORANGE, INK, MUTED = '#2a78d6', '#eb6834', '#2b2b29', '#77766f'

d = pd.read_csv('data/ebola/insp-sitreps.csv', parse_dates=['report_date'])
d = d[d.latest]
nat = lambda table, ind: d[(d.table == table) & (d.location == 'CD') & (d.indicator == ind)].groupby('report_date').value.last()

cum = d[(d.table == 'zones') & (d.level == 'province') & (d.indicator == 'cum_cases')].groupby('report_date').value.sum()
cum = cum.reindex(pd.date_range(cum.index.min(), cum.index.max())).interpolate()  # missing reports: spread evenly
daily = cum.diff()
hub = pd.read_csv('production/hubs/BDBV-Modeling-Hub/target-data/time-series.csv')
hub = hub[(hub.as_of == hub.as_of.max()) & (hub.location == 'CD')]
hub = hub.assign(week=pd.to_datetime(hub.target_end_date)).set_index('week').observation / 7

rate = (100 * nat('contacts', 'contacts_seen') / nat('contacts', 'contacts_followed')).combine_first(nat('headline', 'contacts_seen_pct'))
suspects = nat('alerts', 'suspects_validated')
positivity = nat('lab', 'positivity_pct')

fig, ax = plt.subplots(4, 1, figsize=(10, 11), sharex=True)
ax[0].plot(daily.index, daily.rolling(7, center=True).mean(), color=BLUE, lw=2, label='Sitreps: new confirmed per reporting day (7-day mean)')
ax[0].step(hub.index, hub.values, where='post', color=ORANGE, lw=2, label=f'Hub: confirmed by onset week / 7 (release {hub.index.max():%d %b}, recent weeks incomplete)')
ax[0].set_ylabel('cases per day')
ax[0].legend(frameon=False, fontsize=8, loc='upper left')
for a, s, label in [(ax[1], rate, 'contact follow-up rate (%)'), (ax[2], suspects, 'suspected cases validated per day'),
                    (ax[3], positivity, 'laboratory positivity (%)')]:
    a.plot(s.index, s.values, color=BLUE, lw=1.2, marker='o', ms=2.5)
    a.set_ylabel(label)
ax[1].axhline(95, color=MUTED, lw=1, ls='--')
ax[1].text(ax[1].get_xlim()[0], 95, ' 95% target', va='bottom', color=MUTED, fontsize=8)
for a in ax:
    a.spines[['top', 'right']].set_visible(False)
    a.grid(axis='y', color='#e4e3dd', lw=0.8)
    a.tick_params(colors=INK, labelsize=8)
    a.set_ylim(bottom=0)
fig.suptitle('INSP daily situation reports, DRC, national (by reporting day)', color=INK)
fig.tight_layout()
fig.savefig('data/ebola/insp-sitreps.png', dpi=130)
print('data/ebola/insp-sitreps.png')
