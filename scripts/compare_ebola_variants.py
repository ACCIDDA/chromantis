"""Compare BDBV forecasts of the same round from several ensemble folders, every location, one PDF.

Each folder is a full ebola_project.py run (same release, same nowcast draws); the folders
differ only in how the 12 neural fits were trained (e.g. --input-noise). Each variant is drawn
as its median and 90% interval; other teams' medians on the hub's main branch for the same
round are thin grey dashed lines.

    .venv/bin/python scripts/compare_ebola_variants.py OUT.pdf data/ebola/ensemble-2026-11-14:"no noise (merged)" \
        data/ebola/ensemble-2026-11-14-noise05:"noise 0.5"
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HUB = Path('../hubs/BDBV-Modeling-Hub')
INK, MUTED, GRID, OTHER = '#0b0b0b', '#52514e', '#e4e3df', '#a3a29d'
COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#6250d6']


def main():
    out, specs = Path(sys.argv[1]), [a.split(':', 1) for a in sys.argv[2:]]
    variants = []
    for (folder, label), color in zip(specs, COLORS):
        d = np.load(Path(folder) / 'trajectories.npz')
        variants.append((label, color, d['paths'], list(d['locations'].astype(str))))
        weeks = pd.to_datetime(d['weeks'])
    settings = json.loads((Path(specs[0][0]) / 'settings.json').read_text())
    reference, today = settings['reference_date'], pd.Timestamp(settings['forecast_date'])
    t = pd.read_csv(HUB / 'target-data/time-series.csv')
    release = t.as_of.max()
    latest = t[t.as_of == release].assign(week=lambda x: pd.to_datetime(x.target_end_date))
    others = []
    for f in sorted((HUB / 'model-output').glob(f'*/{reference}-*.csv')):
        if f.parent.name != 'ACCIDDA-Chromantis':
            o = pd.read_csv(f)
            o = o[o.forecast_date == o.forecast_date.max()]
            others.append(o.assign(model=f.parent.name, week=pd.to_datetime(o.target_end_date, format='mixed', dayfirst=True)))
    other = pd.concat(others).groupby(['model', 'location', 'week']).value.median() if others else None

    def panel(ax, code, title, small):
        rep = latest[(latest.location == code) & (latest.week >= '2026-08-01')].sort_values('week')
        done = rep.week < weeks[0]
        ax.plot(rep.week[done], rep.observation[done], color=INK, lw=1.2, marker='o', ms=2, label=f'Reported ({release} release)')
        ax.plot(rep.week[~done], rep.observation[~done], color=INK, lw=0, marker='o', ms=4, mfc='white',
                label='Reported so far (incomplete)')
        if other is not None:
            for i, (model, o) in enumerate(other.xs(code, level='location').groupby(level='model') if code in
                                           other.index.get_level_values('location') else []):
                ax.plot(o.index.get_level_values('week'), o.values, color=OTHER, lw=.8, ls='--',
                        label='Other teams, median' if i == 0 else None)
        for label, color, paths, locations in variants:
            p = paths[:, :, locations.index(code)]
            ax.fill_between(weeks, np.quantile(p, .05, 0), np.quantile(p, .95, 0), color=color, alpha=.12, lw=0)
            ax.plot(weeks, np.quantile(p, .05, 0), color=color, lw=.6, alpha=.7)
            ax.plot(weeks, np.quantile(p, .95, 0), color=color, lw=.6, alpha=.7, label=f'{label}: 90% interval')
            ax.plot(weeks, np.median(p, 0), color=color, lw=1.6 if small else 2, label=f'{label}: median')
        ax.axvline(today, color=MUTED, lw=.8, ls=':')
        ax.set_title(title, loc='left', fontsize=9 if small else 11, color=INK)
        ax.set_xlim(pd.Timestamp('2026-07-28'), weeks[-1] + pd.Timedelta(days=4))
        ax.grid(axis='y', color=GRID, lw=.8)
        ax.set_ylim(bottom=0)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=7 if small else 9)
        ax.tick_params(axis='x', labelrotation=45)

    def legend(fig, axes, size):
        seen = {}
        for ax in axes.flat:
            for h, l in zip(*ax.get_legend_handles_labels()):
                seen.setdefault(l, h)
        fig.legend(list(seen.values()), list(seen), loc='lower center', ncol=3, frameon=False, fontsize=size)

    fmt = lambda w: f'{w.day} {w:%b}'
    heading = (f'BDBV weekly confirmed cases, ACCIDDA-Chromantis round {reference}: same nowcast of weeks ending '
               f'{fmt(weeks[0])}-{fmt(weeks[weeks <= pd.Timestamp(release)][-1])}, forecasts to {fmt(weeks[-1])}\n'
               'Variants differ only in training: noise s = simulated nowcast error of strength s added to the five '
               'newest input weeks of each training episode (labels unchanged)')
    names = pd.read_csv(HUB / 'auxiliary-data/locations.csv').set_index('location')
    level = {'country': 0, 'province': 1, 'health zone': 2}
    locations = variants[0][3]
    cases = latest.groupby('location').observation.sum()
    order = sorted(locations, key=lambda c: (level[names.location_type[c]], -cases.get(c, 0)))
    title = lambda c: (f'{names.location_name[c]} ({c})' if names.location_type[c] != 'health zone'
                       else f'{names.location_name[c]}, {names.parent[c]} ({c})')

    with PdfPages(out) as pdf:
        # Page 1: national medians per week, each variant, as a table.
        rows = []
        for label, _, paths, locs in variants:
            p = paths[:, :, locs.index('CD')]
            rows.append([label] + [f'{np.median(p[:, j]):.0f} ({np.quantile(p[:, j], .05):.0f}-{np.quantile(p[:, j], .95):.0f})'
                                   for j in range(len(weeks)) if weeks[j] > pd.Timestamp(release)])
        fig, ax = plt.subplots(figsize=(11, 3.2))
        ax.axis('off')
        cols = ['training'] + [f'week ending {fmt(w)}' for w in weeks if w > pd.Timestamp(release)]
        tb = ax.table(cellText=rows, colLabels=cols, loc='center', cellLoc='center')
        tb.auto_set_font_size(False)
        tb.set_fontsize(9)
        tb.scale(1, 1.8)
        ax.set_title('DRC national forecast: median (90% interval), confirmed cases per week by symptom onset',
                     loc='left', fontsize=11)
        fig.suptitle(heading, fontsize=8, x=.01, ha='left')
        pdf.savefig(fig)
        plt.close(fig)
        for section, codes in [('National and provinces', [c for c in order if names.location_type[c] != 'health zone']),
                               ('Health zones', [c for c in order if names.location_type[c] == 'health zone'])]:
            pages = -(-len(codes) // 12)
            for page in range(pages):
                chunk = codes[12 * page:12 * page + 12]
                fig, axes = plt.subplots(4, 3, figsize=(11, 14))
                for ax, code in zip(axes.flat, chunk):
                    panel(ax, code, title(code), small=True)
                for ax in axes.flat[len(chunk):]:
                    ax.set_visible(False)
                legend(fig, axes, 8)
                fig.suptitle(heading, fontsize=8, x=.01, ha='left')
                fig.text(.01, .935, section if pages == 1 else f'{section} ({page + 1} of {pages})', fontsize=13,
                         fontweight='bold', color=INK, ha='left')
                fig.tight_layout(rect=(0, .05, 1, .925))
                pdf.savefig(fig)
                plt.close(fig)
    print(out)


if __name__ == '__main__':
    main()
