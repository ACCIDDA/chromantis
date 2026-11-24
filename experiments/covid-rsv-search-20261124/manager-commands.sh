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
# 2026-11-24 14:00 EST: COVID round 1 scored; round 3 queued (job 10677721); mixtures c01 (CPU job 10677723)
python3 experiments/covid-rsv-search-20261124/rounds.py covid 3   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r03 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-03.json --device cuda
sbatch --job-name=crs-r03 --array=0-5 scripts/flu_search.sbatch cv-s-r03:4
.venv/bin/python scripts/flu_search_mix.py c01 --study $S --prefix crs-mix --experiments cv-s-r01 --max-seeds 8 --members P=ref.Ah,ref.pN,ref.N,ref.Bh L=T,Tl,S T=T N=ref.N S=S E=Tl.esall B=ref.Bh --groups 'prod4:P' 'nov20:L' 'T:T' 'T+N:T,N' 'T+N+S:T,N,S' 'T+N+E:T,N,E' 'T+N+B:T,N,B' 'T+S:T,S'
sbatch --job-name=crs-mix-c01 scripts/covid_tree_mix.sbatch $S/mix-c01.json data/experiments/crs-mix-c01
# 2026-11-24 15:00 EST: RSV round 1 scored; guard fix (ranking.py) and retries; RSV round 3 + guard g03 queued (job 10688103)
python3 experiments/covid-rsv-search-20261124/rounds.py rsv 3; python3 experiments/covid-rsv-search-20261124/rounds.py rsv g03   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r03 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-03.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g03 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g03.json --device cuda
sbatch --job-name=crs-r03b --array=0-5 scripts/flu_search.sbatch rv-s-r03:8 cv-s-g01:4 rv-s-g01:8 rv-s-g03:8
.venv/bin/python scripts/flu_search_table.py --pathogen rsv --parents "$S/rsv-round-*.json" -e rv-s-r01 -e rv-s-r03 --guard rv-s-g01 --guard rv-s-g03
# 2026-11-24 15:45 EST: guard rescoring, RSV reseed rs02 (job 10694722), COVID 16-seed mixtures c02 (CPU job 10694723)
sbatch --job-name=cv-s-g01-score scripts/flu_search_score.sbatch cv-s-g01
python3 experiments/covid-rsv-search-20261124/rounds.py rsv rs02   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs02 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs02.json --device cuda
sbatch --job-name=crs-rs02 --array=0-5 scripts/flu_search.sbatch rv-s-rs02:8
.venv/bin/python scripts/flu_search_mix.py c02 --study $S --prefix crs-mix --experiments cv-s-r01 cv-s-rs01 --max-seeds 16 --members P=ref.Ah,ref.pN,ref.N,ref.Bh L=T,Tl,S T=T N=ref.N S=S --groups 'prod4:P' 'nov20:L' 'T+N:T,N' 'T+N+S:T,N,S'
sbatch --job-name=crs-mix-c02 scripts/covid_tree_mix.sbatch $S/mix-c02.json data/experiments/crs-mix-c02
# 2026-11-24 16:55 EST: RSV sampled runs requeued at 4 lanes (job 10703999, 10694722 cancelled); RSV round 4 + gt guard g04,
# COVID guard seeds g02, COVID reseed rs02 (job 10704128); mixtures c03 (10704131) and guard mixtures c01g (10704133)
sbatch --job-name=crs-rs02b --array=0-5 scripts/flu_search.sbatch rv-s-g03:8 rv-s-r03:4 rv-s-rs02:4
python3 $S/rounds.py rsv 4; python3 $S/rounds.py rsv g04; python3 $S/rounds.py covid g02; python3 $S/rounds.py covid rs02   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r04 --problem problems/us-rsv-short-term-coverage-gt.json --study $S/rsv-round-04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g04 --problem problems/us-rsv-2023-24-prescribed-coverage-gt.json --study $S/rsv-guard-g04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g02 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rs02 --problem problems/us-covid-short-term-coverage.json --study $S/covid-reseed-rs02.json --device cuda
sbatch --job-name=crs-r04 --array=0-5 scripts/flu_search.sbatch rv-s-r04:4 rv-s-g04:4 cv-s-g02:4 cv-s-rs02:4
.venv/bin/python scripts/flu_search_mix.py c03 --study $S --prefix crs-mix --experiments cv-s-r01 cv-s-r03 --max-seeds 8 --members P=ref.Ah,ref.pN,ref.N,ref.Bh T=T N=ref.N S=S NS=N.smp NR=N.real --groups 'prod4:P' 'T+N+S:T,N,S' 'N:N' 'N+S:N,S' 'N+NS:N,NS' 'T+N+NS:T,N,NS' 'T+NR+S:T,NR,S' 'T+N+NR+S:T,N,NR,S'
sbatch --job-name=crs-mix-c03 scripts/covid_tree_mix.sbatch $S/mix-c03.json data/experiments/crs-mix-c03
.venv/bin/python scripts/flu_search_mix.py c01g --study $S --prefix crs-mix --experiments cv-s-g01 --max-seeds 8 --members P=ref.Ah,ref.pN,ref.N,ref.Bh L=T,Tl,S T=T N=ref.N S=S --groups 'prod4:P' 'nov20:L' 'T+N:T,N' 'T+N+S:T,N,S' 'N+S:N,S'
sbatch --job-name=crs-mix-c01g scripts/covid_tree_mix.sbatch $S/mix-c01g.json data/experiments/crs-mix-c01g
.venv/bin/python scripts/crs_mix_table.py data/experiments/crs-mix-c02/ranking/headline-season-scores.csv   # mixture table (scratch helper)
