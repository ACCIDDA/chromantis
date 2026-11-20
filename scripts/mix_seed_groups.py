"""Write 12-seed backtest mixture specs for the release candidates by gathering each recipe's completed runs across
its round and reseed experiments (seeds 44-55). Run from the Longleaf campaign folder:
    python3 scripts/mix_seed_groups.py covid main
"""
import csv, json, sys
from pathlib import Path
spec = {
 'covid': ({'GruL1': ('T.pN_gru.real.log_loss1', ['r04', 'reseed03', 'reseed04']), 'Att': ('T.pN_gru.real.log_loss1.attention', ['r07', 'reseed03', 'reseed04']),
            'J03': ('T.pN_gru.real.log_loss1.joint0.3', ['r09', 'reseed03', 'reseed04']), 'SAhGru': ('S.Ah.gru_national.real', ['r08', 'reseed03', 'reseed04']),
            'Gru': ('T.pN_gru.real', ['r02', 'reseed02', 'reseed04'])},
           {'GruL1 alone': ['GruL1'], 'GruL1+Att': ['GruL1', 'Att'], 'GruL1+Att+SAhGru': ['GruL1', 'Att', 'SAhGru'], 'GruL1+Gru+SAhGru': ['GruL1', 'Gru', 'SAhGru'],
            'GruL1+SAhGru': ['GruL1', 'SAhGru'], 'J03 alone': ['J03'], 'J03+Att': ['J03', 'Att'], 'GruL1+J03+Att+SAhGru': ['GruL1', 'J03', 'Att', 'SAhGru'], 'Att alone': ['Att']}),
 'rsv': ({'W1': ('A4c0.national.rsvnet.calendar.weeks1', ['r09', 'reseed03', 'reseed04']), 'NRCal': ('A4c0.national.rsvnet.calendar', ['r06', 'reseed03', 'reseed04']),
          'A4cN': ('A4c0.national', ['r02', 'reseed02', 'reseed04']), 'NR': ('A4c0.national.rsvnet', ['r05', 'reseed03', 'reseed04']),
          'BwHcLog': ('Bw.national.hc.log1p', ['r08', 'reseed03', 'reseed04'])},
         {'W1 alone': ['W1'], 'W1+NRCal': ['W1', 'NRCal'], 'W1+A4cN+NR': ['W1', 'A4cN', 'NR'], 'A4cN+NR': ['A4cN', 'NR'], 'NRCal alone': ['NRCal'],
          'W1+BwHcLog': ['W1', 'BwHcLog'], 'BwHcLog alone': ['BwHcLog'], 'W1+NRCal+A4cN+NR': ['W1', 'NRCal', 'A4cN', 'NR']})}
# Final comparison (20 Nov 2026): the recommended members on every backtest seed run (44-79), same seed count per recipe.
final = {
 'covid': ({'GruL1': ('T.pN_gru.real.log_loss1', ['r04', 'reseed03', 'reseed04', 'reseed05', 'reseed06', 'reseed07']),
            'Gru': ('T.pN_gru.real', ['r02', 'reseed02', 'reseed04', 'reseed05', 'reseed06', 'reseed07']),
            'SAhGru': ('S.Ah.gru_national.real', ['r08', 'reseed03', 'reseed04', 'reseed05', 'reseed06', 'reseed07'])},
           {'GruL1 alone': ['GruL1'], 'GruL1+Gru+SAhGru': ['GruL1', 'Gru', 'SAhGru'], 'GruL1+Gru': ['GruL1', 'Gru']}),
 'rsv': ({'W1': ('A4c0.national.rsvnet.calendar.weeks1', ['r09', 'reseed03', 'reseed04', 'reseed05', 'reseed06', 'reseed07']),
          'NRCal': ('A4c0.national.rsvnet.calendar', ['r06', 'reseed03', 'reseed04', 'reseed06', 'reseed07'])},
         {'W1 alone': ['W1'], 'W1+NRCal': ['W1', 'NRCal']})}
p, kind = sys.argv[1], sys.argv[2]
recipes, groups = (final if len(sys.argv) > 3 and sys.argv[3] == 'final' else spec)[p]
out = {}
for label, (name, rounds) in recipes.items():
    runs, seeds, scen = [], set(), None
    for r in rounds:
        e = f'{p}-cov-{r}' if kind == 'main' else f'{p}-cov-' + (r.replace('r0', 'fwd0').replace('r1', 'fwd1') if r.startswith('r') and not r.startswith('reseed') else r.replace('reseed', 'reseedfwd'))
        for row in csv.DictReader(open(f'data/experiments/{e}/runs.csv')):
            if row['name'] == name and row['status'] == 'complete' and row['seed'] not in seeds:
                seeds.add(row['seed']); runs.append(f'data/experiments/{e}/{row["attempt"]}'); scen = row['scenario']
    out[label] = {'runs': runs, 'scenario': scen}
    print(label, len(runs), sorted(seeds), file=sys.stderr)
tag = 'final' if len(sys.argv) > 3 and sys.argv[3] == 'final' else '04'
json.dump({'description': f'{p} backtest mixtures ({kind}, {tag})', 'recipes': out, 'groups': groups, 'rules': ['mixture'], 'forecast_view': 'corrected'},
          open(f'experiments/covid-rsv-coverage-20261118/{p}-mix-{tag}-{kind}.json', 'w'), indent=1)
