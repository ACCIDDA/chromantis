"""Score the complete four-seed ILI experiment and save tables/figures in its run cache.

Run from the repository root after all training jobs finish:
    PYTHONPATH=src .venv/bin/python scripts/finish_season_peak_ili.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from chromantis.experiment.planner import completed_runs
from chromantis.problem import Problem
from chromantis.seasonal import run, score


EXPERIMENT = Path('data/experiments/season-peak-ili')
OUTPUT = EXPERIMENT / 'seasonal'
PROBLEM = 'problems/us-flu-season-peak-ili.json'
LABELS = {
    'I.sqrt_noise': 'MLP: square root + local noise',
    'I.fourth_root': 'MLP: fourth root + shared noise',
    'climatology-own': 'Climatology: other ILI seasons',
    'climatology-all': 'Climatology: other ILI + NHSN seasons',
    'analogue-all': 'Analogue: other ILI + NHSN seasons',
}
METRICS = ['peak_week_log_score', 'peak_wis_log']


def main():
    torch.set_num_threads(1)
    rows, complete = completed_runs(EXPERIMENT)
    assert complete
    problem = Problem.load(PROBLEM)
    settings = json.loads((EXPERIMENT / 'experiment.json').read_text())
    training_problem = Problem.load(settings['problem'])
    if training_problem.folds != problem.folds or training_problem.panel != problem.panel:
        raise ValueError('Training and seasonal scoring must use the same folds and panel')
    study = json.loads((EXPERIMENT / 'study.json').read_text())
    expected = {(name, seed) for name in study['candidates'] for seed in study['seeds']}
    if {(r['name'], r['seed']) for r in rows} != expected:
        raise ValueError('Completed runs do not match the study candidates and seeds')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    checkpoint_records = []
    frames = []
    for name in study['candidates']:
        checkpoints = OUTPUT / 'checkpoints' / name
        for row in [r for r in rows if r['name'] == name]:
            for held_out in problem.folds:
                source = EXPERIMENT / row['attempt'] / f'eval_{held_out}' / 'model.pt'
                saved = torch.load(source, map_location='cpu', weights_only=False)['metadata']
                if (saved['held_out_season'], saved['seed'], saved['dataset_sha256']) != (
                        held_out, row['seed'], settings['dataset_sha256']):
                    raise ValueError(f'Wrong held-out season, seed or dataset: {source}')
                target = checkpoints / held_out / f"s{row['seed']}" / 'model.pt'
                target.parent.mkdir(parents=True, exist_ok=True)
                target.unlink(missing_ok=True)
                target.symlink_to(source.resolve())
                checkpoint_records.append(dict(candidate=name, seed=row['seed'], held_out=held_out,
                                               model=str(source), training_seasons=[
                                                   s for s in training_problem.training_folds if s != held_out]))
        folder = run(PROBLEM, f'model=trajectory,samples=512,checkpoints={checkpoints},'
                     f'fold_problem={settings["problem"]}', OUTPUT / name)
        frames.append(score(folder).assign(candidate=name))
    for name, recipe in [
        ('climatology-own', 'model=climatology'),
        ('climatology-all', 'model=climatology,library=all'),
        ('analogue-all', 'model=analogue,library=all,noise=0.3,tau=0.5'),
    ]:
        frames.append(score(run(PROBLEM, recipe, OUTPUT / name)).assign(candidate=name))
    table = pd.concat(frames, ignore_index=True)
    # Keep exactly the same location/origin tasks across all five forecasts.
    keys = ['season', 'origin', 'location']
    sets = [set(map(tuple, t[keys].to_numpy())) for t in frames]
    shared = set.intersection(*sets)
    table = table[[tuple(k) in shared for k in table[keys].to_numpy()]].copy()
    table.to_csv(OUTPUT / 'scores.csv', index=False)
    before = table[(table.geography == 'states_dc') & (table.weeks_to_true_peak >= 0)].copy()
    before['lead_group'] = np.where(before.weeks_to_true_peak >= 8, '8+ weeks before peak', '0–7 weeks before peak')
    overall = before.groupby('candidate')[METRICS].mean().reindex(LABELS)
    overall['timing_cells'] = before.groupby('candidate').peak_week_log_score.count()
    overall['size_cells'] = before.groupby('candidate').peak_wis_log.count()
    overall.to_csv(OUTPUT / 'summary.csv')
    by_season = before.groupby(['candidate', 'season'])[METRICS].mean()
    by_season.to_csv(OUTPUT / 'by-season.csv')
    before.groupby(['candidate', 'lead_group'])[METRICS].mean().to_csv(OUTPUT / 'by-lead.csv')
    context = dict(
        training='Each MLP is retrained on the other nine ILI-converted seasons among 2011–12 through '
                 '2021–22, excluding 2020–21. Admissions-only inputs; 36 weekly prediction labels '
                 'are the same converted ILI counts. Both use neighboring-state exchange and weekly, '
                 'path and peak losses. Four fitted seeds (44–47) supply 512 pooled draws.',
        evaluation='Each excluded season is evaluated using converted ILI history through the preceding '
                   'Saturday. Peak labels are maxima and argmaxes of that same converted ILI series '
                   'over epiweeks 40–21. These are retrospective proxy admissions, not real hospital '
                   'admissions or real-time Wednesday reports.',
        conversion='Per-state conversion factors were fitted on paired ILI and NHSN data from '
                   '2022–23 through 2025–26; historical ILI has its own summer baseline subtracted.',
        baselines='Own climatology draws from the other nine ILI seasons; all climatology and analogue '
                  'also include NHSN 2022–23 through 2025–26. They use the same observed evaluation history.',
        aggregation='States/DC; reference dates at or before the true peak week; mean over common '
                    'location/date cells. Tied truth peaks are excluded from timing only. Lower is better. '
                    'Timing: negative log probability, floored at 0.001. Size: WIS on log(1 + count).',
        checkpoint_records=checkpoint_records,
        recipes=study['candidates'], seeds=study['seeds'],
    )
    (OUTPUT / 'context.json').write_text(json.dumps(context, indent=2) + '\n')
    fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
    for metric, ax, title in zip(METRICS, axes, ['Peak-week negative log probability', 'Peak-size WIS on log(1 + converted admissions)']):
        for name, label in LABELS.items():
            values = by_season.loc[name, metric].reindex(problem.folds)
            ax.plot(range(len(values)), values, marker='o', label=label)
        ax.set_ylabel(title + '\n(lower is better)')
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8, ncol=2)
    axes[1].set_xticks(range(len(problem.folds)), [s[:4] + '–' + s[-2:] for s in problem.folds])
    axes[1].set_xlabel('Held-out evaluation season')
    fig.suptitle('Season peaks from ILI-converted admissions · all four seeds · states and DC')
    fig.text(.06, .02, 'MLPs: train on the other nine ILI seasons (2011–12 to 2021–22; 2020–21 excluded); labels are 36 future converted-ILI weeks.\n'
             'Square-root/local-noise vs fourth-root/shared-noise training inputs; both use neighbors and path + peak losses.\n'
             'Evaluate on the held-out season’s converted-ILI history and peak labels; dates at or before peak. No retraining for pooling.\n'
             '“Other ILI” excludes the evaluated season; “NHSN” adds 2022–23 to 2025–26. Conversion factors also use those NHSN seasons.', fontsize=8)
    fig.tight_layout(rect=(0, .115, 1, .95))
    fig.savefig(OUTPUT / 'peak-comparison.png', dpi=160)
    plt.close(fig)
    print(overall.to_string(), flush=True)
    print(f'Complete: {OUTPUT}', flush=True)


if __name__ == '__main__':
    main()
