"""Current-season refits of recipes chosen before reserved-season outcomes are read."""
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from chromantis.model.scenario import Scenario

KINDS = ('fourweek', 'fullseason', 'california', 'utah')


def selected_candidates(state, root, kind):
    if kind == 'fourweek':
        rd = next(r for r in state['rounds'] if r['name'] == state['confirmation'])
        study = json.loads(Path(rd['study']).read_text())
        name, scenario = next(iter(study['candidates'].items()))
        candidates = {name: scenario, name+'_fit_lag1':
                      replace(Scenario.from_string(scenario), training_target_lag=1).scenario_string}
        delay = json.loads((root/'delay-frozen-selection.json').read_text())
        candidates['county_development_recipe_fit_on_main_panel'] = delay['candidates']['county_development_recipe_fit_on_main_panel']
        return candidates
    file = 'full-season-frozen-selection.json' if kind == 'fullseason' else f'{kind}-frozen-selection.json'
    frozen = json.loads((root/file).read_text())
    return {name: scenario for name, scenario in frozen['candidates'].items() if 'reference' not in name}


def plan_next(state, root, plan, save, state_path):
    assert datetime.now(timezone.utc) >= datetime(2026, 10, 21, 5, 30, tzinfo=timezone.utc)
    assert all(state.get(k) for k in (
        'confirmation', 'full_season_confirmation', 'delay_confirmation',
        'context_confirmation', 'california_confirmation', 'utah_confirmation'))
    current = state.setdefault('current_refits', {})
    for kind in KINDS:
        if kind in current:
            continue
        candidates = selected_candidates(state, root, kind)
        assert candidates
        name = plan(state, candidates, {}, [42,43,44,45,46], stage='current-'+kind,
                    problem=f'problems/metrocast-current-{kind}.json', protocol=dict(
                        training_seasons=['2024-07-06 through 2026-07-25'] if kind == 'california'
                        else ['2022-2023','2023-2024','2024-2025','2025-2026'],
                        evaluation_season='2026-2027; current partial-season diagnostics, never used for recipe selection',
                        inputs=('Provisional unmerged PR587 revised weekly Utah histories; no release archive; selected target-history fitting gap.'
                                if kind == 'utah' else 'Revised training histories, with the selected recipe target-history gap; source covariates unchanged.'),
                        labels='Published California partial admission sums' if kind == 'california' else 'Future local flu ED proportions',
                        selection='Recipes copied from development-only frozen selections; confirmation outcomes are not read.',
                        export='2026-10-24 reference, equal five-seed mixture, 100 intact trajectories; no publication.'))
        current[kind] = name
        save(state_path, state)
        save(root/f'current-{kind}-selection.json', dict(
            experiment=name, candidates=candidates, reference_date='2026-10-24',
            selection='Development-only frozen recipes; confirmation outcomes not consulted.',
            frozen_at=datetime.now(timezone.utc).isoformat()))
        cmd = ['sbatch', f'--job-name={name}-export', 'scripts/metrocast_current_export.sbatch', name]
        result = subprocess.run(cmd, text=True, capture_output=True, check=True)
        with (root/'manager-commands.sh').open('a') as f:
            f.write('\n'+' '.join(cmd)+'\n# '+result.stdout.strip()+'\n')
            f.write(f'.venv/bin/python scripts/export_metrocast_current.py -e {name}\n')
        return name
    return None
