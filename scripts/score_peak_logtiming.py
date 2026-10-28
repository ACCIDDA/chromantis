"""Compare complete timing-loss experiments on identical archived-report peak tasks."""
import argparse
import json
import textwrap
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', nargs='+', default=['season-peak-logtiming'],
                        help='One or more experiments; runs of the same recipe name are pooled (2026-10-25)')
    parser.add_argument('--out', help='Output folder; default <first experiment>/seasonal')
    args = parser.parse_args()
    torch.set_num_threads(1)
    experiments = [Path('data/experiments') / name for name in args.experiment]
    experiment = experiments[0]
    study = json.loads((experiment / 'study.json').read_text())
    settings = json.loads((experiment / 'experiment.json').read_text())
    out = Path(args.out) if args.out else experiment / 'seasonal'
    rows = []
    for folder in experiments:
        found, complete = completed_runs(folder)
        assert complete
        rows += [dict(r, attempt=str(folder / r['attempt'])) for r in found]
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
                source = Path(row['attempt']) / f'eval_{held}' / 'model.pt'
                metadata = torch.load(source, map_location='cpu', weights_only=False)['metadata']
                if (metadata['held_out_season'], metadata['seed']) != (held, row['seed']):
                    raise ValueError(f'Wrong checkpoint: {source}')
                target = checkpoints / held / f"s{row['seed']}" / 'model.pt'
                target.parent.mkdir(parents=True, exist_ok=True)
                target.unlink(missing_ok=True)
                target.symlink_to(source.resolve())
        folders[name] = run('problems/us-flu-season-peak.json',
                            f'model=trajectory,inputs=reported,samples=512,checkpoints={checkpoints},'
                            f'fold_problem={settings["problem"]}', out / name)
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
        'training': study['description'],
        'evaluation': '2024–25 and 2025–26: archived FluSight Wednesday-deadline reports, no finalized-value fallback; final NHSN peak labels over epiweeks 40–21. Exclude missing past-window reports. Matched state/DC tasks at or before the true peak, excluding timing ties. FluSight-ensemble uses its archived submissions. Lower is better: peak-week negative log probability (floor 0.001), peak-size WIS of log(1+admissions). Retrospective development comparison, not an untouched or forward-only test.',
        'tasks': len(shared), 'runs': rows, 'study': study,
    }
    (out / 'context.json').write_text(json.dumps(context, indent=2) + '\n')
    fig, axes = plt.subplots(1, 2, figsize=(13, 8))
    for metric, ax in zip(metrics, axes):
        summary[metric].plot.barh(ax=ax)
        ax.set_xlabel(metric + ' (lower is better)')
        ax.set_ylabel('')
    fig.suptitle(f'Archived-report peak forecasts · {len(shared)} identical state/DC tasks')
    caption = study['description'] + ' Reference MLP: finalized training histories, no peak-week log loss, four seeds (44–47).'
    fig.text(.02, .015, textwrap.fill(caption, 155), fontsize=8)
    fig.tight_layout(rect=(0, .25, 1, .94))
    fig.savefig(out / 'comparison.png', dpi=150)
    plt.close(fig)
    print(summary.to_string(), flush=True)


if __name__ == '__main__':
    main()
