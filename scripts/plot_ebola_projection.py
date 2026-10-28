"""Plot the BDBV projection: reported weekly cases, nowcast of incomplete weeks, 1-4 week forecast.

Writes projection.png (country and three provinces) and projection-all-locations.pdf (every
submitted location, 12 per page: country, provinces, then health zones by total cases).

    .venv/bin/python scripts/plot_ebola_projection.py data/ebola/ensemble-2026-10-31
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HUB = Path('../hubs/BDBV-Modeling-Hub')
BLUE, BAND, INK, MUTED, GRID = '#2a78d6', '#86b6ef', '#0b0b0b', '#52514e', '#e4e3df'
# Other hub submissions for the same round, drawn as dashed medians where they cover a location.
# MOBS-GLEAM_BDBV is the Epistorm model (repo epistorm/EBV2026); it covers the country only.
OTHERS = [('OHTJHU-BM', 'OHTJHU-BM median', '#eb6834'), ('MOBS-GLEAM_BDBV', 'Epistorm (MOBS-GLEAM) median', '#1baf7a'),
          ('CEPH-Rtrend_BDBV', 'CEPH-Rtrend median', '#6250d6')]
PANELS = [('CD', 'DRC (national)'), ('CD-IT', 'Ituri'), ('CD-NK', 'Nord Kivu'), ('CD-HU', 'Haut Uele')]
TODAY = pd.Timestamp('2026-10-27')


def panel(ax, code, title, paths, weeks, locations, latest, other, start='2026-05-01', small=False):
    p = paths[:, :, locations.index(code)]
    rep = latest[latest.location == code].sort_values('week')
    rep = rep[rep.week >= start]
    complete = rep.week < weeks[0]
    ax.plot(rep.week[complete], rep.observation[complete], color=INK, lw=1.2 if small else 1.5, marker='o',
            ms=2 if small else 3, label='Reported (24 Oct release)')
    ax.plot(rep.week[~complete], rep.observation[~complete], color=INK, lw=0, marker='o', ms=3.5 if small else 5,
            mfc='white', label='Reported so far (still incomplete)')
    for lo, hi, a in [(.05, .95, .25), (.25, .75, .45)]:
        ax.fill_between(weeks, np.quantile(p, lo, 0), np.quantile(p, hi, 0), color=BAND, alpha=a, lw=0,
                        label=f'{round(100 * (hi - lo))}% interval')
    ax.plot(weeks, np.median(p, 0), color=BLUE, lw=1.5 if small else 2, label='Median (nowcast, then forecast)')
    for frame, label, color in other:
        if code in set(frame.location):
            o = frame[frame.location == code].groupby('target_end_date').value.median()
            ax.plot(pd.to_datetime(o.index), o.values, color=color, lw=1.2, ls='--', label=label)
    ax.axvline(TODAY, color=MUTED, lw=.8, ls=':')
    ax.set_title(title, loc='left', fontsize=9 if small else 11, color=INK)
    ax.grid(axis='y', color=GRID, lw=.8)
    ax.set_ylim(bottom=0)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=7 if small else 9)


def legend(axes):
    """Handles and labels across all panels of a figure, each label once."""
    seen = {}
    for ax in axes.flat:
        for h, l in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(l, h)
    return list(seen.values()), list(seen)


def main():
    folder = Path(sys.argv[1])
    d = np.load(folder / 'trajectories.npz')
    paths, weeks, locations = d['paths'], pd.to_datetime(d['weeks']), list(d['locations'].astype(str))
    t = pd.read_csv(HUB / 'target-data/time-series.csv')
    latest = t[t.as_of == t.as_of.max()].assign(week=lambda x: pd.to_datetime(x.target_end_date))
    files = [(HUB / f'model-output/{m}/2026-10-31-{m}.csv', label, color) for m, label, color in OTHERS]
    other = [(pd.read_csv(f), label, color) for f, label, color in files if f.exists()]
    heading = 'BDBV weekly confirmed cases: nowcast of weeks ending 26 Sep-24 Oct and forecast to 21 Nov\nACCIDDA_Chromantis'

    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True)
    for ax, (code, title) in zip(axes.flat, PANELS):
        panel(ax, code, title, paths, weeks, locations, latest, other)
    for ax in axes[:, 0]:
        ax.set_ylabel('Confirmed cases per week (symptom onset)', color=MUTED)
    fig.legend(*legend(axes), loc='lower center', ncol=3, frameon=False, fontsize=9)
    fig.suptitle(heading, fontsize=10, x=.01, ha='left')
    fig.tight_layout(rect=(0, .07, 1, 1))
    fig.savefig(folder / 'projection.png', dpi=150)
    plt.close(fig)

    names = pd.read_csv(HUB / 'auxiliary-data/locations.csv').set_index('location')
    level = {'country': 0, 'province': 1, 'health zone': 2}
    cases = latest.groupby('location').observation.sum()
    order = sorted(locations, key=lambda c: (level[names.location_type[c]], -cases.get(c, 0)))
    title = lambda c: (f'{names.location_name[c]} ({c})' if names.location_type[c] != 'health zone'
                       else f'{names.location_name[c]}, {names.parent[c]} ({c})')
    # Two sections, each starting on a new page: the country with its provinces, then health zones.
    sections = [('National and provinces', [c for c in order if names.location_type[c] != 'health zone']),
                ('Health zones', [c for c in order if names.location_type[c] == 'health zone'])]
    with PdfPages(folder / 'projection-all-locations.pdf') as pdf:
        for section, codes in sections:
            pages = -(-len(codes) // 12)
            for page in range(pages):
                chunk = codes[12 * page:12 * page + 12]
                fig, axes = plt.subplots(4, 3, figsize=(11, 14))
                for ax, code in zip(axes.flat, chunk):
                    panel(ax, code, title(code), paths, weeks, locations, latest, other, start='2026-08-01', small=True)
                    ax.set_xlim(pd.Timestamp('2026-07-28'), weeks[-1] + pd.Timedelta(days=4))
                    ax.tick_params(axis='x', labelrotation=45)
                for ax in axes.flat[len(chunk):]:
                    ax.set_visible(False)
                fig.legend(*legend(axes), loc='lower center', ncol=3, frameon=False, fontsize=8)
                fig.suptitle(heading, fontsize=9, x=.01, ha='left')
                label = section if pages == 1 else f'{section} ({page + 1} of {pages})'
                fig.text(.01, .935, label, fontsize=13, fontweight='bold', color=INK, ha='left')
                fig.tight_layout(rect=(0, .04, 1, .925))
                pdf.savefig(fig)
                plt.close(fig)
    print(folder / 'projection.png', folder / 'projection-all-locations.pdf')


if __name__ == '__main__':
    main()
