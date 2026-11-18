# COVID tree search of 30 October 2026, on Longleaf from /hickory/proj/jlessler/projects/tapestry-all/covid-20261030
# (PYTHONPATH=src or the experiment's code snapshot).
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r01 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd01 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-reseed01 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/reseed-01.json --device cuda
sbatch --array=0-5 scripts/covid_tree.sbatch covid-1030-r01 covid-1030-fwd01 covid-1030-reseed01   # job 7397008, 2026-10-30 16:28 EDT
.venv/bin/python -m chromantis.experiment.planner status -e covid-1030-r01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-1030-r01 --no-report
.venv/bin/python -m chromantis.experiment.planner replay -e covid-1030-r01 --inputs reported --device cpu
.venv/bin/python -m chromantis.experiment.planner rank -e covid-1030-r01 --inputs reported --no-report
.venv/bin/python scripts/covid_tree_table.py -e covid-1030-r01 --forward covid-1030-fwd01 --out output/covid-1030-r01.csv
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-production00 --problem problems/us-covid-production.json --study experiments/covid-tree-20261030/production-00.json --device cuda
sbatch --array=0-5 --dependency=afterany:7397008 scripts/covid_tree.sbatch covid-1030-production00

# Strict forward check of the finalized-history recipes (Bf, Af, Bw512f)
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd02 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-02.json --device cuda
sbatch --array=0-5 scripts/covid_tree.sbatch covid-1030-fwd02
.venv/bin/python -m chromantis.experiment.planner status -e covid-1030-fwd02
.venv/bin/python -m chromantis.experiment.planner rank -e covid-1030-fwd02 --no-report

# Round 2: covariates, more architectures, combinations; then its strict forward check
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r02 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd03 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-03.json --device cuda
sbatch --array=0-5 scripts/covid_tree.sbatch covid-1030-r02 covid-1030-fwd03
.venv/bin/python -m chromantis.experiment.planner status -e covid-1030-r02
.venv/bin/python -m chromantis.experiment.planner status -e covid-1030-fwd03
.venv/bin/python scripts/covid_tree_table.py -e covid-1030-r02 --forward covid-1030-fwd03 --out output/covid-1030-r02.csv

# Fresh seeds 204-207 for the round 1 leaders, queued after round 2 and its forward check
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-reseed02 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/reseed-02.json --device cuda
sbatch --array=0-5 --dependency=afterany:7527414 scripts/covid_tree.sbatch covid-1030-reseed02
.venv/bin/python -m chromantis.experiment.planner status -e covid-1030-reseed02
.venv/bin/python scripts/covid_tree_table.py -e covid-1030-reseed02 --out output/covid-1030-reseed02.csv

# 24-hour queue, in priority order (chained after covid-1030-reseed02, job 7527659)
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-production01 --problem problems/us-covid-production.json --study experiments/covid-tree-20261030/production-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r03 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-03.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd04 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-ed01 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/ed-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-edfwd01 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/ed-forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-leaders01 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/leaders-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-leadersfwd01 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/leaders-forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r02b --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-02b.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd03b --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-03b.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r03b --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-03b.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd04b --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-04b.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r01b --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-01b.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd01b --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-01b.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-leaders02 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/leaders-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-leadersfwd02 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/leaders-forward-02.json --device cuda
sbatch --array=0-5 --dependency=afterany:7527659 scripts/covid_tree.sbatch covid-1030-production01 covid-1030-r03 covid-1030-fwd04 covid-1030-ed01 covid-1030-edfwd01 covid-1030-leaders01 covid-1030-leadersfwd01 covid-1030-r02b covid-1030-fwd03b covid-1030-r03b covid-1030-fwd04b covid-1030-r01b covid-1030-fwd01b covid-1030-leaders02 covid-1030-leadersfwd02 
# 2026-10-31 15:53 EDT: pooled exchange first; replaces array 7530947.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-production02 --problem problems/us-covid-production.json --study experiments/covid-tree-20261030/production-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-confirm01 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/confirm-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-confirmfwd01 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/confirm-forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r04 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd05 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-ed02 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/ed-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-edfwd02 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/ed-forward-02.json --device cuda
sbatch --array=0-5 scripts/covid_tree.sbatch covid-1030-production02 covid-1030-confirm01 covid-1030-confirmfwd01 covid-1030-r04 covid-1030-fwd05 covid-1030-ed02 covid-1030-edfwd02 covid-1030-r03 covid-1030-fwd04 covid-1030-ed01 covid-1030-edfwd01 covid-1030-leaders01 covid-1030-leadersfwd01 covid-1030-r02b covid-1030-fwd03b covid-1030-r03b covid-1030-fwd04b covid-1030-r01b covid-1030-fwd01b covid-1030-leaders02 covid-1030-leadersfwd02   # job 7553962
# 2026-10-31 17:05 EDT: real mixtures, no refit; tables in data/experiments/covid-1030-mix01/*/ranking.
sbatch --job-name=covid-mix01-artificial scripts/covid_tree_mix.sbatch experiments/covid-tree-20261030/mix-01-artificial.json data/experiments/covid-1030-mix01/artificial
sbatch --job-name=covid-mix01-reported scripts/covid_tree_mix.sbatch experiments/covid-tree-20261030/mix-01-reported.json data/experiments/covid-1030-mix01/reported
sbatch --job-name=covid-mix01-forward scripts/covid_tree_mix.sbatch experiments/covid-tree-20261030/mix-01-forward.json data/experiments/covid-1030-mix01/forward
# 2026-10-31 18:07 EDT: tests of the swing with training seasons first; replaces arrays 7553962 and 7570560.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-production03 --problem problems/us-covid-production.json --study experiments/covid-tree-20261030/production-03.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-cal01 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/cal-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-calfwd01 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/cal-forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-bagfwda --problem problems/us-covid-forward-2025-26-reported-baga.json --study experiments/covid-tree-20261030/bag-forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-bagfwdb --problem problems/us-covid-forward-2025-26-reported-bagb.json --study experiments/covid-tree-20261030/bag-forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-bagfwdc --problem problems/us-covid-forward-2025-26-reported-bagc.json --study experiments/covid-tree-20261030/bag-forward-01.json --device cuda
sbatch --array=0-5 scripts/covid_tree.sbatch covid-1030-production03 covid-1030-bagfwda covid-1030-bagfwdb covid-1030-bagfwdc covid-1030-leaders01 covid-1030-leadersfwd01 covid-1030-cal01 covid-1030-calfwd01 covid-1030-r04 covid-1030-fwd05 covid-1030-ed02 covid-1030-edfwd02 covid-1030-r03 covid-1030-fwd04 covid-1030-ed01 covid-1030-edfwd01 covid-1030-r02b covid-1030-fwd03b covid-1030-r03b covid-1030-fwd04b covid-1030-r01b covid-1030-fwd01b covid-1030-leaders02 covid-1030-leadersfwd02   # job 7571455
sbatch --job-name=covid-mix02-reported scripts/covid_tree_mix.sbatch experiments/covid-tree-20261030/mix-02-reported.json data/experiments/covid-1030-mix02/reported
# 2026-10-31 19:05 EDT: leading mixtures on seeds 208-215, once leaders-01 and its forward check are scored.
sbatch --job-name=covid-mix03-artificial scripts/covid_tree_mix.sbatch experiments/covid-tree-20261030/mix-03-artificial.json data/experiments/covid-1030-mix03/artificial
sbatch --job-name=covid-mix03-reported scripts/covid_tree_mix.sbatch experiments/covid-tree-20261030/mix-03-reported.json data/experiments/covid-1030-mix03/reported
sbatch --job-name=covid-mix03-forward scripts/covid_tree_mix.sbatch experiments/covid-tree-20261030/mix-03-forward.json data/experiments/covid-1030-mix03/forward

# 2 November: best of round 4, all-season fits for the live check, then fresh seeds and forward check.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-production04 --problem problems/us-covid-production.json --study experiments/covid-tree-20261030/production-04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-confirm02 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/confirm-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-confirmfwd02 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/confirm-forward-02.json --device cuda
sbatch --array=0-5 scripts/covid_tree.sbatch covid-1030-production04 covid-1030-confirm02 covid-1030-confirmfwd02

# 3 November: round 5, the GRU encoder on other roots and options; all-season fits first for the live check.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-production05 --problem problems/us-covid-production.json --study experiments/covid-tree-20261030/production-05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-r05 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261030/round-05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-1030-fwd06 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261030/forward-06.json --device cuda
sbatch --array=0-5 scripts/covid_tree.sbatch covid-1030-production05 covid-1030-r05 covid-1030-fwd06
