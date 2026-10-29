"""Draw the package documentation figures from saved data and schematic diagrams."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/figures/chromantis'
INK, BLUE, PALE, GRAY, GOLD = '#202c35', '#28698a', '#e6f0f5', '#edf0f2', '#f0deac'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'svg.fonttype': 'none', 'pdf.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.labelcolor': INK, 'text.color': INK, 'axes.edgecolor': INK,
                     'savefig.facecolor': 'white'})


def canvas(height):
    fig, ax = plt.subplots(figsize=(7.2, height))
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    fig.subplots_adjust(left=.015, right=.985, top=.98, bottom=.02)
    return fig, ax


def text(ax, x, y, label, size=10, bold=False, **kw):
    ax.text(x, y, label, fontsize=size, weight='bold' if bold else 'normal',
            ha=kw.pop('ha', 'center'), va='center', **kw)


def box(ax, x, y, w, h, label='', fill='white', dashed=False, size=10):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=BLUE if fill == PALE else INK,
                           linewidth=.8, linestyle='--' if dashed else '-'))
    if label:
        text(ax, x+w/2, y+h/2, label, size)


def arrow(ax, a, b, **kw):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=10,
                                 linewidth=.85, color=INK, **kw))


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f'{name}.svg')
    plt.close(fig)


def information():
    fig, ax = canvas(3.7)
    text(ax, .015, .95, 'A  An observed zero is different from a missing report', 11, True, ha='left')
    x, w = .33, .205
    for i, label in enumerate(['Observed', 'Observed zero', 'Missing']):
        text(ax, x+(i+.5)*w, .83, label, 10)
    for y, label, values in [(.67, 'Value', ['12', '0', '0*']),
                            (.55, 'Available? (1 / 0)', ['1', '1', '0'])]:
        text(ax, .03, y+.055, label, 10, ha='left')
        for i, value in enumerate(values):
            box(ax, x+i*w, y, w, .11, value, GRAY if i == 2 else 'white', size=11)
    text(ax, .33, .495, '* Missing values use a zero placeholder after preprocessing.', 8.3, ha='left')
    text(ax, .015, .40, 'B  Adjust the recent past, then predict the weeks ahead', 11, True, ha='left')
    left, cw = .14, .138
    dates = ['10 Oct', '17 Oct', '24 Oct', '31 Oct', '7 Nov', '14 Nov']
    labels = ['Adjust\nreport', 'Adjust\nreport', 'Nowcast', 'Forecast\n+1 week',
              'Forecast\n+2 weeks', 'Forecast\n+3 weeks']
    for i, (day, label) in enumerate(zip(dates, labels)):
        text(ax, left+(i+.5)*cw, .24, day, 9.5)
        box(ax, left+i*cw, .065, cw, .14, label,
            PALE if i < 2 else GOLD if i == 2 else 'white', size=9)
    text(ax, .015, .24, 'Week\nending', 9, ha='left')
    boundary = left+2*cw
    ax.plot([boundary, boundary], [.045, .30], color=INK, linestyle=':', linewidth=1)
    text(ax, boundary, .325, 'Issued 21 Oct 2026', 9)
    save(fig, 'information')


def network():
    fig, ax = canvas(4.8)
    text(ax, .03, .97, 'From a reported history to a forecast', 12, True, ha='left')
    text(ax, .03, .91, 'One signal at one location; each column is one history week', 9, ha='left')
    start, cw = .35, .12
    for y, label, vals in [(.80, 'Value', ['x', '0', 'x', '0']),
                          (.71, 'Available? (1 / 0)', ['1', '0', '1', '1'])]:
        text(ax, .04, y+.04, label, 10, ha='left')
        for i, val in enumerate(vals):
            box(ax, start+i*cw, y, cw, .08, val, GRAY if i == 1 else 'white')
    text(ax, .53, .675, 'Missing', 8, color='#555')
    text(ax, .77, .675, 'Observed zero', 8, color='#555')
    box(ax, .04, .51, .38, .105, 'Encode the target history', size=10)
    box(ax, .58, .51, .38, .105, 'Encode all signals + context', size=10)
    arrow(ax, (.53, .70), (.23, .62))
    arrow(ax, (.65, .70), (.77, .62))
    box(ax, .58, .35, .38, .095, 'Optional: add nearby-state context', dashed=True, size=9)
    arrow(ax, (.77, .51), (.77, .45))
    box(ax, .08, .18, .84, .105,
        'Combine histories + target + forecast week; normalize', fill=PALE, size=10)
    arrow(ax, (.23, .51), (.23, .29))
    arrow(ax, (.77, .35), (.77, .29))
    box(ax, .22, .025, .56, .095, 'Predict samples or ordered quantiles', size=10)
    arrow(ax, (.50, .18), (.50, .125))
    save(fig, 'network')


def decoders():
    fig, ax = canvas(3.65)
    cols = [(.015, 'A  Basic sampled'), (.355, 'B  Residual sampled'), (.695, 'C  Direct quantiles')]
    for x, label in cols:
        text(ax, x, .96, label, 10.5, True, ha='left')
    for x, _ in cols:
        text(ax, x+.14, .84, 'History features', 9.5)
    box(ax, .015, .62, .275, .12, 'Noise sets scale / shift', PALE)
    box(ax, .015, .37, .275, .12, 'MLP readout')
    arrow(ax, (.1525, .80), (.1525, .745))
    text(ax, .32, .68, '$z$', 11, color=BLUE)
    arrow(ax, (.309, .68), (.292, .68))
    arrow(ax, (.1525, .62), (.1525, .495))
    box(ax, .345, .32, .295, .45, dashed=True)
    box(ax, .375, .61, .23, .10, 'Normalize')
    box(ax, .375, .47, .23, .10, 'Noise sets scale / shift', PALE)
    box(ax, .375, .33, .23, .10, 'MLP + skip')
    arrow(ax, (.49, .80), (.49, .715))
    arrow(ax, (.49, .61), (.49, .575))
    text(ax, .668, .52, '$z$', 11, color=BLUE)
    arrow(ax, (.655, .52), (.609, .52))
    arrow(ax, (.49, .47), (.49, .435))
    text(ax, .595, .745, 'Repeat', 9)
    box(ax, .375, .20, .23, .085, 'Linear readout', size=9)
    arrow(ax, (.49, .32), (.49, .29))
    box(ax, .695, .62, .285, .12, 'MLP: 23 outputs')
    box(ax, .695, .37, .285, .12, 'Median + positive gaps')
    arrow(ax, (.8375, .80), (.8375, .745))
    arrow(ax, (.8375, .62), (.8375, .495))
    box(ax, .12, .035, .76, .105, 'Add the latest-value anchor; restore admission counts or ED share', fill=GRAY)
    for x, y in [(.1525, .37), (.49, .20), (.8375, .37)]:
        arrow(ax, (x, y), (x, .145))
    save(fig, 'decoders')


def forecast():
    from chromantis.dataset.build import load, for_hub
    panel = for_hub(load(ROOT / 'data/operational-20261021/processed/panel.npz'), 'flusight')
    issue = list(map(str, panel['issuance_dates'])).index('2026-10-21')
    loc = list(map(str, panel['locations'])).index('NC')
    dates = pd.to_datetime(panel['dates'])
    use = (dates >= '2026-08-01') & (dates <= '2026-10-17')
    names = list(map(str, panel['target_names']))
    submitted = pd.read_csv(ROOT / 'production/submissions/2026-10-24/2026-10-24-ACCIDDA-Chromantis.csv',
                            dtype={'location': str})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharex=True)
    for ax, source, target, title, unit, factor in zip(
            axes, ['nhsn_flu_admissions', 'nssp_flu_proportion'],
            ['wk inc flu hosp', 'wk inc flu prop ed visits'],
            ['A  Flu admissions', 'B  Flu ED share'], ['Admissions / week', 'Percent of ED visits'], [1, 100]):
        history = panel['asof_targets'][issue, use, loc, names.index(source)] * factor
        rows = submitted[(submitted.location == '37') & (submitted.target == target) &
                         (submitted.output_type == 'quantile')]
        q = rows.pivot(index='target_end_date', columns='output_type_id', values='value') * factor
        q.columns = q.columns.astype(float)
        q.index = pd.to_datetime(q.index)
        ax.plot(dates[use], history, '.-', color=INK, markersize=3.5, linewidth=1, label='Reports at issuance')
        ax.fill_between(q.index, q[.025], q[.975], color=BLUE, alpha=.14, linewidth=0, label='95% interval')
        ax.fill_between(q.index, q[.25], q[.75], color=BLUE, alpha=.30, linewidth=0, label='50% interval')
        ax.plot(q.index, q[.5], '.-', color=BLUE, markersize=4, linewidth=1.4, label='Forecast median')
        ax.axvline(pd.Timestamp('2026-10-21'), color=INK, linestyle=':', linewidth=.8)
        ax.set_title(title, fontsize=10, loc='left', weight='bold')
        ax.set_ylabel(unit, fontsize=9)
        ax.set_ylim(bottom=0)
        ax.set_xticks(pd.to_datetime(['2026-08-01','2026-09-05','2026-10-03','2026-11-07']),
                      ['1 Aug','5 Sep','3 Oct','7 Nov'])
        ax.tick_params(labelsize=8)
        ax.yaxis.grid(True, linewidth=.4, color='#dddddd')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=2, loc='lower center', frameon=False, fontsize=8.5,
               bbox_to_anchor=(.5, .005), handlelength=1.6)
    fig.subplots_adjust(left=.095, right=.99, top=.90, bottom=.27, wspace=.32)
    save(fig, 'forecast')


def fitting():
    """Vector workflow: reference US flu data and CV roles, with schematic search/loss curves."""
    import json
    from chromantis.dataset.cv import week_roles, season_start
    from chromantis.model.scenario import Scenario
    from chromantis.problem import Problem

    study = json.loads((ROOT / 'experiments/tree-20261010/round-01.json').read_text())
    scenario = Scenario.from_string(study['candidates']['B_width256'])
    problem = Problem.load(ROOT / 'problems/us-flu-short-term-prescribed.json')
    colors = dict(fit='#dbe9f1', validation='#f3d288', score='#eab2af')
    green = '#298051'
    fig, ax = canvas(8.1)
    fig.set_figwidth(11.8)
    text(ax, .015, .973, 'Fitting and evaluating a model', 15, True, ha='left')
    text(ax, .015, .937, 'Influenza example: a width-256 quantile MLP, with 12 weeks of admissions and ED history',
         10, ha='left')

    # A branching proposal history, followed by measured evaluation and feedback.
    text(ax, .015, .879, 'A  LLM proposes configuration changes', 11, True, ha='left')
    box(ax, .02, .775, .325, .070, 'Fixed data, input policy, labels,\nseason folds and primary score', fill=GRAY, size=9)
    arrow(ax, (.1825, .775), (.1825, .751))
    box(ax, .095, .685, .175, .065, 'Starting configuration\nWidth-256 quantile MLP', size=9)
    children = [(.016, 'Reporting errors\n× 1.5 in training'), (.129, 'Learning rate\n× 2'), (.242, 'Calendar inputs\noff')]
    for x, label in children:
        arrow(ax, (.1825, .685), (x+.051, .651))
        box(ax, x, .586, .102, .064, label, size=8)
    arrow(ax, (.067, .586), (.067, .558))
    box(ax, .016, .492, .102, .065, 'Then try\nwidth 512', size=8)
    text(ax, .14, .53, 'Example branches from the flu search.\nEach node is a newly fitted recipe;\nno branch scores are drawn here.', 8.2, ha='left')

    box(ax, .025, .373, .31, .070, 'Code fits every candidate and seed;\nevaluates the same tasks and labels', fill=PALE, size=9)
    arrow(ax, (.183, .485), (.183, .447))
    box(ax, .025, .270, .31, .073, 'Code ranks by log-admission WIS; lower is better.\nRepeat seeds before continuing a branch.\nThe flu search required ≥4 seeds before expansion.', size=8.3)
    arrow(ax, (.183, .373), (.183, .347))
    ax.plot([.025, .006, .006, .095], [.3065, .3065, .7175, .7175], lw=.8, color=green)
    arrow(ax, (.07, .7175), (.094, .7175))
    text(ax, .017, .225, 'LLM uses measured scores to propose the next round.\nRepeated selection on the same seasons is not an untouched test.', 8.3, ha='left')

    # The black curve is reference US admissions, not artificially perturbed inputs.
    # Read only the required arrays; loading the report-vintage tensors is unnecessary.
    with np.load(ROOT / problem.panel, allow_pickle=False) as panel:
        us = list(panel['locations'].astype(str)).index('US')
        flu = list(panel['target_names'].astype(str)).index('nhsn_flu_admissions')
        admissions = pd.Series(panel['targets'][:, us, flu], index=pd.to_datetime(panel['dates']))

    # Recreate the CV layout with the exact role function used for fitting.
    text(ax, .395, .879, 'B  Cross-validation by season', 11, True, ha='left')
    text(ax, .395, .851, 'Black: reference US flu admissions/week; common scale 0-60,000.', 8.5, ha='left')
    left, width = .51, .112
    for j, season in enumerate(problem.training_folds):
        text(ax, left+(j+.5)*width, .826, season.replace('2022-2023', '2022-23').replace('2023-2024', '2023-24')
             .replace('2024-2025', '2024-25').replace('2025-2026', '2025-26'), 8.8)
    for i, held in enumerate(problem.folds):
        y, height = .750-i*.065, .052
        text(ax, .395, y+height/2, 'Evaluate\n'+held[:4]+'-'+held[-2:], 8.6, ha='left')
        text(ax, left-.008, y+height-.003, '60k', 5.8, ha='right')
        text(ax, left-.008, y+.003, '0', 5.8, ha='right')
        for j, season in enumerate(problem.training_folds):
            year = int(season[:4])
            dates = pd.date_range(pd.Timestamp(season_start(year))+pd.Timedelta(days=6),
                                  pd.Timestamp(season_start(year+1)), freq='7D').values.astype('datetime64[D]')
            roles = week_roles(dates, problem, scenario, held)
            cw = width/len(roles)
            for k, role in enumerate(roles):
                ax.add_patch(Rectangle((left+j*width+k*cw, y), cw, height,
                                       fc=colors[role], ec='none'))
            counts = admissions.reindex(pd.to_datetime(dates)).to_numpy()
            x = left+j*width+(np.arange(len(dates))+.5)*cw
            ax.plot(x, y+.003+(height-.006)*counts/60000, color='black', lw=.8, zorder=3)
            box(ax, left+j*width, y, width, height)
            # The outline must not cover the role colors or reference-data curve.
            ax.patches[-1].set_facecolor('none')
    for x, role, label in [(.40, 'fit', 'Inner fitting weeks'), (.59, 'validation', 'Early-stopping labels'),
                            (.80, 'score', 'Outer evaluation season')]:
        ax.add_patch(Rectangle((x, .602), .013, .013, fc=colors[role], ec=INK, lw=.4))
        text(ax, x+.019, .6085, label, 8.2, ha='left')
    text(ax, .395, .565, 'Yellow: hide 3 weeks in every 16, starting after the first 4 weeks of each training season.\n'
         'Those weeks are absent from inner-fit inputs, labels and scaling statistics.\n'
         'After epoch selection, refit on all blue + yellow weeks. Red weeks supply no fitting labels.',
         8.6, ha='left')
    text(ax, .395, .498, 'This is retrospective CV: a fit may use seasons later than its evaluation season.',
         8.6, ha='left', color='#555')

    # The loss curve is illustrative, with no fabricated empirical scores or epochs.
    text(ax, .395, .450, 'C  Inside one fold: select the epoch, then fit a fresh model', 11, True, ha='left')
    curve = fig.add_axes([.405, .285, .225, .135])
    epoch = np.linspace(0, 1, 180)
    training_loss = .20+.65*np.exp(-4*epoch)
    validation_loss = .33+.48*np.exp(-7*epoch)+.37*epoch**2
    best = np.argmin(validation_loss)
    stop = best+40
    curve.plot(epoch, training_loss, color=BLUE, lw=1.2)
    curve.plot(epoch[:stop+1], validation_loss[:stop+1], color='#b67d21', lw=1.4)
    curve.axvline(epoch[best], color=INK, lw=.8, ls=':')
    curve.plot(epoch[best], validation_loss[best], 'o', ms=3, color='#b67d21')
    curve.annotate('best epoch', (epoch[best], validation_loss[best]), xytext=(.04, .40),
                   textcoords='axes fraction', fontsize=8, arrowprops=dict(arrowstyle='->', lw=.7))
    curve.annotate('stop after patience', (epoch[stop], validation_loss[stop]), xytext=(.48, .82),
                   textcoords='axes fraction', fontsize=7.6, arrowprops=dict(arrowstyle='->', lw=.7))
    curve.set(xlim=(0, 1), ylim=(.16, .9), xticks=[], yticks=[])
    curve.set_xlabel('Epoch (schematic)', fontsize=8, labelpad=2)
    curve.set_ylabel('Loss', fontsize=8, labelpad=2)
    text(ax, .40, .249, 'Blue: training; gold: validation.\nCurves are illustrative, not run results.', 7.6, ha='left')
    box(ax, .675, .333, .285, .073, 'Fresh initialization\nRefit all permitted seasons\nfor the selected epoch count', fill=PALE, size=9)
    arrow(ax, (.638, .370), (.670, .370))
    box(ax, .675, .224, .285, .073, 'Freeze fit; predict held-out season.\nScore against its reference labels.\nDo this separately for all three folds.', size=9)
    arrow(ax, (.8175, .333), (.8175, .301))
    text(ax, .395, .204, f'Example patience: {scenario.patience} epochs without improvement; cap: {scenario.epochs} epochs.',
         8, ha='left')

    # Release fitting uses all completed seasons rather than any of the CV checkpoints.
    box(ax, .02, .137, .94, .042,
        'Researcher selects recipes → fresh release fits on 2022-23 through 2025-26 → freeze checkpoints → weekly inputs, no refitting',
        fill=GRAY, size=9)
    text(ax, .02, .105,
         'Training inputs: reference flu admissions / ED histories, perturbed with prescribed 2025-26 reporting errors; '
         'tree children change the stated settings.', 8.2, ha='left')
    text(ax, .02, .079,
         'Prediction labels: September 2026 reference future admissions / ED, plus 4 recent reference weeks for '
         'auxiliary reconstruction in the quantile parent.', 8.2, ha='left')
    text(ax, .02, .053,
         'Evaluation inputs: 3 shared artificial preliminary histories per task from that reporting process; '
         'each saved fit updates the newest 2 weeks before forecasting.', 8.2, ha='left')
    text(ax, .02, .027,
         'Each CV row fits on the other three completed seasons and scores its red season. '
         'The LLM proposes recipes; numerical losses and WIS come from code.', 8.2, ha='left')
    save(fig, 'fitting')


def llm_search():
    """Compact, schematic recipe search; numerical scores are computed by code."""
    fig, ax = canvas(3.5)
    fig.set_figwidth(6.4)
    text(ax, .5, .964, 'Searching model configurations', 12, True)
    text(ax, .5, .906, 'Researcher fixes data, prediction labels, splits and score', 8.8)
    box(ax, .35, .72, .30, .13, 'Current configuration', fill=PALE, size=10)
    for x, label in [(.045, 'Change\nmodel width'), (.355, 'Change\nlearning rate'),
                     (.665, 'Change\ntraining inputs')]:
        arrow(ax, (.50, .72), (x+.14, .615))
        box(ax, x, .49, .28, .12, label, size=9)
        ax.plot([x+.14, x+.14], [.49, .435], color=INK, lw=.8)
    ax.plot([.185, .805], [.435, .435], color=INK, lw=.8)
    arrow(ax, (.5, .435), (.5, .405))
    box(ax, .15, .26, .70, .14, 'Code refits and scores every candidate\nSame evaluation tasks; repeated seeds', fill=GRAY, size=9.5)
    arrow(ax, (.5, .26), (.5, .19))
    box(ax, .12, .05, .76, .135, 'LLM uses measured scores to suggest the next round\nRepeat candidates with new seeds before continuing', fill=PALE, size=9.2)
    ax.plot([.88, .975, .975, .69], [.1175, .1175, .785, .785], color=BLUE, lw=1)
    ax.add_patch(FancyArrowPatch((.69, .785), (.653, .785), arrowstyle='-|>',
                                 mutation_scale=10, lw=1, color=BLUE))
    text(ax, .958, .67, 'Next round', 7.8, rotation=90, color=BLUE)
    save(fig, 'llm-search')


def sampled_blocks():
    """Building blocks of the flu width-96, Kinsa, three-block sampled recipe."""
    fig, ax = canvas(6.0)
    fig.set_figwidth(8.2)
    text(ax, .02, .967, 'Sampled forecasting model: building blocks', 13, True, ha='left')
    text(ax, .02, .929, 'Flu example: width 96, Kinsa summaries, three residual decoder blocks', 9.5, ha='left')

    # Both encoders consist of two fully connected layers with one SiLU activation.
    for y, heading, features, name in [
            (.815, 'Scaled own-target history [24]', 24, 'Target-history MLP: each location and target'),
            (.625, 'Scaled all-signal history + context [69]', 69, 'Context MLP: each location')]:
        text(ax, .18, y+.073, heading, 9)
        box(ax, .02, y, .115, .060, f'Linear\n{features} → 96', size=8.5)
        box(ax, .165, y, .070, .060, 'SiLU', size=8.5)
        box(ax, .265, y, .115, .060, 'Linear\n96 → 96', size=8.5)
        arrow(ax, (.135, y+.030), (.162, y+.030))
        arrow(ax, (.235, y+.030), (.262, y+.030))
        text(ax, .20, y-.026, name, 8.3)
        text(ax, .40, y+.030, '[96]', 8.2)

    box(ax, .45, .680, .205, .150,
        'Add history + context\n+ target + week projection\n\nLayerNorm [96]', fill=PALE, size=8.8)
    arrow(ax, (.417, .845), (.447, .785))
    arrow(ax, (.417, .655), (.447, .715))
    arrow(ax, (.655, .755), (.726, .755))
    text(ax, .692, .789, '[96]', 8)
    box(ax, .73, .685, .245, .140, 'Residual block × 3\n\nLinear 96 → 1', fill=PALE, size=9.5)
    text(ax, .8525, .882, 'Noise z ~ Normal(0, I)\n[M, N, 16]', 8.6, color=BLUE)
    arrow(ax, (.8525, .852), (.8525, .828))
    arrow(ax, (.8525, .685), (.8525, .635))
    box(ax, .73, .550, .245, .080, 'Anchor + native-unit link\nAdmissions / ED share', fill=GRAY, size=8.8)
    text(ax, .8525, .520, '[M, N, 4 weeks, 2 targets, 52]', 8)
    text(ax, .02, .540, 'Context: 48 history fields + 3 calendar + 2 geography + 10 dynamics + 6 Kinsa summaries = 69.',
         8.1, ha='left')
    text(ax, .02, .500, 'History MLP weights are shared across locations; own-target weights are also shared across targets.',
         8.1, ha='left')

    # One residual block is expanded into its actual operations below.
    text(ax, .02, .447, 'Inside each sampled residual block', 11, True, ha='left')
    box(ax, .015, .075, .965, .330, dashed=True)
    text(ax, .09, .380, 'Same z [16]', 8.5, color=BLUE)
    arrow(ax, (.09, .357), (.255, .357))
    box(ax, .26, .325, .185, .065, 'Linear 16 → 192', fill=PALE, size=9)
    text(ax, .59, .357, 'Split into scale γ [96] and shift β [96]', 8.4, color=BLUE)
    arrow(ax, (.445, .357), (.475, .357))
    arrow(ax, (.3525, .325), (.3525, .295))

    box(ax, .065, .205, .120, .085, 'LayerNorm\n[96]', size=9)
    box(ax, .245, .205, .200, .085, '(1 + γ) × h + β\n[96]', fill=PALE, size=9)
    box(ax, .495, .205, .115, .085, 'Linear\n96 → 96', size=8.5)
    box(ax, .640, .205, .070, .085, 'SiLU', size=8.5)
    box(ax, .740, .205, .115, .085, 'Linear\n96 → 96', size=8.5)
    for a, b in [(.03, .061), (.185, .241), (.445, .491), (.610, .636), (.710, .736), (.855, .883)]:
        arrow(ax, (a, .2475), (b, .2475))
    ax.add_patch(Circle((.905, .2475), .018, fc='white', ec=INK, lw=.8))
    text(ax, .905, .2475, '+', 12)
    arrow(ax, (.923, .2475), (.97, .2475))
    text(ax, .948, .285, '[96]', 8)
    ax.plot([.035, .035, .905], [.2475, .130, .130], lw=.9, color=INK)
    arrow(ax, (.905, .130), (.905, .226))
    text(ax, .47, .105, 'Skip connection: add the block input', 8.5)
    text(ax, .02, .039, 'Each block has its own weights and noise projection. The same draw z is shared across blocks, locations, targets and weeks.',
         8, ha='left')
    text(ax, .02, .010, 'M: sampled paths; N: episodes. Shown: four forecast weeks. One decoded value per path, location, target and week.',
         8, ha='left')
    save(fig, 'sampled-building-blocks')


if __name__ == '__main__':
    information()
    network()
    decoders()
    forecast()
    fitting()
    llm_search()
    sampled_blocks()
