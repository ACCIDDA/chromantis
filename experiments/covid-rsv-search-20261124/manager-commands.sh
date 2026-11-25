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
# 2026-11-24 17:50 EST: RSV round 5 + guard g05 + reseed rs03 (job 10709697); RSV mixtures r01 (10709698), guard mixtures r01g (10709699)
python3 $S/rounds.py rsv 5; python3 $S/rounds.py rsv g05; python3 $S/rounds.py rsv rs03   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r05 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g05 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs03 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs03.json --device cuda
sbatch --job-name=crs-r05 --array=0-5 scripts/flu_search.sbatch rv-s-r05:6 rv-s-g05:6 rv-s-rs03:6
.venv/bin/python scripts/flu_search_mix.py r01 --study $S --prefix crs-mix --experiments rv-s-r01 rv-s-r03 --max-seeds 8 --members P=ref.Ball,ref.Bw,ref.A4c0,ref.A4i L=Rc,R1 Q=Bwq QS=Bwq.smp Rc=Rc RR=Rc.real A=ref.A4c0 --groups 'prod4:P' 'nov20:L' 'QS:QS' 'Q+Rc:Q,Rc' 'QS+Rc:QS,Rc' 'Q+QS+Rc:Q,QS,Rc' 'QS+RR:QS,RR' 'Q+QS+RR:Q,QS,RR' 'Q+QS+Rc+A:Q,QS,Rc,A'
sbatch --job-name=crs-mix-r01 scripts/covid_tree_mix.sbatch $S/mix-r01.json data/experiments/crs-mix-r01
.venv/bin/python scripts/flu_search_mix.py r01g --study $S --prefix crs-mix --experiments rv-s-g01 rv-s-g03 --max-seeds 8 --members P=ref.Ball,ref.Bw,ref.A4c0,ref.A4i L=Rc,R1 Q=Bwq QS=Bwq.smp Rc=Rc --groups 'prod4:P' 'nov20:L' 'Q+Rc:Q,Rc' 'QS+Rc:QS,Rc' 'Q+QS+Rc:Q,QS,Rc'
sbatch --job-name=crs-mix-r01g scripts/covid_tree_mix.sbatch $S/mix-r01g.json data/experiments/crs-mix-r01g
# 2026-11-24 18:45 EST: finalist seeds (COVID rs03 + g03, RSV rs04 + g06; job 10718486); COVID 16-seed mixtures main c04 (10718488), guard c02g (10718487)
for a in "covid rs03" "covid g03" "rsv rs04" "rsv g06"; do python3 $S/rounds.py $a; done   # on the Mac (bash)
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rs03 --problem problems/us-covid-short-term-coverage.json --study $S/covid-reseed-rs03.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g03 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g03.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs04 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g06 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g06.json --device cuda
sbatch --job-name=crs-rs03 --array=0-5 scripts/flu_search.sbatch rv-s-rs04:4 rv-s-g06:4 cv-s-rs03:4 cv-s-g03:4
.venv/bin/python scripts/flu_search_mix.py c04 --study $S --prefix crs-mix --experiments cv-s-r01 cv-s-rs01 --max-seeds 16 --members P=ref.Ah,ref.pN,ref.N,ref.Bh PT=ref.Ah,T,ref.N,ref.Bh T=T N=ref.N S=S pN=ref.pN --groups 'prod4:P' 'prod4T:PT' 'prod4+T:P,T' 'T+N+S:T,N,S' 'T+N:T,N' 'N+pN+S:N,pN,S' 'T+N+pN:T,N,pN' 'T+N+S+pN:T,N,S,pN'
sbatch --job-name=crs-mix-c04 scripts/covid_tree_mix.sbatch $S/mix-c04.json data/experiments/crs-mix-c04
# guard version: same groups with --experiments cv-s-g01 cv-s-g02, name c02g
sbatch --job-name=crs-mix-c02g scripts/covid_tree_mix.sbatch $S/mix-c02g.json data/experiments/crs-mix-c02g
# 2026-11-24 19:50 EST: RSV round 6, reseeds rs05/rs06, guard g07 (job 10724990); RSV mixtures r02 (CPU job 10724993)
for a in "rsv 6" "rsv rs05" "rsv rs06" "rsv g07"; do python3 $S/rounds.py $a; done   # on the Mac (bash)
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r06 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-06.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs05 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs06 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs06.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g07 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g07.json --device cuda
sbatch --job-name=crs-r06 --array=0-5 scripts/flu_search.sbatch rv-s-g07:6 rv-s-r06:6 rv-s-rs05:6 rv-s-rs06:6
.venv/bin/python scripts/flu_search_mix.py r02 --study $S --prefix crs-mix --experiments rv-s-r01 rv-s-r03 rv-s-r05 --max-seeds 8 --members P=ref.Ball,ref.Bw,ref.A4c0,ref.A4i PN=ref.Ball,Bw.nat,ref.A4c0,A4i.nat BN=Bw.nat AN=A4i.nat QS=Bwq.smp Rc=Rc A=ref.A4c0 Q=Bwq --groups "prod4:P" "prodnat:PN" "BN+AN:BN,AN" "BN+AN+Rc:BN,AN,Rc" "QS+AN:QS,AN" "QS+AN+Rc:QS,AN,Rc" "BN+QS+AN+Rc:BN,QS,AN,Rc" "Q+QS+Rc+A:Q,QS,Rc,A"
sbatch --job-name=crs-mix-r02 scripts/covid_tree_mix.sbatch $S/mix-r02.json data/experiments/crs-mix-r02
# 2026-11-24 20:45 EST: COVID round 4 and RSV round 7 queued (job 10729461)
python3 $S/rounds.py covid 4; python3 $S/rounds.py rsv 7   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r04 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r07 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-07.json --device cuda
sbatch --job-name=crs-r07 --array=0-5 scripts/flu_search.sbatch cv-s-r04:4 rv-s-r07:4
# 2026-11-24 21:45 EST: COVID 32-seed main (c05, CPU job 10733139) and 24-seed guard mixtures (c03g, 10733140); RSV round 8 + guard g08 (job 10733166)
M="P=ref.Ah,ref.pN,ref.N,ref.Bh T=T N=ref.N S=S pN=ref.pN"
.venv/bin/python scripts/flu_search_mix.py c05 --study $S --prefix crs-mix --experiments cv-s-r01 cv-s-rs01 cv-s-rs02 cv-s-rs03 --max-seeds 32 --members $M --groups "prod4:P" "prod4+T:P,T" "T+N+S:T,N,S" "T+N:T,N" "N+pN+S:N,pN,S" "T+N+S+pN:T,N,S,pN"
sbatch --job-name=crs-mix-c05 scripts/covid_tree_mix.sbatch $S/mix-c05.json data/experiments/crs-mix-c05
.venv/bin/python scripts/flu_search_mix.py c03g --study $S --prefix crs-mix --experiments cv-s-g01 cv-s-g02 cv-s-g03 --max-seeds 24 --members $M --groups "prod4:P" "prod4+T:P,T" "T+N+S:T,N,S" "T+N:T,N" "N+pN+S:N,pN,S" "T+N+S+pN:T,N,S,pN"
sbatch --job-name=crs-mix-c03g scripts/covid_tree_mix.sbatch $S/mix-c03g.json data/experiments/crs-mix-c03g
python3 $S/rounds.py rsv 8; python3 $S/rounds.py rsv g08   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r08 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-08.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g08 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g08.json --device cuda
sbatch --job-name=crs-r08 --array=0-5 scripts/flu_search.sbatch rv-s-g08:6 rv-s-r08:6
# 2026-11-24 22:50 EST: Bw.nat.smp guard g09 + reseed rs07, all-season release fits rv-s-rel / cv-s-rel (seeds 42-61), job 10737452
for a in "rsv rs07" "rsv rel" "covid rel" "rsv g09"; do python3 $S/rounds.py $a; done   # on the Mac (bash)
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g09 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g09.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs07 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs07.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rel --problem problems/us-rsv-production-coverage.json --study $S/rsv-reseed-rel.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rel --problem problems/us-covid-production-coverage.json --study $S/covid-reseed-rel.json --device cuda
sbatch --job-name=crs-rel --array=0-5 scripts/flu_search.sbatch rv-s-g09:4 rv-s-rs07:4 rv-s-rel:4 cv-s-rel:4
# peak-window check of the COVID mixtures (CPU job 10737453)
sbatch --job-name=crs-phase --partition=jlessler --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/crs-search/phase-c05.txt --wrap "PYTHONPATH=src .venv/bin/python scripts/flu_phase_check.py data/experiments/crs-mix-c05/*-mixture"
# 2026-11-24 23:45 EST: RSV 24-seed mixtures main r03 (CPU job 10744647) and guard r03g (10744648)
M="P=ref.Ball,ref.Bw,ref.A4c0,ref.A4i PB=ref.Ball,Bw.nat,ref.A4c0,ref.A4i PN=ref.Ball,Bw.nat,ref.A4c0,A4i.nat PS=ref.Ball,Bw.nat.smp,ref.A4c0,A4i.nat BN=Bw.nat AN=A4i.nat BS=Bw.nat.smp"
GR=("prod4:P" "prodBnat:PB" "prodnat:PN" "prodnat-smp:PS" "BN+AN:BN,AN" "BS+AN:BS,AN")
.venv/bin/python scripts/flu_search_mix.py r03 --study $S --prefix crs-mix --experiments rv-s-r01 rv-s-r03 rv-s-r05 rv-s-r07 rv-s-rs01 rv-s-rs03 rv-s-rs04 rv-s-rs05 rv-s-rs06 rv-s-rs07 --max-seeds 24 --members $M --groups "${GR[@]}"
sbatch --job-name=crs-mix-r03 scripts/covid_tree_mix.sbatch $S/mix-r03.json data/experiments/crs-mix-r03
.venv/bin/python scripts/flu_search_mix.py r03g --study $S --prefix crs-mix --experiments rv-s-g01 rv-s-g06 rv-s-g07 rv-s-g08 rv-s-g09 --max-seeds 24 --members $M --groups "${GR[@]}"
sbatch --job-name=crs-mix-r03g scripts/covid_tree_mix.sbatch $S/mix-r03g.json data/experiments/crs-mix-r03g
# 2026-11-25 00:45 EST: release seeds 62-81 (job 10750562); RSV peak-window check (CPU job 10750528)
python3 $S/rounds.py rsv rel2; python3 $S/rounds.py covid rel2   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rel2 --problem problems/us-rsv-production-coverage.json --study $S/rsv-reseed-rel2.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rel2 --problem problems/us-covid-production-coverage.json --study $S/covid-reseed-rel2.json --device cuda
sbatch --job-name=crs-rel2 --array=0-5 scripts/flu_search.sbatch rv-s-rel2:4 cv-s-rel2:4
sbatch --job-name=crs-phase-r --partition=jlessler --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/crs-search/phase-r03.txt --wrap "PYTHONPATH=src .venv/bin/python scripts/flu_phase_check.py data/experiments/crs-mix-r03/*-mixture"
# 2026-11-25 01:45 EST: per-task phase tables + bootstrap (CPU job 10754918); 32-seed checks rs08/g10/g04 (job 10754932)
sbatch --job-name=crs-phase2 --partition=jlessler --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/crs-search/phase2.log --wrap 'PYTHONPATH=src .venv/bin/python scripts/flu_phase_check.py --out output/crs-search/tasks-r03.csv data/experiments/crs-mix-r03/*-mixture >/dev/null && PYTHONPATH=src .venv/bin/python scripts/flu_phase_check.py --out output/crs-search/tasks-c05.csv data/experiments/crs-mix-c05/*-mixture >/dev/null'
.venv/bin/python scripts/crs_phase_diff.py output/crs-search/tasks-r03.csv "prod4 [24 seeds]-mixture" "prodnat [24 seeds]-mixture"
python3 $S/rounds.py rsv rs08; python3 $S/rounds.py rsv g10; python3 $S/rounds.py covid g04   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs08 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs08.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g10 --problem problems/us-rsv-2023-24-prescribed-coverage.json --study $S/rsv-guard-g10.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g04 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g04.json --device cuda
sbatch --job-name=crs-s32 --array=0-5 scripts/flu_search.sbatch rv-s-rs08:4 rv-s-g10:4 cv-s-g04:4
# 2026-11-25 02:50 EST: phase bootstrap (all phases added); COVID round 5 + RSV round 9 queued (job 10758357)
.venv/bin/python scripts/crs_phase_diff.py output/crs-search/tasks-c05.csv "prod4 [32 seeds]-mixture" "prod4+T [32 seeds]-mixture"
python3 $S/rounds.py covid 5; python3 $S/rounds.py rsv 9   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r05 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r09 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-09.json --device cuda
sbatch --job-name=crs-r09 --array=0-5 scripts/flu_search.sbatch rv-s-r09:4 cv-s-r05:4
# 2026-11-25 03:50 EST: 32-seed final mixtures (c04g 10761392, r04 10761393, r04g 10761394); COVID round 6 + RSV round 10 (job 10761417)
.venv/bin/python scripts/flu_search_mix.py c04g --study $S --prefix crs-mix --experiments cv-s-g01 cv-s-g02 cv-s-g03 cv-s-g04 --max-seeds 32 --members P=ref.Ah,ref.pN,ref.N,ref.Bh T=T N=ref.N S=S pN=ref.pN --groups "prod4:P" "prod4+T:P,T" "T+N+S:T,N,S" "N+pN+S:N,pN,S"
sbatch --job-name=crs-mix-c04g scripts/covid_tree_mix.sbatch $S/mix-c04g.json data/experiments/crs-mix-c04g
M="P=ref.Ball,ref.Bw,ref.A4c0,ref.A4i PB=ref.Ball,Bw.nat,ref.A4c0,ref.A4i PN=ref.Ball,Bw.nat,ref.A4c0,A4i.nat"; GR=("prod4:P" "prodBnat:PB" "prodnat:PN")
.venv/bin/python scripts/flu_search_mix.py r04 --study $S --prefix crs-mix --experiments rv-s-r01 rv-s-r03 rv-s-r05 rv-s-rs01 rv-s-rs03 rv-s-rs04 rv-s-rs05 rv-s-rs06 rv-s-rs08 --max-seeds 32 --members $M --groups "${GR[@]}"
sbatch --job-name=crs-mix-r04 scripts/covid_tree_mix.sbatch $S/mix-r04.json data/experiments/crs-mix-r04
.venv/bin/python scripts/flu_search_mix.py r04g --study $S --prefix crs-mix --experiments rv-s-g01 rv-s-g06 rv-s-g07 rv-s-g08 rv-s-g10 --max-seeds 32 --members $M --groups "${GR[@]}"
sbatch --job-name=crs-mix-r04g scripts/covid_tree_mix.sbatch $S/mix-r04g.json data/experiments/crs-mix-r04g
python3 $S/rounds.py covid 6; python3 $S/rounds.py rsv 10   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r06 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-06.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r10 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-10.json --device cuda
sbatch --job-name=crs-r10 --array=0-5 scripts/flu_search.sbatch rv-s-r10:4 cv-s-r06:4
# 2026-11-25 04:50 EST: disjoint 8-seed block mixtures (seed SE of mixture differences; 16 CPU jobs, see protocol); joint-network rounds (job 10764153)
#   e.g. .venv/bin/python scripts/flu_search_mix.py cb2 --study $S --prefix crs-mix --max-seeds 8 --experiments cv-s-rs01 --members P=ref.Ah,ref.pN,ref.N,ref.Bh T=T N=ref.N S=S pN=ref.pN --groups "prod4:P" "prod4+T:P,T" "T+N+S:T,N,S" "N+pN+S:N,pN,S"
#   blocks: COVID main cv-s-r01 | cv-s-rs01 | cv-s-rs02 | cv-s-rs03; guard cv-s-g01..g04; RSV main r01+r03+r05 | rs01+rs03+rs05 | rs04+rs06+rs05 | rs08; guard g01+g07 | g06+g07 | g08 | g10
python3 $S/rounds.py covid 7; python3 $S/rounds.py rsv 11   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r07 --problem problems/us-respiratory-joint-short-term-coverage.json --study $S/covid-round-07.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r11 --problem problems/us-respiratory-joint-short-term-coverage.json --study $S/rsv-round-11.json --device cuda
sbatch --job-name=crs-joint --array=0-5 scripts/flu_search.sbatch rv-s-r11:4 cv-s-r07:4
# 2026-11-25 05:45 EST: block seed errors (scripts/crs_block_se.py); joint RSV seeds rs09 + joint guard g11 (job 10767854); joint mix test rj1 (CPU 10767856)
python3 scripts/crs_block_se.py
python3 $S/rounds.py rsv rs09; python3 $S/rounds.py rsv g11   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs09 --problem problems/us-respiratory-joint-short-term-coverage.json --study $S/rsv-reseed-rs09.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-g11 --problem problems/us-respiratory-joint-2023-24-prescribed-coverage.json --study $S/rsv-guard-g11.json --device cuda
sbatch --job-name=crs-joint2 --array=0-5 scripts/flu_search.sbatch rv-s-rs09:4 rv-s-g11:4
.venv/bin/python scripts/flu_search_mix.py rj1 --study $S --prefix crs-mix --max-seeds 8 --experiments rv-s-r01 rv-s-r03 rv-s-r05 rv-s-r11 --members P=ref.Ball,ref.Bw,ref.A4c0,ref.A4i PN=ref.Ball,Bw.nat,ref.A4c0,A4i.nat PJ=ref.Ball,Bw.nat.joint,ref.A4c0,A4i.nat.joint PJB=ref.Ball,Bw.nat.joint,ref.A4c0,A4i.nat --groups "prod4:P" "prodnat:PN" "prodnat-joint:PJ" "prodnat-jointB:PJB"
sbatch --job-name=crs-mix-rj1 scripts/covid_tree_mix.sbatch $S/mix-rj1.json data/experiments/crs-mix-rj1
# 2026-11-25 06:45 EST: joint Ball/A4c0 (rv-s-r12, job 10770646); all-joint mixture rj2 (CPU 10770647). Mixing joint and RSV-only members is not possible.
python3 $S/rounds.py rsv 12   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r12 --problem problems/us-respiratory-joint-short-term-coverage.json --study $S/rsv-round-12.json --device cuda
sbatch --job-name=crs-joint3 --array=0-5 scripts/flu_search.sbatch rv-s-r12:4
.venv/bin/python scripts/flu_search_mix.py rj2 --study $S --prefix crs-mix --max-seeds 24 --experiments rv-s-r11 rv-s-rs09 --members J=Bw.nat.joint,A4i.nat.joint BJ=Bw.nat.joint AJ=A4i.nat.joint --groups 'BJ+AJ:J' 'BJ:BJ' 'AJ:AJ'
sbatch --job-name=crs-mix-rj2 scripts/covid_tree_mix.sbatch $S/mix-rj2.json data/experiments/crs-mix-rj2
# 2026-11-25 07:45 EST: all-joint mixture rj3 (CPU 10772189); COVID 40-seed checks rs04/g05 + joint release fits reljoint (job 10772207)
.venv/bin/python scripts/flu_search_mix.py rj3 --study $S --prefix crs-mix --max-seeds 8 --experiments rv-s-r11 rv-s-r12 --members PJ=ref.Ball.joint,Bw.nat.joint,ref.A4c0.joint,A4i.nat.joint --groups "prodnat-alljoint:PJ"
sbatch --job-name=crs-mix-rj3 scripts/covid_tree_mix.sbatch $S/mix-rj3.json data/experiments/crs-mix-rj3
for a in "covid rs04" "covid g05" "rsv reljoint"; do python3 $S/rounds.py $a; done   # on the Mac (bash)
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rs04 --problem problems/us-covid-short-term-coverage.json --study $S/covid-reseed-rs04.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g05 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-reljoint --problem problems/us-respiratory-joint-production-coverage.json --study $S/rsv-reseed-reljoint.json --device cuda
sbatch --job-name=crs-s40 --array=0-5 scripts/flu_search.sbatch cv-s-rs04:4 cv-s-g05:4 rv-s-reljoint:4
# 2026-11-25 08:45 EST: cancelled hung element 10704128_1; 40-seed COVID mixtures c06 / c05g + blocks cb5 / cgb5; RSV composition mixtures r05 / r05g
scancel 10704128_1
CM="P=ref.Ah,ref.pN,ref.N,ref.Bh T=T N=ref.N S=S pN=ref.pN"; CG=("prod4:P" "prod4+T:P,T" "T+N+S:T,N,S" "N+pN+S:N,pN,S")
.venv/bin/python scripts/flu_search_mix.py c06 --study $S --prefix crs-mix --max-seeds 40 --experiments cv-s-r01 cv-s-rs01 cv-s-rs02 cv-s-rs03 cv-s-rs04 --members $CM --groups "${CG[@]}"
.venv/bin/python scripts/flu_search_mix.py c05g --study $S --prefix crs-mix --max-seeds 40 --experiments cv-s-g01 cv-s-g02 cv-s-g03 cv-s-g04 cv-s-g05 --members $CM --groups "${CG[@]}"
#   (same with cb5: --experiments cv-s-rs04 --max-seeds 8; cgb5: cv-s-g05), each followed by
sbatch --job-name=crs-mix-c06 scripts/covid_tree_mix.sbatch $S/mix-c06.json data/experiments/crs-mix-c06
M="PN=ref.Ball,Bw.nat,ref.A4c0,A4i.nat PR=ref.Ball,Bw.nat,Rc,A4i.nat P3=ref.Ball,Bw.nat,A4i.nat P5=ref.Ball,Bw.nat,ref.A4c0,A4i.nat,Rc"
.venv/bin/python scripts/flu_search_mix.py r05 --study $S --prefix crs-mix --max-seeds 24 --experiments rv-s-r01 rv-s-r03 rv-s-r05 rv-s-rs01 rv-s-rs03 rv-s-rs04 rv-s-rs05 rv-s-rs06 --members $M --groups "prodnat:PN" "prodnat-Rc:PR" "prodnat-noA4c0:P3" "prodnat+Rc:P5"
.venv/bin/python scripts/flu_search_mix.py r05g --study $S --prefix crs-mix --max-seeds 24 --experiments rv-s-g01 rv-s-g06 rv-s-g07 rv-s-g08 --members $M --groups "prodnat:PN" "prodnat-Rc:PR" "prodnat-noA4c0:P3" "prodnat+Rc:P5"
python3 scripts/crs_block_se.py
# 2026-11-25 09:40 EST: COVID seeds 84-91 (rs05, g06; job 10776153); draft release manifests (not installed)
python3 $S/rounds.py covid rs05; python3 $S/rounds.py covid g06   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rs05 --problem problems/us-covid-short-term-coverage.json --study $S/covid-reseed-rs05.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g06 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g06.json --device cuda
sbatch --job-name=crs-s48 --array=0-5 scripts/flu_search.sbatch cv-s-rs05:4 cv-s-g06:4
.venv/bin/python scripts/flu_search_release.py rsv-nat-candidate-20261125 $S/draft-release-rsv-nat.json rv-s-rel+rv-s-rel2:ref.Ball=Ball_c0w512 rv-s-rel+rv-s-rel2:Bw.nat=Bw.nat rv-s-rel+rv-s-rel2:ref.A4c0=A4c0 rv-s-rel+rv-s-rel2:A4i.nat=A4i.nat --hub rsv --problem problems/us-rsv-production-coverage.json --description "..."
.venv/bin/python scripts/flu_search_release.py covid-tns-candidate-20261125 $S/draft-release-covid-tns.json cv-s-rel+cv-s-rel2:T=T cv-s-rel+cv-s-rel2:ref.N=N.multiscale cv-s-rel+cv-s-rel2:S=S --hub covid --problem problems/us-covid-production-coverage.json --description "..."
.venv/bin/python scripts/flu_search_release.py covid-prod-refit-20261125 $S/draft-release-covid-prod-refit.json cv-s-rel+cv-s-rel2:ref.Ah=Ah.neighbors cv-s-rel+cv-s-rel2:ref.pN=pN.enc_gru cv-s-rel+cv-s-rel2:ref.N=N.multiscale cv-s-rel+cv-s-rel2:ref.Bh=Bh.wd cv-s-rel+cv-s-rel2:T=T --hub covid --problem problems/us-covid-production-coverage.json --description "..."
# 2026-11-25 10:40 EST: 48-seed COVID mixtures c07 / c06g + blocks cb6 / cgb6; release seeds 82-121 (job 10781142)
.venv/bin/python scripts/flu_search_mix.py c07 --study $S --prefix crs-mix --max-seeds 48 --experiments cv-s-r01 cv-s-rs01 cv-s-rs02 cv-s-rs03 cv-s-rs04 cv-s-rs05 --members $CM --groups "${CG[@]}"
.venv/bin/python scripts/flu_search_mix.py c06g --study $S --prefix crs-mix --max-seeds 48 --experiments cv-s-g01 cv-s-g02 cv-s-g03 cv-s-g04 cv-s-g05 cv-s-g06 --members $CM --groups "${CG[@]}"
python3 $S/rounds.py covid rel3; python3 $S/rounds.py rsv rel3   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rel3 --problem problems/us-rsv-production-coverage.json --study $S/rsv-reseed-rel3.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rel3 --problem problems/us-covid-production-coverage.json --study $S/covid-reseed-rel3.json --device cuda
sbatch --job-name=crs-rel3 --array=0-5 scripts/flu_search.sbatch rv-s-rel3:4 cv-s-rel3:4
# 2026-11-25 11:45 EST: RSV draft release refreshed to 80 seeds (rv-s-rel+rel2+rel3); round covid 8 / rsv 13 (job 10787049)
.venv/bin/python scripts/flu_search_release.py rsv-nat-candidate-20261125 $S/draft-release-rsv-nat.json rv-s-rel+rv-s-rel2+rv-s-rel3:ref.Ball=Ball_c0w512 rv-s-rel+rv-s-rel2+rv-s-rel3:Bw.nat=Bw.nat rv-s-rel+rv-s-rel2+rv-s-rel3:ref.A4c0=A4c0 rv-s-rel+rv-s-rel2+rv-s-rel3:A4i.nat=A4i.nat --hub rsv --problem problems/us-rsv-production-coverage.json --description "..."
python3 $S/rounds.py covid 8; python3 $S/rounds.py rsv 13   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r08 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-08.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r13 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-13.json --device cuda
sbatch --job-name=crs-r13 --array=0-5 scripts/flu_search.sbatch rv-s-r13:4 cv-s-r08:4
# 2026-11-25 12:45 EST: COVID release refreshed to 80 seeds; delayed-view mixtures c07d / r04d; round covid 9 / rsv 14 (job 10797081)
.venv/bin/python scripts/flu_search_release.py covid-tns-candidate-20261125 $S/draft-release-covid-tns.json cv-s-rel+cv-s-rel2+cv-s-rel3:T=T cv-s-rel+cv-s-rel2+cv-s-rel3:ref.N=N.multiscale cv-s-rel+cv-s-rel2+cv-s-rel3:S=S --hub covid --problem problems/us-covid-production-coverage.json --description "..."
#   mix-c07d.json / mix-r04d.json = mix-c07.json / mix-r04.json with "views": ["corrected", "delayed"]
sbatch --job-name=crs-mix-c07d scripts/covid_tree_mix.sbatch $S/mix-c07d.json data/experiments/crs-mix-c07d
sbatch --job-name=crs-mix-r04d scripts/covid_tree_mix.sbatch $S/mix-r04d.json data/experiments/crs-mix-r04d
python3 $S/rounds.py covid 9; python3 $S/rounds.py rsv 14   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r09 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-09.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-r14 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-14.json --device cuda
sbatch --job-name=crs-r14 --array=0-5 scripts/flu_search.sbatch cv-s-r09:4 rv-s-r14:4
# 2026-11-25 13:45 EST: delayed-view results recorded; amplitude COVID members rs06 + guard g07 (job 10805040)
python3 $S/rounds.py covid rs06; python3 $S/rounds.py covid g07   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rs06 --problem problems/us-covid-short-term-coverage.json --study $S/covid-reseed-rs06.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g07 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g07.json --device cuda
sbatch --job-name=crs-amp --array=0-5 scripts/flu_search.sbatch cv-s-rs06:4 cv-s-g07:4
# 2026-11-25 14:50 EST: amplitude mixtures ca1 / cag and aligned blocks ab1-3 / agb1-3 (--seeds); round covid 10 + amplitude release fits (job 10811226)
CM="P=ref.Ah,ref.pN,ref.N,ref.Bh TNS=T,ref.N,S AMP=T.amp3,ref.N.amp3,S.amp3 AM2=T.amp3,ref.N.amp3,S"; CG=("prod4:P" "T+N+S:TNS" "amp-T+N+S:AMP" "amp-T+N+S-S:AM2")
.venv/bin/python scripts/flu_search_mix.py ca1 --study $S --prefix crs-mix --max-seeds 24 --experiments cv-s-r01 cv-s-rs01 cv-s-rs02 cv-s-r09 cv-s-rs06 --members $CM --groups "${CG[@]}"
.venv/bin/python scripts/flu_search_mix.py cag --study $S --prefix crs-mix --max-seeds 24 --experiments cv-s-g01 cv-s-g02 cv-s-g03 cv-s-g07 --members $CM --groups "${CG[@]}"
.venv/bin/python scripts/flu_search_mix.py ab1 --study $S --prefix crs-mix --max-seeds 8 --seeds 44-51 --experiments cv-s-r01 cv-s-rs01 cv-s-rs02 cv-s-r09 cv-s-rs06 --members $CM --groups "${CG[@]}"   # ab2 52-59, ab3 60-67; agb1-3 with the guard experiments
python3 $S/rounds.py covid 10; python3 $S/rounds.py covid relamp   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-r10 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-10.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-relamp --problem problems/us-covid-production-coverage.json --study $S/covid-reseed-relamp.json --device cuda
sbatch --job-name=crs-amp2 --array=0-5 scripts/flu_search.sbatch cv-s-r10:4 cv-s-relamp:4
# 2026-11-25 15:45 EST: amplitude mixtures scored (python3 output/crs-search/ampblk.py: aligned blocks); amplitude members to 48 seeds (rs07, g08; job 10818964); peak check of ca1
python3 $S/rounds.py covid rs07; python3 $S/rounds.py covid g08   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-rs07 --problem problems/us-covid-short-term-coverage.json --study $S/covid-reseed-rs07.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g08 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g08.json --device cuda
sbatch --job-name=crs-amp48 --array=0-5 scripts/flu_search.sbatch cv-s-rs07:4 cv-s-g08:4
sbatch --job-name=crs-phase3 --partition=jlessler --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/crs-search/phase3.log --wrap "PYTHONPATH=src .venv/bin/python scripts/flu_phase_check.py --out output/crs-search/tasks-ca1.csv data/experiments/crs-mix-ca1/*-mixture > output/crs-search/phase-ca1.txt"
# 2026-11-25 16:45 EST: amplitude mixture fails the peak window (not adopted); 64-seed COVID guard (g09, job 10825626); RSV peak check r04
.venv/bin/python scripts/crs_phase_diff.py output/crs-search/tasks-ca1.csv "prod4 [24 seeds]-mixture" "amp-T+N+S [24 seeds]-mixture"
python3 $S/rounds.py covid g09   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e cv-s-g09 --problem problems/us-covid-2023-24-prescribed-coverage.json --study $S/covid-guard-g09.json --device cuda
sbatch --job-name=crs-g64 --array=0-5 scripts/flu_search.sbatch cv-s-g09:4
sbatch --job-name=crs-phase4 --partition=jlessler --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/crs-search/phase4.log --wrap 'PYTHONPATH=src .venv/bin/python scripts/flu_phase_check.py --out output/crs-search/tasks-r04.csv data/experiments/crs-mix-r04/*-mixture > output/crs-search/phase-r04.txt'
# 2026-11-25 17:45 EST: RSV peak check at 32 seeds (fails narrowly); blended RSV mixtures r06 / r06g; 64-seed COVID guard mixtures c07g + blocks; RSV seeds 76-91 (rs10)
.venv/bin/python scripts/crs_phase_diff.py output/crs-search/tasks-r04.csv "prod4 [32 seeds]-mixture" "prodnat [32 seeds]-mixture"
M="P=ref.Ball,ref.Bw,ref.A4c0,ref.A4i PN=ref.Ball,Bw.nat,ref.A4c0,A4i.nat P6=ref.Ball,ref.Bw,Bw.nat,ref.A4c0,ref.A4i,A4i.nat PB6=ref.Ball,ref.Bw,Bw.nat,ref.A4c0,ref.A4i"
.venv/bin/python scripts/flu_search_mix.py r06 --study $S --prefix crs-mix --max-seeds 32 --experiments rv-s-r01 rv-s-r03 rv-s-r05 rv-s-rs01 rv-s-rs03 rv-s-rs04 rv-s-rs05 rv-s-rs06 rv-s-rs08 --members $M --groups "prod4:P" "prodnat:PN" "prod+nat:P6" "prod+Bnat:PB6"
.venv/bin/python scripts/flu_search_mix.py c07g --study $S --prefix crs-mix --max-seeds 64 --experiments cv-s-g01 cv-s-g02 cv-s-g03 cv-s-g04 cv-s-g05 cv-s-g06 cv-s-g09 --members "P=ref.Ah,ref.pN,ref.N,ref.Bh" "TNS=T,ref.N,S" --groups "prod4:P" "T+N+S:TNS"
python3 $S/rounds.py rsv rs10   # on the Mac
.venv/bin/python -m chromantis.experiment.planner plan -e rv-s-rs10 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-reseed-rs10.json --device cuda
sbatch --job-name=crs-r48 --array=0-5 scripts/flu_search.sbatch rv-s-rs10:6
