# covid-rsv-search-20261124. Longleaf campaign folder (shares panels and .venv with the flu search):
#   /hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113
# From the Mac: send code, problems, datasets and the study
rsync -a --exclude __pycache__ --exclude .DS_Store src scripts problems datasets chadi@longleaf.unc.edu:/hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113/
rsync -a experiments/covid-rsv-search-20261124 chadi@longleaf.unc.edu:/hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113/experiments/
# Write study files on the Mac (pathogen, round number | guard tag | reseed tag)
python3 experiments/covid-rsv-search-20261124/rounds.py covid 1; python3 experiments/covid-rsv-search-20261124/rounds.py rsv 1
python3 experiments/covid-rsv-search-20261124/rounds.py covid g01; python3 experiments/covid-rsv-search-20261124/rounds.py rsv g01
# On Longleaf, in the campaign folder:
export PYTHONPATH=src
S=experiments/covid-rsv-search-20261124
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r01 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r01 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g01 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g01 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g01.json --device cuda
sbatch --job-name=crs-r01 --array=0-5 scripts/flu_search.sbatch cv-s-r01:4 rv-s-r01:8 cv-s-g01:4 rv-s-g01:8
# 2026-11-24 11:50 EST: round 1 launched as job 10666606 (element 5 waits for the GPU of another lab member).
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rs01 --problem problems/us-covid-short-term-coverage.json --study $S/covid-reseed-rs01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs01 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs01.json --device cuda
sbatch --job-name=crs-rs01 --array=0-5 scripts/flu_search.sbatch cv-s-rs01:4 rv-s-rs01:8
# 2026-11-24 11:53 EST: reseed rs01 queued as job 10666698 (no dependency: takes GPUs as round 1's elements finish).
# Check and score
squeue -u chadi
.venv/bin/python -m chromantis.experiment.planner status -e cv-s-r01
.venv/bin/python -m chromantis.experiment.planner status -e rv-s-r01
.venv/bin/python -m chromantis.experiment.planner rank -e cv-s-r01 --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner rank -e rv-s-r01 --allow-incomplete --no-report
.venv/bin/python scripts/flu_search_table.py --pathogen covid --parents "$S/covid-round-*.json" -e cv-s-r01 -e cv-s-rs01 --guard cv-s-g01 --out output/crs-search/covid-r01.csv
.venv/bin/python scripts/flu_search_table.py --pathogen rsv --parents "$S/rsv-round-*.json" -e rv-s-r01 -e rv-s-rs01 --guard rv-s-g01 --out output/crs-search/rsv-r01.csv
# 2026-11-24 13:35 EST: Google Trends for COVID/RSV (Mac pull, then panels on Longleaf), round 2 queued as job 10674043
#   (on the Mac) .../gt/bin/python scripts/pull_google_trends.py --terms covid rsv --out data/raw/google_trends
rsync -a data/raw/google_trends/ chadi@longleaf.unc.edu:/hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113/data/raw/google_trends/
.venv/bin/python scripts/add_google_trends.py data/processed/panel-coverage.npz data/raw/google_trends data/processed/panel-coverage-cgt.npz covid_symptoms covid_test
.venv/bin/python scripts/add_google_trends.py data/processed/panel-coverage-rsv.npz data/raw/google_trends data/processed/panel-coverage-rsv-gt.npz rsv rsv_symptoms
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r02 --problem problems/us-covid-short-term-coverage-gt.json --study $S/covid-round-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r02 --problem problems/us-rsv-short-term-coverage-gt.json --study $S/rsv-round-02.json --device cuda
sbatch --job-name=crs-r02 --array=0-5 scripts/flu_search.sbatch cv-s-r02:4 rv-s-r02:8
.venv/bin/python scripts/flu_search_table.py --pathogen covid --parents "$S/covid-round-*.json" -e cv-s-r01 -e cv-s-r02 --guard cv-s-g01
