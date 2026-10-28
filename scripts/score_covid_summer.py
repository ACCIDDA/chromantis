"""Separate June–September diagnostic on saved COVID forecasts; never changes selection scores."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from chromantis.evaluation.standard import export, check_raw_tasks, scored, QCOLS, KEY, scales_for
from chromantis.experiment.planner import ranking_runs
from chromantis.evaluation.ranking import deployed_view


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('-e', '--experiment')
    source.add_argument('--ensemble-directory', type=Path)
    p.add_argument('--inputs', choices=['reported'])
    args = p.parse_args()
    if args.ensemble_directory:
        folder = args.ensemble_directory
        runs = [dict(path=f.parent, name=f.parent.name, seed=0,
                     config_id=json.dumps(json.loads(f.read_text())['ensemble'], sort_keys=True))
                for f in sorted(folder.glob('*/manifest.json'))
                if 'ensemble' in json.loads(f.read_text())]
    else:
        folder = Path('data/experiments') / args.experiment
        runs, _ = ranking_runs(folder, allow_incomplete=True, inputs=args.inputs)
    rows = []
    for run in runs:
        view = deployed_view(run['path'])
        from chromantis.evaluation.ranking import views
        selected = {k: v for k, v in views(run['path']).items()
                    if k == view or (k.startswith('draw') and k.endswith('_' + view))}
        for draw, target in selected.items():
            for (season, signal), frame in export(target).items():
                frame = frame[frame.model_original_mask.astype(bool) & frame.horizon.lt(4)
                              & frame.reference_date.str[5:7].isin(['06', '07', '08', '09'])]
                if frame.empty:
                    continue
                check_raw_tasks(frame, signal, str(target))
                for scale in scales_for(signal):
                    for geography, part in [('states_dc', frame.location.ne('US')), ('US', frame.location.eq('US'))]:
                        f = frame.loc[part].sort_values(KEY)
                        if f.empty:
                            continue
                        values = scored(f[QCOLS].to_numpy(), f.model_original_truth.to_numpy(), scale)
                        rows.append(dict(name=run['name'], seed=run['seed'], scenario=run['config_id'],
                                         view=view, evaluation_draw=draw, season=season, target=signal, scale=scale, geography=geography,
                                         mean_wis=float(values.wis.mean()), tasks=len(f),
                                         first_reference=f.reference_date.min(), last_reference=f.reference_date.max(),
                                         support_sha256=hashlib.sha256(f[[*KEY, 'model_original_truth']].to_csv(index=False).encode()).hexdigest()))
    out = folder / ('summer-reported.csv' if args.inputs else 'summer.csv')
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f'{out}: {len(rows)} rows; no rows means summer forecasts are unavailable, not zero error')


if __name__ == '__main__':
    main()
