# flu-search-20261120. Longleaf campaign folder (shares the coverage panel, ILI archive and .venv of the nowcast study):
#   /hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113
# From the Mac: send code, problems, datasets and the study
rsync -a --exclude __pycache__ --exclude .DS_Store src scripts problems datasets chadi@longleaf.unc.edu:/hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113/
rsync -a experiments/flu-search-20261120 chadi@longleaf.unc.edu:/hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113/experiments/
# Write a round's study files (main + 2023-24 guard) on the Mac
python3 experiments/flu-search-20261120/rounds.py 1
# On Longleaf, in the campaign folder:
export PYTHONPATH=src
S=experiments/flu-search-20261120
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-r01 --problem problems/us-flu-short-term-coverage.json --study $S/round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-g01 --problem problems/us-flu-2023-24-prescribed-coverage.json --study $S/guard-01.json --device cuda
sbatch --job-name=flu-s-r01 --array=0-5 scripts/flu_search.sbatch flu-s-r01 flu-s-g01
.venv/bin/python -m chromantis.experiment.planner status -e flu-s-r01
.venv/bin/python -m chromantis.experiment.planner status -e flu-s-g01
.venv/bin/python -m chromantis.experiment.planner rank -e flu-s-r01 --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner rank -e flu-s-g01 --allow-incomplete --no-report
.venv/bin/python scripts/flu_search_table.py -e flu-s-r01 --guard flu-s-g01 --out output/flu-search/r01.csv
# 2026-11-20 16:09 EST: round 1 launched as job 9984420 (array 0-5; element 5 waits for the GPU used by another lab member).
# 2026-11-20 16:45 EST: guard of round 1 reduced to references and roots (7 recipes; children are guarded only if they pass main), re-planned:
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-g01 --problem problems/us-flu-2023-24-prescribed-coverage.json --study $S/guard-01.json --device cuda
# GBQR member (not a release candidate after the 17:25 peak check) and its mixtures, CPU jobs:
.venv/bin/python scripts/flu_gbqr.py nowcast-tree-20261113-r01 T.real flu-gbqr-test --workers 8
.venv/bin/python scripts/flu_search_mix.py gbqrtest --members TR=T.real --experiments nowcast-tree-20261113-r01 --gbqr G=flu-gbqr-test/gbqr --groups "T.real:TR" "G:G" "T.real+G:TR,G"
sbatch --job-name=flu-mix-gbqrtest scripts/covid_tree_mix.sbatch experiments/flu-search-20261120/mix-gbqrtest.json data/experiments/flu-mix-gbqrtest
.venv/bin/python scripts/flu_phase_check.py data/experiments/flu-mix-gbqrtest/*-mixture
# Round 2 (sampled recipes, peak-oriented losses) and reseed rs01 (refs + roots, seeds 52-59), chained after round 1 (job 9989288):
python3 experiments/flu-search-20261120/rounds.py 2; python3 experiments/flu-search-20261120/rounds.py rs01   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-r02 --problem problems/us-flu-short-term-coverage.json --study $S/round-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-rs01 --problem problems/us-flu-short-term-coverage.json --study $S/reseed-rs01.json --device cuda
sbatch --job-name=flu-s-r02 --array=0-5 --dependency=afterany:9984420 scripts/flu_search.sbatch flu-s-r02 flu-s-rs01
.venv/bin/python -m chromantis.experiment.planner status -e flu-s-r02
.venv/bin/python -m chromantis.experiment.planner rank -e flu-s-r02 --allow-incomplete --no-report
