"""Input and output tensor shapes of the weekly flu model, drawn from the real 21 October 2026 issuance.

Input: the operational episode (`input_mode='reported'`, lookback 12, flu admissions + flu ED, Kinsa) that the
production fits receive, before the correction trees. Output: the submitted 24 October medians.
Values are shaded per location (log(1 + admissions), ED share), scaled to the location's maximum over the
12 input and 4 output weeks. Kinsa is copied across locations from its national series. The calendar is shown once per episode;
the network broadcasts it to every location. Availability is black (1, observed); missing cells carry red crosses. Green outlines mark the
two newest history weeks whose observed values are updated before scaling. The displayed input
values are the reports before those updates. Purple outlines connect one location/target slice
to its schematic encoder features and submitted median. Feature-vector cells are schematic.
The schematic shows the two history MLPs and latent noise entering the sampled decoder;
direct-quantile decoders use no noise. Shapes retain the episode axis on both inputs and outputs.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np
import pandas as pd

from chromantis.data.geography import STATE_FIPS
from chromantis.dataset.build import load, for_hub
from chromantis.dataset.episodes import calendar, episodes
from chromantis.problem import Problem

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/chromantis-manuscript/figures'
PANEL = ROOT / 'data/operational-20261021/processed/panel.npz'
SUBMISSION = ROOT / 'production/submissions/2026-10-24/2026-10-24-ACCIDDA-Chromantis.csv'
ISSUANCE = '2026-10-21'
INK, BLUE = '#202c35', '#28698a'
RED, GREEN, OWN, CONTEXT = '#ce3434', '#238345', '#8852a3', '#a16d20'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
                     'text.color': INK, 'axes.edgecolor': INK, 'axes.labelcolor': INK,
                     'savefig.facecolor': 'white'})
VALUES = plt.get_cmap('Blues').copy()
VALUES.set_bad('white')
MASK = matplotlib.colors.ListedColormap(['white', 'black'])


def inputs():
    problem = Problem.load(ROOT / 'problems/us-flu-production.json')
    panel = for_hub(load(PANEL), 'flusight')
    names = problem.input_names('target')
    eps = [e for e in episodes(panel, problem, names, 12, 'reported', problem.covariate_names('kinsa'),
                               horizons=problem.horizons, require_labels=False) if e['issuance'] == ISSUANCE]
    return eps[0]


def outputs(locations):
    d = pd.read_csv(SUBMISSION, dtype={'location': str})
    d = d[d.target.isin(['wk inc flu hosp', 'wk inc flu prop ed visits'])]
    d['abbr'] = d.location.map(lambda f: STATE_FIPS.get(f, f))
    q = d.pivot_table(index=['target', 'abbr', 'horizon'], columns='output_type_id', values='value')
    q.columns = q.columns.astype(float)
    shape = (4, 2, len(locations))
    result = {p: np.full(shape, np.nan) for p in (.5,)}
    for c, target in enumerate(['wk inc flu hosp', 'wk inc flu prop ed visits']):
        for j, loc in enumerate(locations):
            for h in range(4):
                if (target, loc, h) in q.index:
                    for p in result:
                        result[p][h, c, j] = q.loc[(target, loc, h), p]
    return result


def grid(ax, x, y, array, cmap, cell, vmin=0, vmax=1):
    """array [rows=locations, cols=weeks], first location on top."""
    rows, cols = array.shape
    ax.imshow(np.ma.masked_invalid(array), cmap=cmap, vmin=vmin, vmax=vmax, interpolation='nearest',
              extent=(x, x+cols*cell[0], y, y+rows*cell[1]), aspect='auto', zorder=1)
    ax.add_patch(Rectangle((x, y), cols*cell[0], rows*cell[1], fill=False, lw=.6, ec=INK, zorder=2))


def main():
    e = inputs()
    locations = list(e['locations'])
    out = outputs(locations)
    values = np.where(e['available'], e['values'], np.nan)  # [12, 2, L]
    available = e['available'].astype(float)
    scale = lambda v, c: np.log1p(v) if c == 0 else v
    shade = np.full((16, 2, len(locations)), np.nan)
    for c in range(2):
        both = np.concatenate([scale(values[:, c], c), scale(out[.5][:, c], c)])  # [16, L]
        shade[:, c] = both / np.nanmax(both, axis=0, keepdims=True)

    kinsa = e['covariates'][:, 0]  # [12, 2 fields, L]; national, identical in every location
    kinsa_shade = kinsa[:, 0] / kinsa[:, 0].max()
    cal = calendar([e['context_dates'][-1]])[0]  # sin, cos of annual phase; weeks to Christmas / 26

    fig = plt.figure(figsize=(14.8, 7.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 204), ylim=(0, 100))
    ax.axis('off')
    n = len(locations)
    w, h = .60, .98
    top, bottom = 82, 82 - n*h
    selected = locations.index('NC')
    selected_y = top - (selected+1)*h
    rows = lambda a: a.T
    text = lambda x, y, s, **kw: ax.text(x, y, s, ha=kw.pop('ha', 'center'),
                                        va=kw.pop('va', 'center'), **kw)

    def arrow(a, b, **kw):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=10,
                                     lw=.9, color=kw.pop('color', INK), zorder=5, **kw))

    def outline(x, y, width, height, color, lw=1.3):
        ax.add_patch(Rectangle((x, y), width, height, fill=False, ec=color, lw=lw, zorder=6))

    def box(x, y, width, height, label, size=8):
        ax.add_patch(Rectangle((x, y), width, height, fc='#e6f0f5', ec=BLUE, lw=.8))
        text(x+width/2, y+height/2, label, fontsize=size)

    def missing(x, y, mask, cell):
        # imshow places the first location at the top of each grid.
        loc, week = np.nonzero(~mask.T.astype(bool))
        ax.scatter(x+(week+.5)*cell[0], y+(n-loc-.5)*cell[1],
                   marker='x', s=7, linewidths=.65, color=RED, zorder=7)

    def vector(x, y, label, shape, color):
        # A schematic d-feature vector; these cells do not encode fitted activations.
        for j in range(7):
            ax.add_patch(Rectangle((x+3*j, y), 3, 3, fc='#f2f4f5', ec='#b9c1c6', lw=.45))
        outline(x, y, 21, 3, color)
        text(x+10.5, y-3, label, fontsize=7, color=color)
        text(x+10.5, y-6, shape, fontsize=6.7)

    text(3, 96, 'A  Inputs', ha='left', fontsize=11, weight='bold')
    text(68, 96, 'B  Scaling, history encoders and decoder', ha='left', fontsize=11, weight='bold')
    text(165, 96, 'C  Output', ha='left', fontsize=11, weight='bold')
    text(3, 90, 'History x  [N, 12, 2 signals, 2 fields, 52]', ha='left', fontsize=8)
    blocks = [('Flu admissions', 5.5, shade[:12, 0], available[:, 0]),
              ('Flu ED share', 25, shade[:12, 1], available[:, 1]),
              ('Kinsa (optional)', 44.5, kinsa_shade, kinsa[:, 1])]
    for i, (title, x, value, mask) in enumerate(blocks):
        grid(ax, x, bottom, rows(value), VALUES, (w, h))
        mask_x = x+12*w+1
        grid(ax, mask_x, bottom, rows(mask), MASK, (w, h))
        missing(x, bottom, mask, (w, h))
        missing(mask_x, bottom, mask, (w, h))
        center = x+12*w+.5
        text(center, top+5.5, title, fontsize=8, weight='bold')
        for x0, label in ((x, 'value'), (mask_x, 'available')):
            text(x0+6*w, top+2, label, fontsize=6.5)
        shape = '[N, 12, 2 fields, 52]' if i < 2 else '[N, 12, 1, 2 fields, 52]'
        text(center, bottom-3, shape, fontsize=6.5)
        if i < 2:
            # Trees revise observed values in the two newest weeks; masks stay unchanged.
            outline(x+10*w, bottom, 2*w, n*h, GREEN)
            label_x = x+11*w
            text(label_x, bottom-9, 'Updated', fontsize=8, color=GREEN, weight='bold')
            arrow((label_x, bottom-7), (label_x, bottom-.3), color=GREEN)
            text(label_x, bottom-12.5, '2 newest weeks', fontsize=6.5, color=GREEN)
        if i == 0:
            outline(x, selected_y, 24*w+1, h, OWN, lw=1.5)
            text(x-.6, selected_y+h/2, 'NC', ha='right', fontsize=6, color=OWN, weight='bold')
    text(1.4, (top+bottom)/2, '52 locations', rotation=90, fontsize=7)
    text(52, bottom-8, '12 history weeks →', fontsize=7)

    # Calendar bypasses value scaling and is broadcast inside the context encoder.
    grid(ax, 45.5, 15, cal[None], VALUES, (2.3, 2.3), vmin=-1, vmax=1)
    text(44.5, 16.2, 'Calendar [N, 3]', ha='right', fontsize=7)
    text(49, 12, 'sin, cos, Christmas', fontsize=6.5)

    box(68, 39, 20, 43, 'Scaling\nafter updates\n\nTransform values\nSubtract offset\nDivide by scale\n\nTraining statistics,\nper signal / location\n\nMissing values → 0\nKeep availability', size=7.2)
    arrow((61, 61), (67.5, 61))
    arrow((88, 75), (93.5, 75))
    arrow((88, 50), (93.5, 50))

    # Both encoders run per location. The own-target MLP also runs per target.
    text(107.5, 87, 'Each location, each target', fontsize=7.5, weight='bold')
    box(94, 70, 27, 10, 'Own-target MLP\n24 → d → d')
    text(107.5, 83, 'Weights shared across locations and targets', fontsize=6.7)
    arrow((107.5, 70), (107.5, 67.5))
    vector(97, 64, 'Own-target v[l, c]  [d]', '[N, 52, 2 targets, d]', OWN)

    box(94, 45, 27, 11, 'Context MLP, per location\nAll signals + enabled context\nFlatten → d → d', size=7.2)
    text(107.5, 43, 'Weights shared across locations', fontsize=6.7)
    arrow((107.5, 41.5), (107.5, 39.5))
    vector(97, 36, 'Context u[l]  [d]', '[N, 52, d]', CONTEXT)
    ax.plot([53, 91, 91], [16.2, 16.2, 48], color=INK, lw=.8)
    arrow((91, 48), (93.5, 48))
    text(107.5, 23, 'Optional spatial exchange\nafter the context encoder', fontsize=6.7, color='#555')
    text(107.5, 14, 'Outlined feature vectors\nare schematic d-value slices', fontsize=6.7, color='#555')

    box(129, 51, 27, 16, 'Add own-target + context\n+ target / horizon embeddings\nthen normalize', size=7.4)
    arrow((118, 65.5), (128.5, 62))
    arrow((118, 37.5), (128.5, 55))
    text(142.5, 71, '[N, 4, 52, 2, d]', fontsize=7)
    box(129, 31, 27, 12, 'Decoder MLP\n+ link to native units')
    arrow((142.5, 51), (142.5, 43.5))
    text(142.5, 20, 'Noise z ~ Normal(0, I)\n[M, N, latent width]', fontsize=7, color=BLUE)
    arrow((142.5, 24), (142.5, 30.5), color=BLUE)
    text(142.5, 11, 'Scale / shift inside sampled decoder\nDirect quantiles: no noise', fontsize=6.5, color=BLUE)

    # Each target's decoder output is explicit; submitted medians illustrate its units.
    text(182, 90, '[M, N, 4 weeks, 2 targets, 52]', fontsize=8)
    ow = 1.65
    for x, c, title in [(166, 0, 'Admissions'), (186, 1, 'ED share')]:
        for k in (2, 1):
            ax.add_patch(Rectangle((x+k*.8, bottom+k*.8), 4*ow, n*h,
                                   fc='white', ec='#999', lw=.5))
        grid(ax, x, bottom, rows(shade[12:, c]), VALUES, (ow, h))
        missing(x, bottom, np.isfinite(out[.5][:, c]), (ow, h))
        text(x+2*ow, top+5.5, title, fontsize=8, weight='bold')
        text(x+2*ow, top+2, 'submitted median', fontsize=6.5)
        text(x+2*ow, bottom-3, '[M, N, 4, 52]', fontsize=6.5)
        if c == 0:
            outline(x, selected_y, 4*ow, h, OWN, lw=1.5)
            text(x+4*ow+.8, selected_y+h/2, 'NC', ha='left', fontsize=6, color=OWN, weight='bold')
    ax.plot([156, 161, 161], [37, 37, 56], color=INK, lw=.9)
    arrow((161, 56), (165.5, 56))
    text(181, bottom-8, '4 prediction weeks →', fontsize=7)
    text(181, 17, 'M = sampled paths\nor direct quantiles', fontsize=7)

    text(5.5, 7.5, 'Red cross: missing; black: available. Purple outlines: NC admissions and its feature/output slice. '
                       'N: episodes; d: hidden width.', ha='left', fontsize=7, color='#555')
    text(5.5, 3.5, 'Grids show reports before updates. Blue shading is for display only: relative values per location; '
                       'calendar on [-1, 1]. Model scaling uses training data.', ha='left', fontsize=7, color='#555')

    OUT.mkdir(parents=True, exist_ok=True)
    for extension in ('svg', 'pdf'):
        fig.savefig(OUT / f'shapes.{extension}')
    plt.close(fig)


if __name__ == '__main__':
    main()
