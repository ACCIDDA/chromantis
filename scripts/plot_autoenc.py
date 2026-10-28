"""Figures for the autoencoder exploration report (docs/experiments/autoenc-20261024).

Reads the `summary.csv` tables written by scripts/autoenc_score.py and the season-peak
`summary.csv` of scripts/score_peak_logtiming.py, copied into one folder per scoring run:

    python scripts/plot_autoenc.py SCORES_FOLDER docs/experiments/autoenc-20261024
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'


def score(folder, recipe, column='mixture_log_states'):
    if not (folder / 'summary.csv').exists():
        return None
    table = pd.read_csv(folder / 'summary.csv', index_col=0)
    return table.loc[recipe, column] if recipe in table.index else None


def first(scores, names, recipe):
    for name in names:
        value = score(scores / name, recipe)
        if value is not None:
            return value
    return None


def style(ax):
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color(GRID)
    ax.spines['bottom'].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis='x', color=GRID, linewidth=.6)
    ax.set_axisbelow(True)


def vae_settings(scores, out):
    """Percent change of A4 with each latent variant against A4, seeds 44-47, in three settings."""
    variants = [('KL 0.03', 'A4.cvae_kl0.03'), ('KL 0.3', 'A4.cvae_kl0.3'), ('KL 1', 'A4.cvae_kl1'),
                ('KL 3', 'A4.cvae_kl3'), ('KL 10', 'A4.cvae_kl10'),
                ('KL 3, posterior off', 'A4.cvae_kl3_prior_only'), ('KL 3, posterior weight 0.3', 'A4.cvae_kl3_w0.3'),
                ('KL 3, posterior weight 3', 'A4.cvae_kl3_w3'), ('KL 1, posterior weight 3', 'A4.cvae_kl1_w3')]
    settings = [('Leave one season out\n(train on 3 of 4 seasons)', ['score-r07', 'score02', 'score01', 'score-loso2']),
                ('Forward: train 2022-23, 2023-24;\nforecast 2024-25', ['score-w3-fwd7', 'score-fwd3']),
                ('Forward: train 2022-23;\nforecast 2023-24', ['score-w3-fwd8'])]
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2), sharey=True)
    for ax, (title, names) in zip(axes, settings):
        reference = first(scores, names, 'A4')
        for i, (label, recipe) in enumerate(variants):
            value = first(scores, names, recipe)
            if value is None:
                continue
            change = 100 * (value / reference - 1)
            color = BLUE if change < 0 else ORANGE
            ax.plot([0, change], [i, i], color=color, linewidth=2, solid_capstyle='round')
            ax.plot(change, i, 'o', color=color, markersize=7, markeredgecolor='white', markeredgewidth=1.5)
            ax.text(change + (.6 if change >= 0 else -.6), i, f'{change:+.1f}%', va='center',
                    ha='left' if change >= 0 else 'right', fontsize=7.5, color=INK)
        ax.axvline(0, color=MUTED, linewidth=1)
        ax.set_title(f'{title}\nA4 alone: {reference:.4f}', fontsize=9, color=INK)
        ax.set_xlabel('change in log-admission WIS vs A4 (%)\nlower is better', fontsize=8, color=MUTED)
        ax.set_xlim(-22, 22)
        style(ax)
    axes[0].set_yticks(range(len(variants)), [v[0] for v in variants], fontsize=8, color=INK)
    axes[0].invert_yaxis()
    fig.suptitle('A4 with a conditional-VAE latent: helps forward in time only with a strong KL and the full posterior loss',
                 fontsize=10, color=INK, x=.02, ha='left')
    fig.text(.02, .005, 'Mixture of seeds 44-47 of each recipe; states/DC WIS of log(1 + admissions), October-May, '
             'prescribed artificial preliminary inputs. Blank rows were not run in that setting.', fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, .03, 1, .95))
    fig.savefig(out / 'vae-settings.png', dpi=150)
    plt.close(fig)


def same_data_arms(scores, out):
    """Round 1: percent change against each reference recipe, leave one season out, seeds 44-47."""
    changes = [('rebuild loss', 'ae1'), ('15% cells hidden', 'm15'), ('rebuild + hidden', 'ae1_m15'),
               ('bottleneck 16', 'b16'), ('rebuild + bottleneck', 'ae1_b16'), ('rebuild + bottleneck + hidden', 'ae1_b16_m15'),
               ('pretrain: rebuild, ILI + COVID/RSV', 'pre_rec_all'), ('pretrain: rebuild, ILI', 'pre_rec_ili'),
               ('pretrain: rebuild, COVID/RSV', 'pre_rec_path'), ('pretrain: forecast (control)', 'pre_fc_all'),
               ('pretrain: rebuild + forecast', 'pre_both_all'), ('pretrain + keep rebuild loss', 'pre_rec_all+ae1')]
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for offset, family, color in ((-.18, 'Bes', BLUE), (.18, 'A4', ORANGE)):
        reference = score(scores / 'score01', family)
        for i, (_, key) in enumerate(changes):
            change = 100 * (score(scores / 'score01', f'{family}.{key}') / reference - 1)
            ax.plot([0, change], [i + offset] * 2, color=color, linewidth=2, solid_capstyle='round')
            ax.plot(change, i + offset, 'o', color=color, markersize=6, markeredgecolor='white', markeredgewidth=1.2,
                    label=f'{family} (alone {reference:.4f})' if i == 0 else None)
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.set_yticks(range(len(changes)), [c[0] for c in changes], fontsize=8, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel('change in log-admission WIS vs the recipe without it (%), lower is better', fontsize=8, color=MUTED)
    ax.legend(frameon=False, fontsize=8, loc='lower right')
    ax.set_title('Input reconstruction, masking, bottleneck and pretraining (round 1, leave one season out)',
                 fontsize=9.5, color=INK, loc='left')
    style(ax)
    fig.text(.01, .005, 'Mixture of seeds 44-47; with seeds 48-51 added, the best A4 changes (bottleneck 16, '
             'pretrain + rebuild) no longer beat A4.', fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, .03, 1, 1))
    fig.savefig(out / 'same-data-arms.png', dpi=150)
    plt.close(fig)


def peaks(scores, out):
    table = pd.concat([pd.read_csv(f / 'summary.csv') for f in sorted(scores.glob('peak*'))])
    table = table.drop_duplicates('model').set_index('model').drop(index='Previous model, four seeds', errors='ignore')
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for name, row in table.iterrows():
        color = MUTED if name == 'FluSight-ensemble' else ORANGE if 'cvae' in name else BLUE
        ax.plot(row.peak_week_log_score, row.peak_wis_log, 'o', color=color, markersize=7,
                markeredgecolor='white', markeredgewidth=1.2)
        ax.annotate(name.replace('Peak8.', '+ '), (row.peak_week_log_score, row.peak_wis_log), xytext=(5, 3),
                    textcoords='offset points', fontsize=7, color=INK)
    ax.set_xlabel('peak-week negative log score, lower is better', fontsize=8, color=MUTED)
    ax.set_ylabel('peak-size WIS of log(1 + admissions), lower is better', fontsize=8, color=MUTED)
    ax.set_title('Season-peak forecasts: Peak8 with autoencoder options (orange: conditional VAE)',
                 fontsize=9.5, color=INK, loc='left')
    style(ax)
    ax.grid(axis='y', color=GRID, linewidth=.6)
    fig.text(.01, .005, f'{int(table.tasks.iloc[0])} matched state/DC tasks, 2024-25 and 2025-26, archived Wednesday reports; '
             'mixture of each recipe\'s seeds (44-51 for Peak8, + pre_both_all, + cvae_kl1 and their combination; 44-47 for the others).', fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, .03, 1, 1))
    fig.savefig(out / 'season-peak.png', dpi=150)
    plt.close(fig)


if __name__ == '__main__':
    scores, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    vae_settings(scores, out)
    same_data_arms(scores, out)
    peaks(scores, out)
