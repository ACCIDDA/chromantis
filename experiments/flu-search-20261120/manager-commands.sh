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
# 2026-11-20 19:45 EST: round 1 scored; round 3 + guard g03 chained after round 2 (job 10006055); round-1 mixtures (CPU job 10006061)
.venv/bin/python scripts/flu_search_table.py -e flu-s-r01 --guard flu-s-g01 --out output/flu-search/r01.csv
python3 experiments/flu-search-20261120/rounds.py 3; python3 experiments/flu-search-20261120/rounds.py g03   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-r03 --problem problems/us-flu-short-term-coverage.json --study $S/round-03.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-g03 --problem problems/us-flu-2023-24-prescribed-coverage.json --study $S/guard-g03.json --device cuda
sbatch --job-name=flu-s-r03 --array=0-4 --dependency=afterany:9989288 scripts/flu_search.sbatch flu-s-r03 flu-s-g03
.venv/bin/python scripts/flu_search_mix.py r01 --experiments flu-s-r01 --members "B7=ref.A,ref.B5,ref.B" Bes=ref.Bes G=Bq.gru L=Bq.ll1 Ar=Ar Bh=Bh Bq=Bq --groups "B7:B7" "Bes:Bes" "Bq.gru:G" "Ar:Ar" "Bh:Bh" "G+Ar:G,Ar" "G+Bh:G,Bh" "G+Bh+Ar:G,Bh,Ar" "G+L+Ar:G,L,Ar" "Ar+Bh:Ar,Bh" "Bq+Ar:Bq,Ar"
sbatch --job-name=flu-mix-r01 scripts/covid_tree_mix.sbatch experiments/flu-search-20261120/mix-r01.json data/experiments/flu-mix-r01
# 2026-11-20 20:45 EST: round 2 scored; round 4, reseed rs02 and guard g04 chained after round 3 (job 10012749)
.venv/bin/python scripts/flu_search_table.py -e flu-s-r01 -e flu-s-r02 --guard flu-s-g01 --out output/flu-search/r02.csv
python3 experiments/flu-search-20261120/rounds.py 4; python3 experiments/flu-search-20261120/rounds.py g04; python3 experiments/flu-search-20261120/rounds.py rs02   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-r04 --problem problems/us-flu-short-term-coverage.json --study $S/round-04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-rs02 --problem problems/us-flu-short-term-coverage.json --study $S/reseed-rs02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-g04 --problem problems/us-flu-2023-24-prescribed-coverage.json --study $S/guard-g04.json --device cuda
sbatch --job-name=flu-s-r04 --array=0-4 --dependency=afterany:10006055 scripts/flu_search.sbatch flu-s-r04 flu-s-rs02 flu-s-g04
# 2026-11-20 21:55 EST: round 3 + guards scored; OOM retry for round 4 (3 lanes per GPU, job 10022195); guard mixtures (CPU job 10022208)
.venv/bin/python scripts/flu_search_table.py -e flu-s-r01 -e flu-s-r02 -e flu-s-r03 --guard flu-s-g01 --guard flu-s-g03 --out output/flu-search/r03.csv
.venv/bin/python scripts/flu_search_table.py -e flu-s-r01 -e flu-s-rs01 --guard flu-s-g01
LANES=3 NTFY=0 sbatch --export=ALL --job-name=flu-s-r04-retry --array=0-4 --dependency=afterany:10012749 scripts/flu_search.sbatch flu-s-r04 flu-s-g04
.venv/bin/python scripts/flu_search_mix.py g01 --experiments flu-s-g01 flu-s-g03 --members "B7=ref.A,ref.B5,ref.B" Bes=ref.Bes G=Bq.gru L=Bq.ll1 Ar=Ar Bh=Bh Bq=Bq B=ref.B --groups "B7:B7" "Bes:Bes" "Bq.gru:G" "Bh:Bh" "Bq:Bq" "ref.B:B" "Ar:Ar" "G+Bh:G,Bh" "G+L+Ar:G,L,Ar" "Bq+Bh:Bq,Bh" "Bh+Ar:Bh,Ar" "Bq+Bh+Ar:Bq,Bh,Ar"
# 2026-11-20 22:20-22:50 EST: three-season mixtures; round 5 + g05 (job 10022573, 4 lanes) and round 6 + rs03 + g06 (job 10029431, 6 lanes) chained
.venv/bin/python scripts/flu_search_mix.py r01s16 --experiments flu-s-r01 flu-s-rs01 --members "B7=ref.A,ref.B5,ref.B" Bes=ref.Bes Ar=Ar Bh=Bh Bq=Bq B=ref.B --groups "B7:B7" "Bes:Bes" "Bh:Bh" "Bq:Bq" "ref.B:B" "Bq+Bh:Bq,Bh" "Bq+Bh+Ar:Bq,Bh,Ar" "B+Bh:B,Bh" "Bh+Ar:Bh,Ar" "Bes+Bh:Bes,Bh"
.venv/bin/python scripts/flu_phase_check.py data/experiments/flu-mix-r01s16/*-mixture
python3 experiments/flu-search-20261120/rounds.py 5; python3 experiments/flu-search-20261120/rounds.py g05   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-r05 --problem problems/us-flu-short-term-coverage.json --study $S/round-05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-g05 --problem problems/us-flu-2023-24-prescribed-coverage.json --study $S/guard-g05.json --device cuda
LANES=4 sbatch --export=ALL --job-name=flu-s-r05 --array=0-4 --dependency=afterany:10022195 scripts/flu_search.sbatch flu-s-r05 flu-s-g05
python3 experiments/flu-search-20261120/rounds.py 6; python3 experiments/flu-search-20261120/rounds.py g06; python3 experiments/flu-search-20261120/rounds.py rs03   # on the Mac
LANES=6 sbatch --export=ALL --job-name=flu-s-r06 --array=0-4 --dependency=afterany:10022573 scripts/flu_search.sbatch flu-s-r06 flu-s-rs03 flu-s-g06
# 2026-11-21 00:30 EST: round 4 + guard re-ranked after the OOM retry; mixtures with Ar.peak (CPU jobs 10033651-2)
.venv/bin/python scripts/flu_search_table.py -e flu-s-r01 -e flu-s-r02 -e flu-s-r03 -e flu-s-r04 -e flu-s-rs01 -e flu-s-rs02 --guard flu-s-g01 --guard flu-s-g03 --guard flu-s-g04 --out output/flu-search/r04.csv
.venv/bin/python scripts/flu_search_mix.py r04m --experiments flu-s-r01 flu-s-rs01 flu-s-r02 flu-s-rs02 --members "B7=ref.A,ref.B5,ref.B" Bq=Bq Bh=Bh AP=Ar.peak BP=B5r.peak --groups "B7:B7" "Bq+Bh:Bq,Bh" "Bq+Bh+AP:Bq,Bh,AP" "Bh+AP:Bh,AP" "Bq+AP:Bq,AP" "Bq+Bh+AP+BP:Bq,Bh,AP,BP" "AP:AP"
.venv/bin/python scripts/flu_search_mix.py g04m --experiments flu-s-g01 flu-s-g04 --members "B7=ref.A,ref.B5,ref.B" Bq=Bq Bh=Bh AP=Ar.peak BP=B5r.peak --groups "B7:B7" "Bq+Bh:Bq,Bh" "Bq+Bh+AP:Bq,Bh,AP" "Bh+AP:Bh,AP" "Bq+AP:Bq,AP" "Bq+Bh+AP+BP:Bq,Bh,AP,BP" "AP:AP"
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-gs01 --problem problems/us-flu-2023-24-prescribed-coverage.json --study $S/guard-gs01.json --device cuda; sbatch --job-name=flu-s-gs01 --array=0-4 --dependency=afterany:10029431 scripts/flu_search.sbatch flu-s-gs01
