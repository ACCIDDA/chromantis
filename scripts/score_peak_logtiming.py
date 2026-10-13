"""Compare complete timing-loss experiments on identical archived-report peak tasks."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import torch

from chromantis.experiment.planner import completed_runs
from chromantis.problem import Problem
from chromantis.seasonal import run, score


def main():
    torch.set_num_threads(1)
    experiment = Path('data/experiments/season-peak-logtiming')
    out = experiment / 'seasonal'
    rows, complete = completed_runs(experiment)
    assert complete
    problem = Problem.load('problems/us-flu-season-peak.json')
    out.mkdir(parents=True, exist_ok=True)
    folders = {
        'Previous model, four seeds': Path('data/seasonal/us-flu-season-peak/reported-sqrt-local'),
        'FluSight-ensemble': Path('data/seasonal/us-flu-season-peak/hub=FluSight-ensemble'),
    }
    for name in dict.fromkeys(row['name'] for row in rows):
        checkpoints = out / 'checkpoints' / name
        for row in [r for r in rows if r['name'] == name]:
            for held in problem.folds:
                source = experiment / row['attempt'] / f'eval_{held}' / 'model.pt'
                metadata = torch.load(source, map_location='cpu', weights_only=False)['metadata']
                if (metadata['held_out_season'], metadata['seed']) != (held, row['seed']):
                    raise ValueError(f'Wrong checkpoint: {source}')
                target = checkpoints / held / f"s{row['seed']}" / 'model.pt'
                target.parent.mkdir(parents=True, exist_ok=True)
                target.unlink(missing_ok=True)
                target.symlink_to(source.resolve())
        folders[name] = run('problems/us-flu-season-peak.json',
                            f'model=trajectory,inputs=reported,samples=512,checkpoints={checkpoints},'
                            'fold_problem=problems/us-flu-long-horizon.json', out / name)
    tables = {name: score(folder) for name, folder in folders.items()}
    keys = ['season', 'origin', 'location']
    metrics = ['peak_week_log_score', 'peak_wis_log']
    shared = set.intersection(*(set(map(tuple, t.loc[
        (t.geography == 'states_dc') & (t.weeks_to_true_peak >= 0)
    ].dropna(subset=metrics)[keys].to_numpy())) for t in tables.values()))
    if not shared:
        raise ValueError('No matched peak tasks')
    tables = {name: t[[tuple(k) in shared for k in t[keys].to_numpy()]].assign(model=name)
              for name, t in tables.items()}
    all_scores = pd.concat(tables.values(), ignore_index=True)
    all_scores.to_csv(out / 'matched-scores.csv', index=False)
    summary = all_scores.groupby('model')[metrics].mean()
    summary['tasks'] = len(shared)
    summary.to_csv(out / 'summary.csv')
    by_season = all_scores.groupby(['model', 'season'])[metrics].mean()
    by_season.to_csv(out / 'by-season.csv')
    all_scores['lead'] = all_scores.weeks_to_true_peak.ge(8).map({True: '8+', False: '0–7'})
    all_scores.groupby(['model', 'lead'])[metrics].mean().to_csv(out / 'by-lead.csv')
    context = {
        'training': 'For each held-out season, sampled MLPs train on the other three seasons among 2022–23 through 2025–26. Inputs are finalized NHSN admissions and flu-ED proportions; labels are 36 future weeks of both series. Square-root counts, local noise, neighboring-state exchange, weekly plus path and peak losses. Candidates add future peak-week log loss at weight 0.3 or 1; two seeds (44,45), compared with the previous model’s four seeds (44–47).',
        'evaluation': '2024–25 and 2025–26: archived FluSight Wednesday-deadline reports, no finalized-value fallback; final NHSN peak labels over epiweeks 40–21. Exclude missing past-window reports. Matched state/DC tasks at or before the true peak, excluding timing ties. FluSight-ensemble uses its archived submissions. Lower is better: peak-week negative log probability (floor 0.001), peak-size WIS of log(1+admissions). Retrospective development comparison, not an untouched or forward-only test.',
        'tasks': len(shared), 'runs': rows,
    }
    (out / 'context.json').write_text(json.dumps(context, indent=2) + '\n')
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for metric, ax in zip(metrics, axes):
        summary[metric].plot.barh(ax=ax)
        ax.set_xlabel(metric + ' (lower is better)')
        ax.set_ylabel('')
    fig.suptitle(f'Archived-report peak forecasts · {len(shared)} identical state/DC tasks')
    fig.text(.02, .015, 'MLPs: train on other three NHSN/flu-ED seasons from 2022–23 to 2025–26; labels are 36 future weekly values.\n'
             'Evaluate on held-out 2024–25 / 2025–26 Wednesday reports and final NHSN peak labels; no truth filling.\n'
             'Candidates add timing log loss (0.3 or 1), two seeds; previous model has four seeds. Retrospective development comparison.', fontsize=8)
    fig.tight_layout(rect=(0, .13, 1, .94))
    fig.savefig(out / 'comparison.png', dpi=150)
    plt.close(fig)
    print(summary.to_string(), flush=True)


if __name__ == '__main__':
    main()
