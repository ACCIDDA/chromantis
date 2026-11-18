"""PDF of the 2026-11-14 MetroCast round: past scores, California admissions, local flu ED forecasts.

Usage: python plot_forecast_pdf.py HUB_DIR NHSN_CA_CSV OUT.pdf
Reads, in this folder: past-scores.csv / past-scores-pairwise.csv (score_past.py), the spliced ED file,
the full-season ED file, and california/2026-11-14-california.parquet. California history is drawn only
from the public Hub target data (July 2026 on); the private CDPH history used for training is not shown.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

hub, nhsn, out = sys.argv[1:4]
REF = pd.Timestamp('2026-11-14')
START = pd.Timestamp('2026-08-01')
truth = pd.read_csv(f'{hub}/target-data/latest-data.csv').assign(date=lambda d: pd.to_datetime(d.target_end_date))
meta = pd.read_csv(f'{hub}/auxiliary-data/locations.csv').drop_duplicates('location').set_index('location')
ed_obs = truth[truth.target == 'Flu ED visits pct']
ca_obs = truth[truth.target == 'Flu hosp admits']
four = pd.read_parquet('spliced/2026-11-14-ACCIDDA-Chromantis.parquet').assign(date=lambda d: pd.to_datetime(d.target_end_date))
full = four
ca = pd.read_parquet('california/2026-11-14-california.parquet').assign(date=lambda d: pd.to_datetime(d.target_end_date))
nhsn = pd.read_csv(nhsn, parse_dates=['date'])
pair = pd.read_csv('past-scores-pairwise.csv', index_col=0).rel_wis
past = pd.read_csv('past-scores.csv')
SEASONS = {'2022-23': 2022, '2023-24': 2023, '2024-25': 2024, '2025-26': 2025}
PAST = dict(zip(SEASONS, ['#c7d3e3', '#9fb3cf', '#6f8db5', '#3f6699']))


def bands(d):
    return d.groupby('date').value.quantile([.025, .1, .25, .5, .75, .9, .975]).unstack()


def draw(ax, f, color, first4, rng, paths=6):
    q = bands(f)
    ax.fill_between(q.index, q[.025], q[.975], color=color, alpha=.13, lw=0, label='95%')
    ax.fill_between(q.index, q[.25], q[.75], color=color, alpha=.3, lw=0, label='50%')
    for sid in rng.choice(f.output_type_id.unique(), paths, replace=False):
        t = f[f.output_type_id == sid].sort_values('date')
        ax.plot(t.date, t.value, color=color, lw=.5, alpha=.6)
    head = q[q.index <= first4]
    ax.plot(q.index, q[.5], color=color, lw=1.2)
    ax.plot(head.index, head[.5], color=color, lw=1.8, marker='o', ms=2.5, label='median')
    return q


def text_page(pdf, title, body):
    fig = plt.figure(figsize=(11, 8.5))
    fig.text(.05, .93, title, fontsize=15, weight='bold')
    fig.text(.05, .87, body, fontsize=9.6, va='top', family='monospace')
    pdf.savefig(fig); plt.close(fig)


rng = np.random.default_rng(0)
with PdfPages(out) as pdf:
    us = past[past.model == 'ACCIDDA-Chromantis']
    text_page(pdf, 'ACCIDDA-Chromantis, Flu MetroCast round of 14 November 2026 (due Thursday 12 Nov)', (
        'DATA. Hub target data of 12 November 2026 (NSSP released a day late after Veterans Day).\n'
        '  Flu ED visits pct: 102 of 103 locations observed through the week ending 7 Nov (one through 31 Oct).\n'
        '  Flu hosp admits (California, 7 locations): unchanged, last week 31 Oct (statewide 755, 1166, 1170 for\n'
        '  17, 24, 31 Oct). Hub horizon -1 is the week ending 7 Nov, not yet published by CDPH.\n'
        '  NHSN California flu admissions (FluSight data, a different but closely matching series: 1181 / 1223 vs\n'
        '  Hub 1166 / 1170 on 24 / 31 Oct) were 1225 for the week ending 7 Nov: flat.\n\n'
        'PAGE 2, HOW WE HAVE BEEN. Our three submitted ED files (24 Oct, 31 Oct, 7 Nov), weeks 0-3 already observed,\n'
        '  scored against the 12 Nov target data. WIS from the 100 trajectories turned into 23 quantiles; pairwise\n'
        '  relative WIS against all MetroCast models (1 = epiENGAGE-baseline, lower is better).\n\n'
        'CALIFORNIA PAGES. Hub target "Flu hosp admits", weekly counts, horizons -1..3 (weeks ending 7 Nov-5 Dec) and\n'
        '  the optional rest of the season. Models: Chromantis MLPs trained on the six CDPH regions plus the statewide\n'
        '  total, Oct 2022 - Jul 2026 (private CDPH history + Hub data), labels = future weekly admissions; reading data\n'
        '  through 31 Oct. Mixture: equal shares of the 9 recipes with the best four-season calibration score (each\n'
        '  season 2022-23..2025-26 held out in turn, mean WIS over the 7 locations at Hub weeks -1..3, <= 58.4),\n'
        '  5 seeds each. The 18 recipes disagree widely on week -1 (statewide medians 573 to 2181), so the mixture\n'
        '  is wide. Submitted: all 32 weeks (to 12 June 2027); from now on the Hub expects California full-season\n'
        '  trajectories every week. History shown = public Hub data only.\n\n'
        'ED PAGES. Hub target "Flu ED visits pct", horizons 0..3 (weeks ending 14 Nov-5 Dec) plus the full season.\n'
        '  Weeks 0-3: 4-week model r010_c08 (5 seeds); later weeks: full_season_finalist_1 (5 seeds), joined by rank\n'
        '  at week 3 as in previous rounds. Both trained on 2022-23 to 2025-26 local ED %, no refit, run on the 12 Nov\n'
        '  data. At the join the full-season model is steeper: median week-4/week-3 ratio 1.9 (1.5 last week).\n'
        '  Blue-grey lines: past seasons shifted onto this calendar by week of season. Black: 2026-27 observed.'))

    fig, axes = plt.subplots(1, 2, figsize=(11, 8.5), gridspec_kw=dict(width_ratios=[1.2, 1]))
    p = pair.sort_values(ascending=False)
    axes[0].barh(p.index, p.values, color=['C1' if 'Chromantis' in m else '0.6' if 'baseline' in m else 'C0' for m in p.index])
    axes[0].axvline(1, color='k', lw=.6)
    for i, v in enumerate(p.values):
        axes[0].text(v + .01, i, f'{v:.3f}', va='center', fontsize=8)
    axes[0].set_title('Pairwise relative WIS, ED files of 24 Oct, 31 Oct, 7 Nov\n(weeks 0-3 observed by 12 Nov; 1 = baseline, lower is better)', fontsize=9)
    axes[0].tick_params(labelsize=8)
    w = past.set_index(['model', 'ref', 'horizon', 'location', 'target_end_date']).wis.unstack('model')[['ACCIDDA-Chromantis', 'epiENGAGE-baseline', 'epiENGAGE-ensemble_short']].dropna()
    r = w.groupby(['ref', 'horizon']).mean()
    tab = pd.DataFrame({'ours / baseline': (r['ACCIDDA-Chromantis'] / r['epiENGAGE-baseline']).round(2),
                        'ensemble / baseline': (r['epiENGAGE-ensemble_short'] / r['epiENGAGE-baseline']).round(2),
                        'tasks': w.groupby(['ref', 'horizon']).size()}).reset_index()
    axes[1].axis('off')
    t = axes[1].table(cellText=tab.values, colLabels=['file (reference date)', 'week', 'ours / baseline', 'ensemble_short / baseline', 'locations'],
                      loc='upper center', cellLoc='center')
    t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.4)
    axes[1].set_title('Mean WIS ratio on the same location-weeks, by file and week\n(lower is better)', fontsize=9)
    fig.tight_layout(); pdf.savefig(fig); plt.close(fig)

    fig, axes = plt.subplots(4, 2, figsize=(11, 11))
    order = ['california'] + sorted(set(ca.location) - {'california'})
    for ax, loc in zip(axes.flat, order):
        o = ca_obs[ca_obs.location == loc]
        draw(ax, ca[ca.location == loc], 'C2', pd.Timestamp('2026-12-05'), rng)
        ax.plot(o.date, o.observation, 'k.-', ms=3, lw=1, label='Hub observed')
        if loc == 'california':
            n = nhsn[nhsn.date >= '2026-07-01']
            ax.plot(n.date, n.value, color='C3', lw=1, ls='--', marker='x', ms=3, label='NHSN CA (not the target)')
        ax.axvline(REF - pd.Timedelta(weeks=1), color='0.5', lw=.5, ls=':')
        ax.set_xlim(pd.Timestamp('2026-07-05'), pd.Timestamp('2027-06-15'))
        ax.set_ylim(0, None)
        ax.set_title(f'{loc}: flu hospital admissions per week', fontsize=9)
        ax.tick_params(labelsize=7)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    axes.flat[0].legend(fontsize=6, ncol=2, loc='upper right')
    axes.flat[-1].axis('off')
    fig.suptitle('California "Flu hosp admits": weeks -1..3 (dots) and rest of season; dotted line = week ending 7 Nov (horizon -1)', fontsize=10)
    fig.tight_layout(); pdf.savefig(fig); plt.close(fig)

    q = ca.groupby(['location', 'date']).value.quantile([.1, .5, .9]).unstack()
    q = q[q.index.get_level_values(1) <= '2026-12-05'].round(0).astype(int)
    last = ca_obs.sort_values('date').groupby('location').observation.last()
    fig = plt.figure(figsize=(11, 8.5)); ax = fig.add_subplot(111); ax.axis('off')
    rows = [[l, d.strftime('%d %b'), int(last[l]), *v] for (l, d), v in zip(q.index, q.values)]
    t = ax.table(cellText=rows, colLabels=['location', 'week ending', 'obs. 31 Oct', '10%', 'median', '90%'], loc='center', cellLoc='center')
    t.auto_set_font_size(False); t.set_fontsize(7); t.scale(1, 1.05)
    ax.set_title('California weekly flu admissions forecast, weeks -1..3 (10% / median / 90% of the 100 trajectories)', fontsize=10)
    pdf.savefig(fig); plt.close(fig)

    locs = sorted(set(four.location), key=lambda l: (meta.loc[l, 'state_abb'], str(meta.loc[l, 'original_location_code']) != 'All', l))
    for page in range(0, len(locs), 6):
        fig, axes = plt.subplots(3, 2, figsize=(11, 8.5))
        for ax, loc in zip(axes.flat, locs[page:page + 6]):
            o = ed_obs[ed_obs.location == loc]
            for name, year in SEASONS.items():
                s = o[(o.date >= f'{year}-08-01') & (o.date < f'{year + 1}-08-01')]
                ax.plot(START + (s.date - pd.Timestamp(f'{year}-08-01')), s.observation, color=PAST[name], lw=1, label=name)
            qq = draw(ax, four[four.location == loc], 'C0', pd.Timestamp('2026-12-05'), rng)
            c = o[o.date >= START]
            ax.plot(c.date, c.observation, 'k.-', ms=3, lw=1, label='2026-27 observed')
            top = max(o.observation.max(), qq[.975].max())
            ax.set_ylim(0, top * 1.08 if np.isfinite(top) and top > 0 else 1)
            ax.set_xlim(START, pd.Timestamp('2027-06-15'))
            ax.set_title(f"{loc} ({meta.loc[loc, 'state_abb']}), % ED visits for flu", fontsize=9)
            ax.tick_params(labelsize=7)
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
        for ax in axes.flat[len(locs[page:page + 6]):]:
            ax.axis('off')
        axes.flat[0].legend(fontsize=6, ncol=2, loc='upper left')
        fig.tight_layout(); pdf.savefig(fig); plt.close(fig)
print(out)
