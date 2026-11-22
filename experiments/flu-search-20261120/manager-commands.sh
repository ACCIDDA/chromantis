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
# 2026-11-21 00:45-01:15 EST: round 5 scored; trajectory mixtures (CPU 10038265-6); round 6 OOM retry (job 10038254, 3 lanes); round 7 + rs04 + g07 + gs02 (job 10038284, 3 lanes)
M="--members B7=ref.A,ref.B5,ref.B Bq=Bq Bh=Bh AP=Ar.peak QS=Bq.hc.smp HS=Bh.smp --groups B7:B7 Bq+Bh+AP:Bq,Bh,AP QS+Bh+AP:QS,Bh,AP QS+HS+AP:QS,HS,AP Bq+HS+AP:Bq,HS,AP QS+HS:QS,HS QS+Bh:QS,Bh --max-seeds 8"
.venv/bin/python scripts/flu_search_mix.py r05m --experiments flu-s-r01 flu-s-r02 flu-s-r05 $M
.venv/bin/python scripts/flu_search_mix.py g05m --experiments flu-s-g01 flu-s-g04 flu-s-g05 $M
LANES=3 NTFY=0 sbatch --export=ALL --job-name=flu-s-r06-retry --array=0-4 --dependency=afterany:10029431 scripts/flu_search.sbatch flu-s-r06 flu-s-rs03 flu-s-g06
python3 experiments/flu-search-20261120/rounds.py 7; python3 experiments/flu-search-20261120/rounds.py g07; python3 experiments/flu-search-20261120/rounds.py rs04   # on the Mac (+ guard-gs02.json)
LANES=3 sbatch --export=ALL --job-name=flu-s-r07 --array=0-4 --dependency=afterany:10034275:10038254 scripts/flu_search.sbatch flu-s-r07 flu-s-rs04 flu-s-g07 flu-s-gs02
# 2026-11-21 02:05 EST: rounds 6-7 scored; round 8 (+rs05, g08, gs03; job 10040511) and round 9 amplitude augmentation (+g09) chained
python3 experiments/flu-search-20261120/rounds.py 8; python3 experiments/flu-search-20261120/rounds.py g08; python3 experiments/flu-search-20261120/rounds.py rs05   # + guard-gs03.json
LANES=3 sbatch --export=ALL --job-name=flu-s-r08 --array=0-4 --dependency=afterany:10038284 scripts/flu_search.sbatch flu-s-r08 flu-s-rs05 flu-s-g08 flu-s-gs03
python3 experiments/flu-search-20261120/rounds.py 9; python3 experiments/flu-search-20261120/rounds.py g09
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-r09 --problem problems/us-flu-short-term-coverage.json --study $S/round-09.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-g09 --problem problems/us-flu-2023-24-prescribed-coverage.json --study $S/guard-g09.json --device cuda
LANES=3 sbatch --export=ALL --job-name=flu-s-r09 --array=0-4 --dependency=afterany:10040511 scripts/flu_search.sbatch flu-s-r09 flu-s-g09
.venv/bin/python scripts/flu_search_mix.py r08m --experiments flu-s-r01 flu-s-rs01 flu-s-r02 flu-s-rs02 flu-s-r04 flu-s-r05 flu-s-rs03 flu-s-rs04 flu-s-r06 flu-s-rs05 --members "B7=ref.A,ref.B5,ref.B" Bq=Bq Bh=Bh AP=Ar.peak QL=Bq.smp.ll1 QS=Bq.hc.smp HS=Bh.smp SQ=Bq.smp --groups "B7:B7" "Bq+Bh+AP:Bq,Bh,AP" "QL+HS+AP:QL,HS,AP" "QS+HS+AP:QS,HS,AP" "QL+Bh+AP:QL,Bh,AP" "QL+QS+HS+AP:QL,QS,HS,AP" "SQ+HS+AP:SQ,HS,AP" "QL+HS:QL,HS"
# 2026-11-21 03:45-04:10 EST: round 9 scored; 24-seed confirmation rs06 + gs04 (job 10043899, 4 lanes); guard mixtures g08m; ED-membership mixtures edm/edg
python3 experiments/flu-search-20261120/rounds.py rs06   # + guard-gs04.json
LANES=4 sbatch --export=ALL --job-name=flu-s-rs06 --array=0-4 scripts/flu_search.sbatch flu-s-rs06 flu-s-gs04
.venv/bin/python scripts/flu_search_mix.py g08m --experiments flu-s-g01 flu-s-gs01 flu-s-g04 flu-s-g05 flu-s-gs02 flu-s-g06 flu-s-gs03 --members "B7=ref.A,ref.B5,ref.B" Bq=Bq Bh=Bh AP=Ar.peak QL=Bq.smp.ll1 HS=Bh.smp SQ=Bq.smp --groups "B7:B7" "Bq+Bh+AP:Bq,Bh,AP" "QL+HS+AP:QL,HS,AP" "QL+Bh+AP:QL,Bh,AP" "SQ+HS+AP:SQ,HS,AP"
G="--members B7=ref.A,ref.B5,ref.B Bq=Bq Bh=Bh AP=Ar.peak QL=Bq.smp.ll1 HS=Bh.smp B5=ref.B5 B=ref.B --groups Bq+AP:Bq,AP QL+AP:QL,AP Bq+QL+AP:Bq,QL,AP Bq+B5+AP:Bq,B5,AP QL+B+AP:QL,B,AP QL+HS+AP:QL,HS,AP B7:B7"
.venv/bin/python scripts/flu_search_mix.py edm --experiments flu-s-r01 flu-s-rs01 flu-s-r02 flu-s-rs02 flu-s-r05 flu-s-rs04 flu-s-r06 flu-s-rs05 $G
.venv/bin/python scripts/flu_search_mix.py edg --experiments flu-s-g01 flu-s-gs01 flu-s-g04 flu-s-g05 flu-s-gs02 flu-s-g06 flu-s-gs03 $G
python3 experiments/flu-search-20261120/rounds.py 10; python3 experiments/flu-search-20261120/rounds.py g10
LANES=3 sbatch --export=ALL --job-name=flu-s-r10 --array=0-4 --dependency=afterany:10043899 scripts/flu_search.sbatch flu-s-r10 flu-s-g10
LANES=4 sbatch --export=ALL --job-name=flu-s-rs07 --array=0-4 --dependency=afterany:10044019 scripts/flu_search.sbatch flu-s-rs07 flu-s-gs05   # 32-seed confirmation (seeds 68-75), main + guard
# 2026-11-21 06:10 EST: round 10 scored; Ar.peak.nokinsa reseed rs08 + gs06 (job 10045848); 24-seed mixtures m24/g24
sbatch --job-name=flu-s-rs08 --array=0-4 --dependency=afterany:10044792 scripts/flu_search.sbatch flu-s-rs08 flu-s-gs06
M="--members B7=ref.A,ref.B5,ref.B Bq=Bq Bh=Bh AP=Ar.peak QL=Bq.smp.ll1 HS=Bh.smp B=ref.B --groups B7:B7 A_QL+B+AP:QL,B,AP B_QL+HS+AP:QL,HS,AP Bq+Bh+AP:Bq,Bh,AP --max-seeds 24"
.venv/bin/python scripts/flu_search_mix.py m24 --experiments flu-s-r01 flu-s-rs01 flu-s-r02 flu-s-rs02 flu-s-r05 flu-s-rs04 flu-s-r06 flu-s-rs05 flu-s-rs06 $M
.venv/bin/python scripts/flu_search_mix.py g24 --experiments flu-s-g01 flu-s-gs01 flu-s-g04 flu-s-g05 flu-s-gs02 flu-s-g06 flu-s-gs03 flu-s-gs04 $M
LANES=4 sbatch --export=ALL --job-name=flu-s-ge01 --array=0-4 --dependency=afterany:10045848 scripts/flu_search.sbatch flu-s-ge01 flu-s-r11 flu-s-g11   # guard with 2024-25 errors; ILI on Bq.smp.ll1
# 2026-11-21 07:45-08:15 EST: round 12 + g12 (job 10047844, 3 lanes); 32-seed mixtures m32/g32 and reporting-regime guard mixtures ge01
LANES=3 sbatch --export=ALL --job-name=flu-s-r12 --array=0-4 scripts/flu_search.sbatch flu-s-r12 flu-s-g12
M="--members B7=ref.A,ref.B5,ref.B AP=Ar.peak NK=Ar.peak.nokinsa QL=Bq.smp.ll1 HS=Bh.smp B=ref.B --groups B7:B7 A:QL,B,AP A_nokinsa:QL,B,NK B:QL,HS,AP B_nokinsa:QL,HS,NK --max-seeds 32"
.venv/bin/python scripts/flu_search_mix.py m32 --experiments flu-s-r01 flu-s-rs01 flu-s-r02 flu-s-rs02 flu-s-r05 flu-s-rs04 flu-s-r06 flu-s-rs05 flu-s-rs06 flu-s-rs07 flu-s-r10 flu-s-rs08 $M
.venv/bin/python scripts/flu_search_mix.py g32 --experiments flu-s-g01 flu-s-gs01 flu-s-g04 flu-s-g05 flu-s-gs02 flu-s-g06 flu-s-gs03 flu-s-gs04 flu-s-gs05 flu-s-g10 flu-s-gs06 $M
# 2026-11-21 08:55 EST: release fits (all four seasons, seeds 42-61; NOT scored: scoring.lock created by hand), then ge02 + rs09 + gs07
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-release --problem problems/us-flu-production-coverage.json --study $S/release-seeds.json --device cuda
mkdir -p data/experiments/flu-s-release/scoring.lock   # block automatic ranking on 2026-27
LANES=4 sbatch --export=ALL --job-name=flu-s-release --array=0-4 scripts/flu_search.sbatch flu-s-release
LANES=4 sbatch --export=ALL --job-name=flu-s-ge02 --array=0-4 --dependency=afterany:10051356 scripts/flu_search.sbatch flu-s-ge02 flu-s-rs09 flu-s-gs07
# 2026-11-21 09:55 EST: in-season retraining test on finalized inputs (frozen vs rolling origin, 2025-26), job 10054265
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-frozen --problem problems/us-flu-2025-26-finalized-coverage.json --study $S/inseason.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-inseason --problem problems/us-flu-2025-26-inseason-finalized-coverage.json --study $S/inseason.json --device cuda
sbatch --job-name=flu-s-inseason --array=0-4 --dependency=afterany:10051407 scripts/flu_search.sbatch flu-s-frozen flu-s-inseason
# 2026-11-21 10:40-11:10 EST: in-season test scored on common tasks; release seeds 62-81 (unscored); round 13 widths
.venv/bin/python scripts/flu_common_tasks.py flu-s-frozen flu-s-inseason
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-release2 --problem problems/us-flu-production-coverage.json --study $S/release-seeds-2.json --device cuda; mkdir -p data/experiments/flu-s-release2/scoring.lock
LANES=4 sbatch --export=ALL --job-name=flu-s-release2 --array=0-4 scripts/flu_search.sbatch flu-s-release2
LANES=3 sbatch --export=ALL --job-name=flu-s-r13 --array=0-4 --dependency=afterany:10058624 scripts/flu_search.sbatch flu-s-r13 flu-s-g13
# 2026-11-21 11:50 EST: 8-week training test and Ar.peak.nokinsa seeds 68-75 (job 10063968)
.venv/bin/python -m chromantis.experiment.planner plan -e flu-s-h8 --problem problems/us-flu-short-term-coverage-h8.json --study $S/h8.json --device cuda
LANES=3 sbatch --export=ALL --job-name=flu-s-h8 --array=0-4 --dependency=afterany:10058714 scripts/flu_search.sbatch flu-s-h8 flu-s-rs10 flu-s-gs08
LANES=3 sbatch --export=ALL --job-name=flu-s-h8g --array=0-4 --dependency=afterany:10063968 scripts/flu_search.sbatch flu-s-h8g   # 8-week test guard
.venv/bin/python scripts/flu_h8_compare.py main; .venv/bin/python scripts/flu_h8_compare.py guard
LANES=4 sbatch --export=ALL --job-name=flu-s-release3 --array=0-4 scripts/flu_search.sbatch flu-s-release3   # Bh.smp release seeds 62-81, unscored
# 2026-11-21 14:45-15:05 EST: round 14 random search (job 10083784, 3 lanes); quantile-member swap mixtures swap/swapg
python3 experiments/flu-search-20261120/rounds.py 14; python3 experiments/flu-search-20261120/rounds.py g14
LANES=3 sbatch --export=ALL --job-name=flu-s-r14 --array=0-4 scripts/flu_search.sbatch flu-s-r14 flu-s-g14
LANES=3 sbatch --export=ALL --job-name=flu-s-r15 --array=0-4 --dependency=afterany:10083784 scripts/flu_search.sbatch flu-s-r15 flu-s-g15   # ED handling
LANES=4 sbatch --export=ALL --job-name=flu-s-rs11 --array=0-4 --dependency=afterany:10106015 scripts/flu_search.sbatch flu-s-rs11 flu-s-gs09   # seeds 76-91 for final 48-seed comparisons
LANES=3 sbatch --export=ALL --job-name=flu-s-r16 --array=0-4 --dependency=afterany:10120397 scripts/flu_search.sbatch flu-s-r16 flu-s-g16   # spatial axis on A members, 16 seeds
LANES=4 sbatch --export=ALL --job-name=flu-s-rl01 --array=0-4 --dependency=afterany:10135701 scripts/flu_search.sbatch flu-s-rl01   # old (leaky) error_reference protocol for B7 and A members
LANES=3 sbatch --export=ALL --job-name=flu-s-rs12 --array=0-4 --dependency=afterany:10148043 scripts/flu_search.sbatch flu-s-rs12 flu-s-gs10   # Bq.smp.ll1.nosp seeds 60-75
