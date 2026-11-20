# covid-rsv-coverage-20261118. Longleaf campaign folder (shares the coverage panel and .venv of the flu nowcast study):
#   /hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113
# From the Mac: send code, problems, datasets and studies
rsync -a --exclude /.git --exclude /data --exclude /output --exclude /.venv ./ chadi@longleaf.unc.edu:/hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113/
# On Longleaf, in that folder:
export PYTHONPATH=src
.venv/bin/python -m chromantis.dataset.build mask --dataset data/processed/panel-coverage.npz --output data/processed/panel-coverage-rsv.npz \
    --signal nhsn_rsv_admissions --before 2024-11-02 --reason "NHSN RSV reporting voluntary before mandatory reporting (as panel-rsv.npz, user decision 2026-10-13)"
S=experiments/covid-rsv-coverage-20261118
.venv/bin/python -m chromantis.experiment.planner plan -e covid-cov-r01 --problem problems/us-covid-short-term-coverage.json --study $S/covid-round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rsv-cov-r01 --problem problems/us-rsv-short-term-coverage.json --study $S/rsv-round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-cov-fwd01 --problem problems/us-covid-forward-2025-26-coverage.json --study $S/covid-round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e rsv-cov-fwd01 --problem problems/us-rsv-forward-2025-26-coverage.json --study $S/rsv-round-01.json --device cuda
sbatch --job-name=cov-r01 --array=0-5 scripts/covid_tree.sbatch covid-cov-r01 rsv-cov-r01 covid-cov-fwd01 rsv-cov-fwd01
.venv/bin/python -m chromantis.experiment.planner status -e covid-cov-r01
.venv/bin/python -m chromantis.experiment.planner status -e rsv-cov-r01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-cov-r01 --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner rank -e rsv-cov-r01 --allow-incomplete --no-report
# 2026-11-18 17:50 EST: round 1 launched as job 9775165 (array 0-5).
# Live decomposition of the submitted forecasts (needs data/hub-target/{covid,rsv}-time-series.parquet from the Hub repos)
PYTHONPATH=src .venv/bin/python scripts/live_nowcast_decomposition.py --hub rsv
PYTHONPATH=src .venv/bin/python scripts/live_nowcast_decomposition.py --hub covid
# Round 1b: covariates on T.<root>.real_cov_hc, chained after round 1 (job 9775775)
for a in "covid-cov-r01b us-covid-short-term-coverage covid" "rsv-cov-r01b us-rsv-short-term-coverage rsv" \
         "covid-cov-fwd01b us-covid-forward-2025-26-coverage covid" "rsv-cov-fwd01b us-rsv-forward-2025-26-coverage rsv"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3-round-01b.json --device cuda
done
sbatch --job-name=cov-r01b --array=0-5 --dependency=afterany:9775165 scripts/covid_tree.sbatch covid-cov-r01b rsv-cov-r01b covid-cov-fwd01b rsv-cov-fwd01b
.venv/bin/python -m chromantis.experiment.planner status -e rsv-cov-r01b
.venv/bin/python -m chromantis.experiment.planner rank -e rsv-cov-r01b --allow-incomplete --no-report
# 2026-11-18 19:20 EST: live gate (all-season fits on the 2026-27 reports) and round 2, chained after round 1b (job 9778147)
for a in "covid-cov-gate01 us-covid-production-coverage covid-gate-01" "rsv-cov-gate01 us-rsv-production-coverage rsv-gate-01" \
         "covid-cov-r02 us-covid-short-term-coverage covid-round-02" "rsv-cov-r02 us-rsv-short-term-coverage rsv-round-02" \
         "covid-cov-fwd02 us-covid-forward-2025-26-coverage covid-round-02" "rsv-cov-fwd02 us-rsv-forward-2025-26-coverage rsv-round-02"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r02 --array=0-5 --dependency=afterany:9775775 scripts/covid_tree.sbatch covid-cov-gate01 rsv-cov-gate01 covid-cov-r02 rsv-cov-r02 covid-cov-fwd02 rsv-cov-fwd02
.venv/bin/python -m chromantis.experiment.planner status -e covid-cov-gate01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-cov-gate01 --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner rank -e covid-cov-r02 --allow-incomplete --no-report
# 2026-11-18 20:25 EST: RSV round 3 (covariates on Bw/A4c0) and COVID reseed 48-51, chained after round 2 (job 9781844)
for a in "rsv-cov-r03 us-rsv-short-term-coverage rsv-round-03" "rsv-cov-fwd03 us-rsv-forward-2025-26-coverage rsv-round-03" \
         "covid-cov-reseed01 us-covid-short-term-coverage covid-reseed-01" "covid-cov-reseedfwd01 us-covid-forward-2025-26-coverage covid-reseed-01"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r03 --array=0-5 --dependency=afterany:9778147 scripts/covid_tree.sbatch rsv-cov-r03 rsv-cov-fwd03 covid-cov-reseed01 covid-cov-reseedfwd01
.venv/bin/python -m chromantis.experiment.planner status -e rsv-cov-r03
.venv/bin/python -m chromantis.experiment.planner rank -e rsv-cov-r03 --allow-incomplete --no-report
# Live gate scored against the latest Hub target data (refresh data/hub-target/*.parquet from the Hub repos first)
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate01 --hub covid
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate01 --hub rsv --view half
# 2026-11-18 21:50 EST: live gate 2 and round 4, chained after round 3 (job 9786230)
for a in "covid-cov-gate02 us-covid-production-coverage covid-gate-02" "rsv-cov-gate02 us-rsv-production-coverage rsv-gate-02" \
         "covid-cov-r04 us-covid-short-term-coverage covid-round-04" "rsv-cov-r04 us-rsv-short-term-coverage rsv-round-04" \
         "covid-cov-fwd04 us-covid-forward-2025-26-coverage covid-round-04" "rsv-cov-fwd04 us-rsv-forward-2025-26-coverage rsv-round-04"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r04 --array=0-5 --dependency=afterany:9781844 scripts/covid_tree.sbatch covid-cov-gate02 rsv-cov-gate02 covid-cov-r04 rsv-cov-r04 covid-cov-fwd04 rsv-cov-fwd04
.venv/bin/python -m chromantis.experiment.planner status -e rsv-cov-r04
.venv/bin/python -m chromantis.experiment.planner rank -e rsv-cov-r04 --allow-incomplete --no-report
# 2026-11-18 23:00 EST: reseed 2 (seeds 48-51) for the leaders, chained after round 4 (job 9790053)
for a in "covid-cov-reseed02 us-covid-short-term-coverage covid-reseed-02" "covid-cov-reseedfwd02 us-covid-forward-2025-26-coverage covid-reseed-02" \
         "rsv-cov-reseed02 us-rsv-short-term-coverage rsv-reseed-02" "rsv-cov-reseedfwd02 us-rsv-forward-2025-26-coverage rsv-reseed-02"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-reseed02 --array=0-5 --dependency=afterany:9786230 scripts/covid_tree.sbatch covid-cov-reseed02 rsv-cov-reseed02 covid-cov-reseedfwd02 rsv-cov-reseedfwd02
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate02 --hub covid
# 2026-11-19 00:10 EST: live gate 3 and round 5, chained after reseed 2 (job 9793968)
for a in "rsv-cov-gate03 us-rsv-production-coverage rsv-gate-03" "covid-cov-gate03 us-covid-production-coverage covid-gate-03" \
         "rsv-cov-r05 us-rsv-short-term-coverage rsv-round-05" "covid-cov-r05 us-covid-short-term-coverage covid-round-05" \
         "rsv-cov-fwd05 us-rsv-forward-2025-26-coverage rsv-round-05" "covid-cov-fwd05 us-covid-forward-2025-26-coverage covid-round-05"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r05 --array=0-5 --dependency=afterany:9790053 scripts/covid_tree.sbatch rsv-cov-gate03 covid-cov-gate03 rsv-cov-r05 covid-cov-r05 rsv-cov-fwd05 covid-cov-fwd05
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate03 --hub rsv
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate02 --hub rsv --view raw
# 2026-11-19 01:45 EST: finalist seeds 46-51, RSV round 6 and gate 4, chained after round 5 (job 9796588)
for a in "covid-cov-final us-covid-production-coverage covid-final-seeds" "rsv-cov-final us-rsv-production-coverage rsv-final-seeds" \
         "rsv-cov-gate04 us-rsv-production-coverage rsv-gate-04" "rsv-cov-r06 us-rsv-short-term-coverage rsv-round-06" "rsv-cov-fwd06 us-rsv-forward-2025-26-coverage rsv-round-06"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-final --array=0-5 --dependency=afterany:9793968 scripts/covid_tree.sbatch covid-cov-final rsv-cov-final rsv-cov-gate04 rsv-cov-r06 rsv-cov-fwd06
# Live mixtures (equal weight per recipe and seed, scored as one forecast)
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate01 covid-cov-gate02 covid-cov-gate03 --hub covid --mix "Gru=T.pN_gru.real" "GruL1+Gru=T.pN_gru.real.log_loss1+T.pN_gru.real"
# Backtest mixtures (CPU, jobs 9796632-3)
for k in main forward; do sbatch --job-name=covid-mix01-$k scripts/covid_tree_mix.sbatch experiments/covid-rsv-coverage-20261118/covid-mix-01-$k.json data/experiments/covid-cov-mix01/$k; done
# 2026-11-19 03:15 EST: backtest mixtures (CPU, jobs 9803849-52)
for p in covid rsv; do for k in main forward; do sbatch --job-name=$p-mix02-$k scripts/covid_tree_mix.sbatch experiments/covid-rsv-coverage-20261118/$p-mix-02-$k.json data/experiments/$p-cov-mix02/$k; done; done
# ED share live
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate01 covid-cov-gate02 covid-cov-gate03 covid-cov-final --hub covid --target ed --mix "GruL1_10=T.pN_gru.real.log_loss1"
# COVID ED round 6, gate 4, RSV seeds 46-51 for round-6 leaders (job 9803968)
for a in "covid-cov-gate04 us-covid-production-coverage covid-gate-04" "rsv-cov-final2 us-rsv-production-coverage rsv-final-seeds-2" \
         "covid-cov-r06 us-covid-short-term-coverage covid-round-06" "covid-cov-fwd06 us-covid-forward-2025-26-coverage covid-round-06"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r06 --array=0-5 --dependency=afterany:9796588 scripts/covid_tree.sbatch covid-cov-gate04 rsv-cov-final2 covid-cov-r06 covid-cov-fwd06
# 2026-11-19 01:40 EST: round 7 (architectures) and release seeds 52-61 (job 9805460); live gate 5 after it (job 9805484)
for a in "covid-cov-r07 us-covid-short-term-coverage covid-round-07" "rsv-cov-r07 us-rsv-short-term-coverage rsv-round-07" \
         "covid-cov-fwd07 us-covid-forward-2025-26-coverage covid-round-07" "rsv-cov-fwd07 us-rsv-forward-2025-26-coverage rsv-round-07" \
         "covid-cov-release us-covid-production-coverage covid-release-seeds" "rsv-cov-release us-rsv-production-coverage rsv-release-seeds" \
         "covid-cov-gate05 us-covid-production-coverage covid-gate-05" "rsv-cov-gate05 us-rsv-production-coverage rsv-gate-05"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r07 --array=0-5 scripts/covid_tree.sbatch covid-cov-r07 rsv-cov-r07 covid-cov-fwd07 rsv-cov-fwd07 covid-cov-release rsv-cov-release
sbatch --job-name=cov-gate05 --array=0-5 --dependency=afterany:9805460 scripts/covid_tree.sbatch covid-cov-gate05 rsv-cov-gate05
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate04 rsv-cov-final2 --hub rsv --mix "NRCal=A4c0.national.rsvnet.calendar"
# 2026-11-19 02:37 EST: gate 5 dependency released by hand while 4 GPUs idled
scontrol update jobid=9805484 dependency=
# 2026-11-19 02:40 EST: round 8 + live gate 6 (COVID sampled recipes, RSV log1p), job 9806963 afterany 9805484
for a in "covid-cov-gate06 us-covid-production-coverage covid-gate-06" "rsv-cov-gate06 us-rsv-production-coverage rsv-gate-06" \
         "covid-cov-r08 us-covid-short-term-coverage covid-round-08" "rsv-cov-r08 us-rsv-short-term-coverage rsv-round-08" \
         "covid-cov-fwd08 us-covid-forward-2025-26-coverage covid-round-08" "rsv-cov-fwd08 us-rsv-forward-2025-26-coverage rsv-round-08"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r08 --array=0-5 --dependency=afterany:9805484 scripts/covid_tree.sbatch covid-cov-gate06 rsv-cov-gate06 covid-cov-r08 rsv-cov-r08 covid-cov-fwd08 rsv-cov-fwd08
.venv/bin/python -m chromantis.experiment.planner status -e covid-cov-gate05
# 2026-11-19 03:40 EST: COVID partner seeds 46-61, round 9 + gate 7 (nowcast-tree settings), job 9808012 (no dependency); mixtures 03 (CPU 9808013-4)
for a in "covid-cov-partners us-covid-production-coverage covid-partner-seeds" "covid-cov-gate07 us-covid-production-coverage covid-gate-07" "rsv-cov-gate07 us-rsv-production-coverage rsv-gate-07" \
         "covid-cov-r09 us-covid-short-term-coverage covid-round-09" "rsv-cov-r09 us-rsv-short-term-coverage rsv-round-09" \
         "covid-cov-fwd09 us-covid-forward-2025-26-coverage covid-round-09" "rsv-cov-fwd09 us-rsv-forward-2025-26-coverage rsv-round-09"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r09 --array=0-5 scripts/covid_tree.sbatch covid-cov-partners covid-cov-gate07 rsv-cov-gate07 covid-cov-r09 rsv-cov-r09 covid-cov-fwd09 rsv-cov-fwd09
for k in main forward; do sbatch --job-name=covid-mix03-$k --dependency=afterany:9806963 scripts/covid_tree_mix.sbatch $S/covid-mix-03-$k.json data/experiments/covid-cov-mix03/$k; done
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate02 covid-cov-gate03 covid-cov-gate05 covid-cov-gate06 covid-cov-final covid-cov-release --hub covid --mix "GruL1+Att=T.pN_gru.real.log_loss1+T.pN_gru.real.log_loss1.attention" "GruL1+SAhGru=T.pN_gru.real.log_loss1+S.Ah.gru_national.real"
# 2026-11-19 04:50 EST: confirmation seeds 46-61 (job 9809000, no dependency)
for a in "covid-cov-confirm us-covid-production-coverage covid-confirm-seeds" "rsv-cov-confirm us-rsv-production-coverage rsv-confirm-seeds"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-confirm --array=0-5 scripts/covid_tree.sbatch rsv-cov-confirm covid-cov-confirm
# 20-seed live mixtures (COVID leader + attention partner)
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate03 covid-cov-final covid-cov-release covid-cov-gate05 covid-cov-gate06 covid-cov-partners --hub covid --mix "GruL1+Att_20=T.pN_gru.real.log_loss1+T.pN_gru.real.log_loss1.attention"
# 2026-11-19 05:45 EST: round 10 + gate 8 (count transforms, latent noise) and backtest reseed 3 (seeds 48-51), job 9809964
for a in "covid-cov-gate08 us-covid-production-coverage covid-gate-08" "rsv-cov-gate08 us-rsv-production-coverage rsv-gate-08" \
         "covid-cov-r10 us-covid-short-term-coverage covid-round-10" "rsv-cov-r10 us-rsv-short-term-coverage rsv-round-10" \
         "covid-cov-fwd10 us-covid-forward-2025-26-coverage covid-round-10" "rsv-cov-fwd10 us-rsv-forward-2025-26-coverage rsv-round-10" \
         "covid-cov-reseed03 us-covid-short-term-coverage covid-reseed-03" "rsv-cov-reseed03 us-rsv-short-term-coverage rsv-reseed-03" \
         "covid-cov-reseedfwd03 us-covid-forward-2025-26-coverage covid-reseed-03" "rsv-cov-reseedfwd03 us-rsv-forward-2025-26-coverage rsv-reseed-03"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r10 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate08 rsv-cov-gate08 covid-cov-r10 rsv-cov-r10 covid-cov-fwd10 rsv-cov-fwd10 covid-cov-reseed03 rsv-cov-reseed03 covid-cov-reseedfwd03 rsv-cov-reseedfwd03
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate07 rsv-cov-confirm --hub rsv --mix "W1_20=A4c0.national.rsvnet.calendar.weeks1"
# 2026-11-19 06:45 EST: round 11 + gate 9 (how training reporting errors are drawn), job 9810868
for a in "covid-cov-gate09 us-covid-production-coverage covid-gate-09" "rsv-cov-gate09 us-rsv-production-coverage rsv-gate-09" \
         "covid-cov-r11 us-covid-short-term-coverage covid-round-11" "rsv-cov-r11 us-rsv-short-term-coverage rsv-round-11" \
         "covid-cov-fwd11 us-covid-forward-2025-26-coverage covid-round-11" "rsv-cov-fwd11 us-rsv-forward-2025-26-coverage rsv-round-11"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r11 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate09 rsv-cov-gate09 covid-cov-r11 rsv-cov-r11 covid-cov-fwd11 rsv-cov-fwd11
# 2026-11-19 07:55 EST: backtest reseed 4 (seeds 52-55), job 9811663
for a in "covid-cov-reseed04 us-covid-short-term-coverage covid-reseed-04" "rsv-cov-reseed04 us-rsv-short-term-coverage rsv-reseed-04" \
         "covid-cov-reseedfwd04 us-covid-forward-2025-26-coverage covid-reseed-04" "rsv-cov-reseedfwd04 us-rsv-forward-2025-26-coverage rsv-reseed-04"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-reseed04 --array=0-5 scripts/covid_tree.sbatch covid-cov-reseed04 rsv-cov-reseed04 covid-cov-reseedfwd04 rsv-cov-reseedfwd04
# Nowcast vs growth decomposition of candidate fits, and its figure
PYTHONPATH=src .venv/bin/python scripts/live_decomposition_fits.py --hub rsv -e rsv-cov-gate01 rsv-cov-gate02 rsv-cov-gate07 rsv-cov-confirm --recipes ref.Bw ref.A4c0 Bw.national A4c0.national A4c0.national.rsvnet.calendar.weeks1
PYTHONPATH=src .venv/bin/python scripts/live_decomposition_fits.py --hub covid -e covid-cov-gate01 covid-cov-gate03 covid-cov-final covid-cov-partners --recipes ref.Bh_wd ref.pN_gru ref.Ah T.pN_gru.real.log_loss1 T.pN_gru.real.log_loss1.attention
.venv/bin/python scripts/plot_live_decomposition_fits.py
# 2026-11-19 08:45 EST: 12-seed backtest mixtures (runs gathered across experiments; scripts/mix_seed_groups.py, run from the campaign folder), CPU jobs 9813237-41
for p in covid rsv; do for k in main forward; do python3 scripts/mix_seed_groups.py $p $k; sbatch --job-name=$p-mix04-$k scripts/covid_tree_mix.sbatch experiments/covid-rsv-coverage-20261118/$p-mix-04-$k.json data/experiments/$p-cov-mix04/$k; done; done
# Round 12 + gate 10 (training length, lr, decoder, width), job 9813322
for a in "covid-cov-gate10 us-covid-production-coverage covid-gate-10" "rsv-cov-gate10 us-rsv-production-coverage rsv-gate-10" \
         "covid-cov-r12 us-covid-short-term-coverage covid-round-12" "rsv-cov-r12 us-rsv-short-term-coverage rsv-round-12" \
         "covid-cov-fwd12 us-covid-forward-2025-26-coverage covid-round-12" "rsv-cov-fwd12 us-rsv-forward-2025-26-coverage rsv-round-12"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r12 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate10 rsv-cov-gate10 covid-cov-r12 rsv-cov-r12 covid-cov-fwd12 rsv-cov-fwd12
# 2026-11-19 09:45 EST: RSV round 13 + gate 11 (full-season leader with the October leader's changes), job 9816482
for a in "rsv-cov-gate11 us-rsv-production-coverage rsv-gate-11" "rsv-cov-r13 us-rsv-short-term-coverage rsv-round-13" "rsv-cov-fwd13 us-rsv-forward-2025-26-coverage rsv-round-13"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=rsv-r13 --array=0-5 scripts/covid_tree.sbatch rsv-cov-gate11 rsv-cov-r13 rsv-cov-fwd13
# 2026-11-19 10:55 EST: reseed 5 (seeds 56-59) of the recommended members, job 9822070
for a in "covid-cov-reseed05 us-covid-short-term-coverage covid-reseed-05" "rsv-cov-reseed05 us-rsv-short-term-coverage rsv-reseed-05" \
         "covid-cov-reseedfwd05 us-covid-forward-2025-26-coverage covid-reseed-05" "rsv-cov-reseedfwd05 us-rsv-forward-2025-26-coverage rsv-reseed-05"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-reseed05 --array=0-5 scripts/covid_tree.sbatch covid-cov-reseed05 rsv-cov-reseed05 covid-cov-reseedfwd05 rsv-cov-reseedfwd05
# Recommended live mixtures (20 seeds)
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate02 covid-cov-gate03 covid-cov-gate06 covid-cov-final covid-cov-release covid-cov-partners covid-cov-gate05 --hub covid --mix "Rec=T.pN_gru.real.log_loss1+T.pN_gru.real+S.Ah.gru_national.real" "Rec+Att=T.pN_gru.real.log_loss1+T.pN_gru.real+S.Ah.gru_national.real+T.pN_gru.real.log_loss1.attention"
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate04 rsv-cov-final2 rsv-cov-release rsv-cov-gate07 rsv-cov-confirm --hub rsv --mix "W1_20=A4c0.national.rsvnet.calendar.weeks1" "W1+NRCal_20=A4c0.national.rsvnet.calendar.weeks1+A4c0.national.rsvnet.calendar"
# 2026-11-19 11:45 EST: round 14 + gate 12 (location-exchange designs), job 9828119
for a in "covid-cov-gate12 us-covid-production-coverage covid-gate-12" "rsv-cov-gate12 us-rsv-production-coverage rsv-gate-12" \
         "covid-cov-r14 us-covid-short-term-coverage covid-round-14" "rsv-cov-r14 us-rsv-short-term-coverage rsv-round-14" \
         "covid-cov-fwd14 us-covid-forward-2025-26-coverage covid-round-14" "rsv-cov-fwd14 us-rsv-forward-2025-26-coverage rsv-round-14"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r14 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate12 rsv-cov-gate12 covid-cov-r14 rsv-cov-r14 covid-cov-fwd14 rsv-cov-fwd14
# 2026-11-19 15:00 EST: round 15 + gate 13 (untried training options), job 9851000
for a in "covid-cov-gate13 us-covid-production-coverage covid-gate-13" "rsv-cov-gate13 us-rsv-production-coverage rsv-gate-13" \
         "covid-cov-r15 us-covid-short-term-coverage covid-round-15" "rsv-cov-r15 us-rsv-short-term-coverage rsv-round-15" \
         "covid-cov-fwd15 us-covid-forward-2025-26-coverage covid-round-15" "rsv-cov-fwd15 us-rsv-forward-2025-26-coverage rsv-round-15"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r15 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate13 rsv-cov-gate13 covid-cov-r15 rsv-cov-r15 covid-cov-fwd15 rsv-cov-fwd15
# 2026-11-19 16:20 EST: replay of the submitted releases on every 2026-27 report (CPU), then score against candidates
sbatch --job-name=replay-covid scripts/replay_release.sbatch --release production/releases/covid-gru-four-candidate-20261103.json --campaign covid-20261030 --panel data/processed/panel-coverage.npz --hub covid --name covid-replay-submitted
sbatch --job-name=replay-rsv scripts/replay_release.sbatch --release production/releases/rsv-four-20261014.json --campaign tapestry --panel data/processed/panel-coverage-rsv.npz --hub rsv --name rsv-replay-submitted
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate03 covid-replay-submitted covid-cov-final covid-cov-release covid-cov-gate02 --hub covid --last-context 2026-11-07 --mix "SUBMITTED-FITS=Ah.neighbors+pN.enc_gru+N.multiscale+Bh.wd" "Leader+Gru=T.pN_gru.real.log_loss1+T.pN_gru.real"
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-replay-submitted rsv-cov-gate07 rsv-cov-confirm --hub rsv --submitted --mix "SUBMITTED-FITS=Ball_c0w512+Bw+A4c0+A4i" "W1=A4c0.national.rsvnet.calendar.weeks1"
# Round 16 + gate 14 (coverage for the trees only, network_coverage=0), job 9855288
for a in "covid-cov-gate14 us-covid-production-coverage covid-gate-14" "rsv-cov-gate14 us-rsv-production-coverage rsv-gate-14" \
         "covid-cov-r16 us-covid-short-term-coverage covid-round-16" "rsv-cov-r16 us-rsv-short-term-coverage rsv-round-16" \
         "covid-cov-fwd16 us-covid-forward-2025-26-coverage covid-round-16" "rsv-cov-fwd16 us-rsv-forward-2025-26-coverage rsv-round-16"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r16 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate14 rsv-cov-gate14 covid-cov-r16 rsv-cov-r16 covid-cov-fwd16 rsv-cov-fwd16
# 2026-11-19 16:30 EST: round 17 + gate 15 (pretraining, reconstruction loss, bottleneck, cVAE), job 9857249
for a in "covid-cov-gate15 us-covid-production-coverage covid-gate-15" "rsv-cov-gate15 us-rsv-production-coverage rsv-gate-15" \
         "covid-cov-r17 us-covid-short-term-coverage covid-round-17" "rsv-cov-r17 us-rsv-short-term-coverage rsv-round-17" \
         "covid-cov-fwd17 us-covid-forward-2025-26-coverage covid-round-17" "rsv-cov-fwd17 us-rsv-forward-2025-26-coverage rsv-round-17"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r17 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate15 rsv-cov-gate15 covid-cov-r17 rsv-cov-r17 covid-cov-fwd17 rsv-cov-fwd17
# 2026-11-19 17:25 EST: round 18 + gate 16 (coverage trees without double counting), job 9861801
for a in "covid-cov-gate16 us-covid-production-coverage covid-gate-16" "rsv-cov-gate16 us-rsv-production-coverage rsv-gate-16" \
         "covid-cov-r18 us-covid-short-term-coverage covid-round-18" "rsv-cov-r18 us-rsv-short-term-coverage rsv-round-18" \
         "covid-cov-fwd18 us-covid-forward-2025-26-coverage covid-round-18" "rsv-cov-fwd18 us-rsv-forward-2025-26-coverage rsv-round-18"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r18 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate16 rsv-cov-gate16 covid-cov-r18 rsv-cov-r18 covid-cov-fwd18 rsv-cov-fwd18
# 2026-11-19 18:30 EST: joint flu+COVID+RSV round 19 + gate 17 (new problems us-respiratory-*-coverage.json), job 9865429
for a in "joint-cov-gate17 us-respiratory-production-coverage joint-gate-17" "joint-cov-r19 us-respiratory-short-term-coverage joint-round-19" "joint-cov-fwd19 us-respiratory-forward-2025-26-coverage joint-round-19"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=joint-r19 --array=0-5 scripts/covid_tree.sbatch joint-cov-gate17 joint-cov-r19 joint-cov-fwd19
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e joint-cov-gate17 --hub covid
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e joint-cov-gate17 --hub rsv
# 2026-11-19 19:25 EST: round 20 + gate 18 (conv encoder, small quantile decoder, RSV GRU w256), job 9869165; joint forward failures (CUDA OOM) resubmitted, job 9869166
for a in "covid-cov-gate18 us-covid-production-coverage covid-gate-18" "rsv-cov-gate18 us-rsv-production-coverage rsv-gate-18" \
         "covid-cov-r20 us-covid-short-term-coverage covid-round-20" "rsv-cov-r20 us-rsv-short-term-coverage rsv-round-20" \
         "covid-cov-fwd20 us-covid-forward-2025-26-coverage covid-round-20" "rsv-cov-fwd20 us-rsv-forward-2025-26-coverage rsv-round-20"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r20 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate18 rsv-cov-gate18 covid-cov-r20 rsv-cov-r20 covid-cov-fwd20 rsv-cov-fwd20
sbatch --job-name=joint-cov-fwd19 --array=0-3 --dependency=afterany:9865429 scripts/jlessler.sbatch joint-cov-fwd19 --retry-failed
# 2026-11-19 20:25 EST: round 21 + gate 19 (random search, 4 settings changed at once), job 9873670
for a in "covid-cov-gate19 us-covid-production-coverage covid-gate-19" "rsv-cov-gate19 us-rsv-production-coverage rsv-gate-19" \
         "covid-cov-r21 us-covid-short-term-coverage covid-round-21" "rsv-cov-r21 us-rsv-short-term-coverage rsv-round-21" \
         "covid-cov-fwd21 us-covid-forward-2025-26-coverage covid-round-21" "rsv-cov-fwd21 us-rsv-forward-2025-26-coverage rsv-round-21"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r21 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate19 rsv-cov-gate19 covid-cov-r21 rsv-cov-r21 covid-cov-fwd21 rsv-cov-fwd21
# 2026-11-19 21:25 EST: cancelled idle joint resubmission; round 22 + gate 20 (second random search), job 9885291
scancel 9869166
for a in "covid-cov-gate20 us-covid-production-coverage covid-gate-20" "rsv-cov-gate20 us-rsv-production-coverage rsv-gate-20" \
         "covid-cov-r22 us-covid-short-term-coverage covid-round-22" "rsv-cov-r22 us-rsv-short-term-coverage rsv-round-22" \
         "covid-cov-fwd22 us-covid-forward-2025-26-coverage covid-round-22" "rsv-cov-fwd22 us-rsv-forward-2025-26-coverage rsv-round-22"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r22 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate20 rsv-cov-gate20 covid-cov-r22 rsv-cov-r22 covid-cov-fwd22 rsv-cov-fwd22
# 2026-11-19 23:30 EST: confirm RSV RS200 (live seeds 46-61, backtest 48-55), job 9894445; round 23 + gate 21, job 9894553
for a in "rsv-cov-confirm-rs200 us-rsv-production-coverage rsv-confirm-rs200" "rsv-cov-reseed-rs200 us-rsv-short-term-coverage rsv-reseed-rs200" "rsv-cov-reseedfwd-rs200 us-rsv-forward-2025-26-coverage rsv-reseed-rs200" \
         "rsv-cov-gate21 us-rsv-production-coverage rsv-gate-21" "covid-cov-gate21 us-covid-production-coverage covid-gate-21" "rsv-cov-r23 us-rsv-short-term-coverage rsv-round-23" \
         "covid-cov-r23 us-covid-short-term-coverage covid-round-23" "rsv-cov-fwd23 us-rsv-forward-2025-26-coverage rsv-round-23" "covid-cov-fwd23 us-covid-forward-2025-26-coverage covid-round-23"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=rsv-rs200 --array=0-5 scripts/covid_tree.sbatch rsv-cov-confirm-rs200 rsv-cov-reseed-rs200 rsv-cov-reseedfwd-rs200
sbatch --job-name=cov-r23 --array=0-5 scripts/covid_tree.sbatch rsv-cov-gate21 covid-cov-gate21 rsv-cov-r23 covid-cov-r23 rsv-cov-fwd23 covid-cov-fwd23
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate20 rsv-cov-confirm-rs200 rsv-cov-gate07 rsv-cov-confirm --hub rsv --mix "RS200_20=RS200.correction_penalty10.0.covariate_dropout0.2.epochs320.patience60" "W1_20=A4c0.national.rsvnet.calendar.weeks1"
# 2026-11-20 01:25 EST: round 24 + gate 22 (8 seeds: target lag, reported histories, error strength), job 9903242
for a in "covid-cov-gate22 us-covid-production-coverage covid-gate-22" "rsv-cov-gate22 us-rsv-production-coverage rsv-gate-22" \
         "covid-cov-r24 us-covid-short-term-coverage covid-round-24" "rsv-cov-r24 us-rsv-short-term-coverage rsv-round-24" \
         "covid-cov-fwd24 us-covid-forward-2025-26-coverage covid-round-24" "rsv-cov-fwd24 us-rsv-forward-2025-26-coverage rsv-round-24"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r24 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate22 rsv-cov-gate22 covid-cov-r24 rsv-cov-r24 covid-cov-fwd24 rsv-cov-fwd24
# 2026-11-20 02:25 EST: round 25 + gate 23 (8 seeds), release seeds 62-81, backtest seeds 56-63; job 9906429 (COVID round 25 part: 9906450)
for a in "covid-cov-gate23 us-covid-production-coverage covid-gate-23" "rsv-cov-gate23 us-rsv-production-coverage rsv-gate-23" "covid-cov-r25 us-covid-short-term-coverage covid-round-25" \
         "rsv-cov-r25 us-rsv-short-term-coverage rsv-round-25" "covid-cov-fwd25 us-covid-forward-2025-26-coverage covid-round-25" "rsv-cov-fwd25 us-rsv-forward-2025-26-coverage rsv-round-25" \
         "covid-cov-release2 us-covid-production-coverage covid-release-seeds-2" "rsv-cov-release2 us-rsv-production-coverage rsv-release-seeds-2" \
         "covid-cov-reseed06 us-covid-short-term-coverage covid-reseed-06" "rsv-cov-reseed06 us-rsv-short-term-coverage rsv-reseed-06" \
         "covid-cov-reseedfwd06 us-covid-forward-2025-26-coverage covid-reseed-06" "rsv-cov-reseedfwd06 us-rsv-forward-2025-26-coverage rsv-reseed-06"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r25 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate23 rsv-cov-gate23 covid-cov-r25 rsv-cov-r25 covid-cov-fwd25 rsv-cov-fwd25 covid-cov-release2 rsv-cov-release2 covid-cov-reseed06 rsv-cov-reseed06 covid-cov-reseedfwd06 rsv-cov-reseedfwd06
# 2026-11-20 03:25 EST: cancelled redundant 9906450; round 26 + gate 24 (random search with categorical choices, 8 seeds), job 9909768
scancel 9906450
for a in "covid-cov-gate24 us-covid-production-coverage covid-gate-24" "rsv-cov-gate24 us-rsv-production-coverage rsv-gate-24" "covid-cov-r26 us-covid-short-term-coverage covid-round-26" \
         "rsv-cov-r26 us-rsv-short-term-coverage rsv-round-26" "covid-cov-fwd26 us-covid-forward-2025-26-coverage covid-round-26" "rsv-cov-fwd26 us-rsv-forward-2025-26-coverage rsv-round-26"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-r26 --array=0-5 scripts/covid_tree.sbatch covid-cov-gate24 rsv-cov-gate24 covid-cov-r26 rsv-cov-r26 covid-cov-fwd26 rsv-cov-fwd26
# 2026-11-20 04:25 EST: 40-seed live check of the recommended releases against the replayed submitted fits
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e covid-cov-gate03 covid-cov-gate02 covid-cov-gate06 covid-cov-final covid-cov-release covid-cov-partners covid-cov-release2 covid-replay-submitted --hub covid --mix "Rec40=T.pN_gru.real.log_loss1+T.pN_gru.real+S.Ah.gru_national.real" "SUBMITTED-FITS=Ah.neighbors+pN.enc_gru+N.multiscale+Bh.wd"
PYTHONPATH=src .venv/bin/python scripts/score_gate_hub_truth.py -e rsv-cov-gate07 rsv-cov-confirm rsv-cov-gate04 rsv-cov-final2 rsv-cov-release2 rsv-replay-submitted --hub rsv --mix "W1_40=A4c0.national.rsvnet.calendar.weeks1" "SUBMITTED-FITS=Ball_c0w512+Bw+A4c0+A4i"
# 2026-11-20 05:25 EST: backtest reseed 7 (seeds 64-79) of the recommended members, last GPU stage
for a in "covid-cov-reseed07 us-covid-short-term-coverage covid-reseed-07" "rsv-cov-reseed07 us-rsv-short-term-coverage rsv-reseed-07" \
         "covid-cov-reseedfwd07 us-covid-forward-2025-26-coverage covid-reseed-07" "rsv-cov-reseedfwd07 us-rsv-forward-2025-26-coverage rsv-reseed-07"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-reseed07 --array=0-5 scripts/covid_tree.sbatch covid-cov-reseed07 rsv-cov-reseed07 covid-cov-reseedfwd07 rsv-cov-reseedfwd07
# 2026-11-20 07:25 EST: final backtest mixtures on 36 seeds (CPU 9922986-90); last GPU stage, backtest seeds for open trade-offs (9922954)
for p in covid rsv; do for k in main forward; do python3 scripts/mix_seed_groups.py $p $k final; sbatch --job-name=$p-mixfinal-$k scripts/covid_tree_mix.sbatch experiments/covid-rsv-coverage-20261118/$p-mix-final-$k.json data/experiments/$p-cov-mixfinal/$k; done; done
for a in "rsv-cov-reseed08 us-rsv-short-term-coverage rsv-reseed-08" "rsv-cov-reseedfwd08 us-rsv-forward-2025-26-coverage rsv-reseed-08" \
         "covid-cov-reseed08 us-covid-short-term-coverage covid-reseed-08" "covid-cov-reseedfwd08 us-covid-forward-2025-26-coverage covid-reseed-08"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=cov-reseed08 --array=0-5 scripts/covid_tree.sbatch rsv-cov-reseed08 rsv-cov-reseedfwd08 covid-cov-reseed08 covid-cov-reseedfwd08
# 2026-11-20 08:25 EST: RSV local search around RS200 redone from the RSV round-22 file (round 23 had taken COVID's RS200), job 9929041
for a in "rsv-cov-gate25 us-rsv-production-coverage rsv-gate-25" "rsv-cov-r23b us-rsv-short-term-coverage rsv-round-23b" "rsv-cov-fwd23b us-rsv-forward-2025-26-coverage rsv-round-23b"; do set -- $a
  .venv/bin/python -m chromantis.experiment.planner plan -e $1 --problem problems/$2.json --study $S/$3.json --device cuda
done
sbatch --job-name=rsv-r23b --array=0-5 scripts/covid_tree.sbatch rsv-cov-gate25 rsv-cov-r23b rsv-cov-fwd23b
# 2026-11-20 10:52 EST: run ended; hourly check stopped. Nothing queued.
