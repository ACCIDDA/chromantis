"""Round table for the COVID tree search: each season scored on its most realistic inputs.

Primary = equal mean of states/DC log(1 + admissions) WIS over archived Wednesday reports in
2024-25 and 2025-26 and shared artificial preliminary histories in 2023-24, which has no COVID
report archive. Fits are never refit between the two inputs. Lower is better.

    .venv/bin/python scripts/covid_tree_table.py -e EXPERIMENT [--forward FORWARD_EXPERIMENT] --out TABLE.csv
"""
import argparse
import json
from pathlib import Path

import pandas as pd

HOSP, ED = 'wk inc covid hosp', 'wk inc covid prop ed visits'


def rankings(folder):
    """Newest complete ranking per evaluation input of one experiment."""
    found = {}
    for path in sorted(folder.glob('ranking-*/headline-season-scores.csv'), key=lambda p: p.stat().st_mtime):
        replayed = '/replay-reported/' in str(json.loads((path.parent / 'manifest.json').read_text()).get('runs'))
        found['reported' if replayed else 'other'] = path.parent
    return found


def season_scores(ranking):
    table = pd.read_csv(ranking / 'headline-season-scores.csv')
    return table[table.deployed]


def pick(table, season, target, scale, geography, column='mean_wis'):
    part = table[(table.target == target) & (table.scale == scale) & (table.geography == geography)]
    if season:
        part = part[part.season == season]
    return part.groupby('name')[column].mean()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--experiment', required=True)
    parser.add_argument('--forward')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    found = rankings(Path('data/experiments') / args.experiment)
    artificial, reported = season_scores(found['other']), season_scores(found['reported'])
    rows = pd.DataFrame({
        's2324_artificial': pick(artificial, '2023-2024', HOSP, 'log', 'states_dc'),
        's2425_archived': pick(reported, '2024-2025', HOSP, 'log', 'states_dc'),
        's2526_archived': pick(reported, '2025-2026', HOSP, 'log', 'states_dc')})
    rows.insert(0, 'primary', rows.mean(axis=1))
    rows['artificial_all_seasons'] = pick(artificial, None, HOSP, 'log', 'states_dc')
    rows['us_log_archived_2526'] = pick(reported, '2025-2026', HOSP, 'log', 'US')
    for geography in ('states_dc', 'US'):
        rows[f'ed_wis_2526_{geography}'] = pick(reported, '2025-2026', ED, 'natural', geography)
        for level in (50, 95):
            rows[f'hosp_cov{level}_2526_{geography}'] = pick(reported, '2025-2026', HOSP, 'log', geography, f'covered_{level}')
            rows[f'ed_cov{level}_2526_{geography}'] = pick(reported, '2025-2026', ED, 'natural', geography, f'covered_{level}')
    relative = found['reported'] / 'hub-relative-scores.csv'
    if relative.exists():
        table = pd.read_csv(relative)
        table = table[table.deployed & (table.season == '2025-2026')]
        for label, target, scale, geography in (('hub_ratio_log_states', HOSP, 'log', 'states_dc'), ('hub_ratio_log_us', HOSP, 'log', 'US'),
                                                ('hub_ratio_ed_states', ED, 'natural', 'states_dc'), ('hub_ratio_ed_us', ED, 'natural', 'US')):
            part = table[(table.target == target) & (table.scale == scale) & (table.geography == geography)]
            rows[label] = part.groupby('name').wis_ratio.mean()
    if args.forward:
        forward = season_scores(rankings(Path('data/experiments') / args.forward)['other'])
        rows['strict_forward_2526'] = pick(forward, '2025-2026', HOSP, 'log', 'states_dc')
    rows.sort_values('primary').to_csv(args.out, float_format='%.5g')
    pd.set_option('display.width', 250, 'display.max_columns', 40, 'display.max_rows', 200)
    show = ['primary', 's2324_artificial', 's2425_archived', 's2526_archived'] + [c for c in ('strict_forward_2526', 'hub_ratio_log_states', 'hub_ratio_ed_states', 'hub_ratio_ed_us') if c in rows]
    print(rows.sort_values('primary')[show].round(4).to_string())


if __name__ == '__main__':
    main()
