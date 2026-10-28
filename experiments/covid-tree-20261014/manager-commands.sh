# Run on Longleaf. Existing experiments are already planned; do not re-plan
# while running. Use status to obtain the exact retry command for stopped fits.
cd /proj/jlessler/projects/tapestry-all/covid-20261014
export PYTHONPATH="$PWD/src"
.venv/bin/python -m chromantis.experiment.planner plan -e covid-r01 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261014/round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-production-baselines --problem problems/us-covid-production.json --study experiments/covid-tree-20261014/production-baselines.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-structure --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261014/branch-structure.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-reserve --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261014/reserve.json --device cuda
# These launches run each preplanned queue in order, stopping at 9 AM ET.
sbatch --job-name=covid-overnight-L40 --array=0-3 --nodelist=g1803jles01 scripts/covid_overnight.sbatch
sbatch --job-name=covid-overnight-H100 --array=0-1 --nodelist=g1803jles02 scripts/covid_overnight.sbatch
for experiment in covid-r01 covid-production-baselines covid-structure covid-reserve; do
    .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
    .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --allow-incomplete --no-report
done
# CPU ranking jobs automatically queued by the worker after each stage:
# sbatch --job-name=EXPERIMENT-progress scripts/rank.sbatch EXPERIMENT --allow-incomplete --no-report

# Interim scoring launched 2026-10-14 22:55 ET, Slurm 4938886.
# Uses the covid-r01 plan above; no refitting.
sbatch --job-name=covid-r01-check scripts/rank.sbatch covid-r01 --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-r01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-r01 --allow-incomplete --no-report

# Separate summer scoring, using saved forecasts from the covid-r01 plan.
sbatch --job-name=covid-summer --partition=jlessler --qos=normal --cpus-per-task=2 --mem=16G --time=00:30:00 --output=output/slurm/covid-summer-%j.log --wrap="PYTHONPATH=src OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/score_covid_summer.py -e covid-r01"
.venv/bin/python -m chromantis.experiment.planner status -e covid-r01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-r01 --allow-incomplete --no-report
# Summer score output: data/experiments/covid-r01/summer.csv; kept separate from primary ranking.

# Second interim rank, using the existing covid-r01 plan and completed fits.
sbatch --job-name=covid-r01-check2 scripts/rank.sbatch covid-r01 --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-r01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-r01 --allow-incomplete --no-report

# Adaptive follow-up, prepared 2026-10-14 23:58 ET. Do not re-plan running studies.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-forward --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261014/forward-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-confirm --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261014/confirm-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-r02 --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261014/round-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-production-02 --problem problems/us-covid-production.json --study experiments/covid-tree-20261014/production-02.json --device cuda
# Already submitted: 4945033, 4945034. Both wait for the old arrays to release all six GPUs.
sbatch --job-name=covid-followup-L40 --array=0-3 --nodelist=g1803jles01 --dependency=afterany:4936352:4936353 scripts/covid_followup.sbatch
sbatch --job-name=covid-followup-H100 --array=0-1 --nodelist=g1803jles02 --dependency=afterany:4936352:4936353 scripts/covid_followup.sbatch
# Already submitted: 4945035. Releases old arrays only after all screen and baseline fits complete.
sbatch --job-name=covid-switch scripts/covid_switch.sbatch 4936352 4936353
for experiment in covid-forward covid-confirm covid-r02 covid-production-02; do
    .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
    .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --allow-incomplete --no-report
done
# Mixture plan: mixtures-01.json names saved runs from the covid-r01 plan; no refitting.
# This command builds and ranks all named groups using the shared scorer.
sbatch --job-name=covid-mixtures01 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=03:00:00 --output=output/slurm/covid-mixtures01-%j.log --wrap="PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-01.json --out data/experiments/covid-mixtures01"
.venv/bin/python -m chromantis.experiment.planner status -e covid-r01
# Mixture ranking: data/experiments/covid-mixtures01/ranking/headline-rankings.csv

# After the complete first screen, score it and replay the same checkpoints on archived reports.
# No retraining. Uses the covid-r01 plan recorded above.
sbatch --job-name=covid-r01-reported --dependency=afterok:4945035 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=05:00:00 --output=output/slurm/covid-r01-reported-%j.log --wrap="export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 CHROMANTIS_TORCH_THREADS=2; .venv/bin/python -m chromantis.experiment.planner rank -e covid-r01 --no-report && .venv/bin/python scripts/score_covid_summer.py -e covid-r01 && .venv/bin/python -m chromantis.experiment.planner replay -e covid-r01 --inputs reported --device cpu && .venv/bin/python -m chromantis.experiment.planner rank -e covid-r01 --inputs reported --no-report && .venv/bin/python scripts/score_covid_summer.py -e covid-r01 --inputs reported"
.venv/bin/python -m chromantis.experiment.planner status -e covid-r01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-r01 --inputs reported --no-report

# 2026-10-15 00:30 ET: mixture plans use saved fits, no retraining.
# Source plans are covid-forward and covid-r01 above; groups explicitly name every recipe/seed.
# Jobs 4946240, 4946241, 4946242.
sbatch --job-name=covid-forward-mixtures --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=03:00:00 --output=output/slurm/covid-forward-mixtures-%j.log --wrap="export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/forward-mixtures.json --out data/experiments/covid-forward-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-forward-mixtures"
sbatch --job-name=covid-reported-mixtures --dependency=afterok:4945052 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=03:00:00 --output=output/slurm/covid-reported-mixtures-%j.log --wrap="export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-01-reported.json --out data/experiments/covid-mixtures01-reported && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-mixtures01-reported"
sbatch --job-name=covid-mixture-summer --partition=jlessler --qos=normal --cpus-per-task=2 --mem=16G --time=00:30:00 --output=output/slurm/covid-mixture-summer-%j.log --wrap="PYTHONPATH=src OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-mixtures01"
.venv/bin/python -m chromantis.experiment.planner status -e covid-forward
.venv/bin/python -m chromantis.experiment.planner rank -e covid-forward --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-r01
.venv/bin/python -m chromantis.experiment.planner rank -e covid-r01 --inputs reported --no-report
# Each ensemble command also ranks its groups into OUT/ranking/headline-rankings.csv.

# Local operational acceptance check (no training or historical scoring).
# Source fit plan/launch/status/rank: covid-production-baselines above.
# Run from /Users/chadi/Research/Tapestry after copying the named checkpoints.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 .venv/bin/python -m chromantis.production run --release production/releases/covid-baseline-candidate-20261015.json --dataset data/operational-20261014/processed/panel.npz --issuance 2026-10-14 --jobs 1 --no-pending

# Summer-only retry after excluding the ranking manifest from ensemble discovery.
sbatch --job-name=covid-mixture-summer-fix --dependency=afterany:4946240 --partition=jlessler --qos=normal --cpus-per-task=2 --mem=16G --time=01:00:00 --output=output/slurm/covid-mixture-summer-fix-%j.log --wrap="export PYTHONPATH=src OPENBLAS_NUM_THREADS=1; .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-mixtures01 && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-forward-mixtures"
# Same source plans; no refit. Status/rank commands for covid-r01 and covid-forward above.

# 2026-10-15 01:00 ET. Fixed mixtures of 3-4 recipes, all subsets.
# Source plans: covid-r01, covid-confirm and covid-forward above. No model refitting.
# Jobs 4948770 and 4948771. Each ensembles command writes its own ranking tables.
sbatch --job-name=covid-mixtures02 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=03:00:00 --output=output/slurm/covid-mixtures02-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; for comparison in screen confirm forward; do .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-02-${comparison}.json --out data/experiments/covid-mixtures02-${comparison} && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-mixtures02-${comparison} || exit 1; done'
sbatch --job-name=covid-mixtures02-reported --dependency=afterok:4945052 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/slurm/covid-mixtures02-reported-%j.log --wrap="export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-02-reported.json --out data/experiments/covid-mixtures02-reported && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-mixtures02-reported"
for experiment in covid-r01 covid-confirm covid-forward; do
    .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
    .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --no-report
done

# Local provisional mixture export checks. Source fit plans: covid-production-baselines
# and covid-production-02 above; model hashes fixed in the release files. Nothing published.
for release in covid-reported-wide-candidate-20261015 covid-artificial-pair-candidate-20261015; do
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 .venv/bin/python -m chromantis.production run --release production/releases/$release.json --dataset data/operational-20261014/processed/panel.npz --issuance 2026-10-14 --jobs 1 --no-pending
done

# 2026-10-15 02:00 ET: data-treatment branch, with matched roots and new seeds 54-57.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-data --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-tree-20261014/data-branch.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-data-forward --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261014/data-forward.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-production-03 --problem problems/us-covid-production.json --study experiments/covid-tree-20261014/production-03.json --device cuda
# Replacement two-H100 array is queued before releasing its predecessor;
# the four L40s continue the architecture experiment uninterrupted.
sbatch --job-name=covid-data-H100 --array=0-1 --nodelist=g1803jles02 --dependency=afterany:4945034 scripts/covid_data.sbatch
scancel 4945034
for experiment in covid-data covid-data-forward covid-production-03; do
    .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
    .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --allow-incomplete --no-report
done

# 03:00 ET: saved-fit mixture plan: mixtures-data-forward.json; no retraining.
# Source training plan: covid-data-forward above; seeds54-57.
sbatch --job-name=covid-data-forward-mixtures --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/slurm/covid-data-forward-mixtures-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python scripts/score_covid_summer.py -e covid-data-forward && .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-data-forward.json --out data/experiments/covid-data-forward-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-data-forward-mixtures'
.venv/bin/python -m chromantis.experiment.planner status -e covid-data-forward
.venv/bin/python -m chromantis.experiment.planner rank -e covid-data-forward --no-report
# Mixture rank: data/experiments/covid-data-forward-mixtures/ranking/headline-rankings.csv

# 04:00 ET: independent half-perturbation confirmation and provisional all-season fits.
# Run in isolated cluster checkout with PYTHONPATH=src. Do not re-plan active studies.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-forward-confirm02 --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-tree-20261014/forward-confirm-02.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-production-04 --problem problems/us-covid-production.json --study experiments/covid-tree-20261014/production-04.json --device cuda
sbatch --job-name=covid-confirm02-H100 --array=0-1 --nodelist=g1803jles02 --dependency=afterany:4951321 scripts/covid_confirm02.sbatch
# Only after the replacement array is accepted, release this study's previous H100 array:
scancel 4951321
for experiment in covid-forward-confirm02 covid-production-04 covid-data; do
    .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
    .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --allow-incomplete --no-report
done

# 04:25 ET saved-fit scoring plan: mixtures-forward-confirm02.json (source plan above).
sbatch --job-name=covid-confirm02-mixtures --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/slurm/covid-confirm02-mixtures-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python scripts/score_covid_summer.py -e covid-forward-confirm02 && .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-forward-confirm02.json --out data/experiments/covid-confirm02-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-confirm02-mixtures'
.venv/bin/python -m chromantis.experiment.planner status -e covid-forward-confirm02
.venv/bin/python -m chromantis.experiment.planner rank -e covid-forward-confirm02 --no-report
# Ensemble rank: data/experiments/covid-confirm02-mixtures/ranking/headline-rankings.csv
# Refresh complete confirmation ranking; automatic stage ranking captured an early subset.
sbatch --job-name=covid-confirm02-fullrank scripts/rank.sbatch covid-forward-confirm02 --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-forward-confirm02
.venv/bin/python -m chromantis.experiment.planner rank -e covid-forward-confirm02 --no-report

# 05:00 ET local operational export check; source production04 plan/launch/status above.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 .venv/bin/python -m chromantis.production run --release production/releases/covid-half-perturbation-candidate-20261015.json --dataset data/operational-20261014/processed/panel.npz --issuance 2026-10-14 --jobs 1 --no-pending

# 05:25 ET scoring completed data branch and interim structure fits. Source plans above.
# Mixture plan: mixtures-data.json; no refitting.
sbatch --job-name=covid-data-mixtures --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/slurm/covid-data-mixtures-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python -m chromantis.experiment.planner rank -e covid-data --no-report && .venv/bin/python scripts/score_covid_summer.py -e covid-data && .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-data.json --out data/experiments/covid-data-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-data-mixtures'
sbatch --job-name=covid-structure-check scripts/rank.sbatch covid-structure --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-data
.venv/bin/python -m chromantis.experiment.planner rank -e covid-data --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-structure
.venv/bin/python -m chromantis.experiment.planner rank -e covid-structure --allow-incomplete --no-report
# Mixture ranking: data/experiments/covid-data-mixtures/ranking/headline-rankings.csv

# 06:00 ET replay plan: existing covid-data fits, seeds54-57, archived evaluation inputs.
# No retraining. Mixture plan: mixtures-data-reported.json.
sbatch --job-name=covid-data-replay --array=0-3 scripts/covid_data_replay.sbatch
sbatch --job-name=covid-data-reported-score --dependency=afterok:4967316 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=01:00:00 --output=output/slurm/covid-data-reported-score-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python -m chromantis.experiment.planner rank -e covid-data --inputs reported --no-report && .venv/bin/python scripts/score_covid_summer.py -e covid-data --inputs reported && .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-tree-20261014/mixtures-data-reported.json --out data/experiments/covid-data-reported-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-data-reported-mixtures'
.venv/bin/python -m chromantis.experiment.planner status -e covid-data
.venv/bin/python -m chromantis.experiment.planner rank -e covid-data --inputs reported --no-report
# Mixture rank: data/experiments/covid-data-reported-mixtures/ranking/headline-rankings.csv

# 07:25 ET refresh architecture scores as more seeds complete; existing structure plan above.
sbatch --job-name=covid-structure-check0730 scripts/rank.sbatch covid-structure --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-structure
.venv/bin/python -m chromantis.experiment.planner rank -e covid-structure --allow-incomplete --no-report

# 08:00 ET: final CPU ranking queued after both existing GPU arrays end at cutoff.
# Uses existing structure/reserve plans, no training. Reserve may be empty.
sbatch --job-name=covid-final-ranks --dependency=afterany:4945033:4953586 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/slurm/covid-final-ranks-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; for experiment in covid-structure covid-reserve; do .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"; .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --allow-incomplete --no-report; done'
.venv/bin/python -m chromantis.experiment.planner status -e covid-structure
.venv/bin/python -m chromantis.experiment.planner rank -e covid-structure --allow-incomplete --no-report
.venv/bin/python -m chromantis.experiment.planner status -e covid-reserve
.venv/bin/python -m chromantis.experiment.planner rank -e covid-reserve --allow-incomplete --no-report
