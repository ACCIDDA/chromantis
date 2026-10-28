"""PDF of the 2026-10-31 MetroCast forecasts: 4-week and full-season, over past seasons.

Usage: python plot_forecast_pdf.py LATEST_DATA LOCATIONS FOUR_WEEK.parquet FULL_SEASON.parquet OUT.pdf
Past seasons are aligned by week of season (season starts on the first Saturday of August).
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

latest, locations, four, full, out = sys.argv[1:6]
obs = pd.read_csv(latest)
obs = obs[obs.target == 'Flu ED visits pct'].assign(date=lambda d: pd.to_datetime(d.target_end_date))
meta = pd.read_csv(locations).set_index('location')
four = pd.read_parquet(four).assign(date=lambda d: pd.to_datetime(d.target_end_date))
full = pd.read_parquet(full).assign(date=lambda d: pd.to_datetime(d.target_end_date))
SEASONS = {'2022-23': 2022, '2023-24': 2023, '2024-25': 2024, '2025-26': 2025}
PAST = dict(zip(SEASONS, ['#c7d3e3', '#9fb3cf', '#6f8db5', '#3f6699']))
START = pd.Timestamp('2026-08-01')


def season_x(dates, year):
    """Map a past season's dates onto the 2026-27 calendar, keeping the week of season."""
    return START + (dates - pd.Timestamp(f'{year}-08-01'))


def bands(d):
    q = d.groupby('date').value.quantile([.025, .25, .5, .75, .975]).unstack()
    return q.index, q


# State first, then its local jurisdictions alphabetically.
order = sorted(set(four.location), key=lambda l: (meta.loc[l, 'state_abb'],
                                                  str(meta.loc[l, 'original_location_code']) != 'All', l))
with PdfPages(out) as pdf:
    fig = plt.figure(figsize=(11, 8.5))
    fig.text(.06, .9, 'ACCIDDA-Chromantis MetroCast forecast, reference date 2026-10-31', fontsize=16, weight='bold')
    fig.text(.06, .52, (
        'Target: percentage of emergency-department visits due to influenza (Hub target data, published 28 October 2026;\n'
        'last observed week 24 October for most locations, 17 October for NYC, 10 October for the 12 Georgia locations).\n\n'
        'Blue, 4-week forecast (the file prepared for submission): season-CV winner, a logit-scale MLP that reads each\n'
        'location\'s own state series through a shared encoder. Five seeds trained on 2022-23 to 2025-26; 100 trajectories.\n'
        'In leave-one-season-out CV its WIS was 0.77 x the direct-MLP reference; on 2025-26, replayed on the Hub\'s\n'
        'archived Wednesday data, 0.82 x the actual MetroCast ensemble (lower is better). Shown: median and 95% interval.\n\n'
        'Orange, full-season trajectories (not validated against any ensemble): weeks 0-3 are the blue forecast;\n'
        'from week 4 each path continues with a rank-matched path of a 52-week-history MLP trained with a whole-path\n'
        'loss (five seeds, 2022-23 to 2025-26), unmodified. At the join it runs ~7% lower (median week-4/week-3 0.93).\n'
        'Shown: median, 50% and 95% pointwise intervals, and six individual whole trajectories (thin lines).\n\n'
        'Black: 2026-27 observations. Blue-grey lines: past seasons, shifted onto this calendar by week of season.'),
        fontsize=10.5, va='top', family='monospace')
    pdf.savefig(fig); plt.close(fig)
    if len(sys.argv) > 6:   # comparison table from compare_models.py
        t = pd.read_csv(sys.argv[6], parse_dates=['peak_week'])
        t = t[t.location.isin(set(four.location))]
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        panels = [('h3_over_last', 'Week-3 median / last observed week (all models)'),
                  ('peak', 'Season peak, % ED visits (median over paths)'),
                  ('total', 'Season total, sum of weekly % (31 Oct - 12 Jun)'),
                  ('peak_week', 'Peak week (median over paths)')]
        for ax, (col, title) in zip(axes.flat, panels):
            g = t.dropna(subset=[col])
            names = list(g.groupby('model')[col].median().sort_values().index) if col != 'peak_week' else \
                list(g.groupby('model')[col].apply(lambda s: s.sort_values().iloc[len(s) // 2]).sort_values().index)
            vals = [(g[g.model == n][col] - pd.Timestamp('2026-10-31')).dt.days / 7 if col == 'peak_week'
                    else g[g.model == n][col] for n in names]
            colors = ['C1' if 'Chromantis' in n else '0.55' if n.startswith('observed') else 'C0' for n in names]
            b = ax.boxplot(vals, vert=False, tick_labels=names, showfliers=False, patch_artist=True)
            for patch, c in zip(b['boxes'], colors):
                patch.set_facecolor(c); patch.set_alpha(.5)
            ax.set_title(title, fontsize=10); ax.tick_params(labelsize=7)
            if col == 'peak_week':
                ax.set_xlabel('weeks after 31 Oct (past seasons aligned by week of season)', fontsize=8)
        fig.suptitle('Across locations: Chromantis (orange) vs other 2026-10-31 Hub submissions (blue) and past seasons (grey)',
                     fontsize=10)
        fig.tight_layout()
        pdf.savefig(fig); plt.close(fig)
    rng = np.random.default_rng(0)
    for page in range(0, len(order), 6):
        fig, axes = plt.subplots(3, 2, figsize=(11, 8.5))
        for ax, loc in zip(axes.flat, order[page:page + 6]):
            o = obs[obs.location == loc]
            for name, year in SEASONS.items():
                s = o[(o.date >= f'{year}-08-01') & (o.date < f'{year + 1}-08-01')]
                ax.plot(season_x(s.date, year), s.observation, color=PAST[name], lw=1, label=name)
            f = full[full.location == loc]
            if len(f):
                x, q = bands(f)
                ax.fill_between(x, q[.025], q[.975], color='C1', alpha=.15, lw=0, label='full season 95%')
                ax.fill_between(x, q[.25], q[.75], color='C1', alpha=.3, lw=0, label='full season 50%')
                for sid in rng.choice(f.output_type_id.unique(), 6, replace=False):
                    t = f[f.output_type_id == sid].sort_values('date')
                    ax.plot(t.date, t.value, color='C1', lw=.6, alpha=.7)
                ax.plot(x, q[.5], color='C1', lw=1.6, label='full season median')
            x, q = bands(four[four.location == loc])
            ax.fill_between(x, q[.025], q[.975], color='C0', alpha=.35, lw=0, label='4-week 95%')
            ax.plot(x, q[.5], color='C0', lw=1.8, marker='o', ms=2.5, label='4-week median')
            c = o[o.date >= START]
            ax.plot(c.date, c.observation, 'k.-', ms=3, lw=1, label='2026-27 observed')
            top = max(o.observation.max(), q[.975].max())
            ax.set_ylim(0, top * 1.08 if np.isfinite(top) and top > 0 else 1)
            ax.set_xlim(START, pd.Timestamp('2027-06-15'))
            ax.set_title(f"{loc} ({meta.loc[loc, 'state_abb']})", fontsize=10)
            ax.set_ylabel('% ED visits, flu', fontsize=8)
            ax.tick_params(labelsize=7)
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
        for ax in axes.flat[len(order[page:page + 6]):]:
            ax.axis('off')
        axes.flat[0].legend(fontsize=6, ncol=2, loc='upper left')
        fig.tight_layout()
        pdf.savefig(fig); plt.close(fig)
print(out, len(order), 'locations')
