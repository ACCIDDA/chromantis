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
