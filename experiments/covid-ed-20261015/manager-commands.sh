# Run in chadi@longleaf.unc.edu:/proj/jlessler/projects/tapestry-all/covid-20261014
export PYTHONPATH=src
.venv/bin/python -m chromantis.experiment.planner plan -e covid-ed-forward --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-ed-20261015/forward.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-ed-screen --problem problems/us-covid-short-term-prescribed.json --study experiments/covid-ed-20261015/screen.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-ed-confirm --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-ed-20261015/confirm.json --device cuda
sbatch --job-name=covid-ed-L40 --array=0-3 --nodelist=g1803jles01 scripts/covid_ed.sbatch
sbatch --job-name=covid-ed-H100 --array=0-1 --nodelist=g1803jles02 scripts/covid_ed.sbatch
for experiment in covid-ed-forward covid-ed-screen covid-ed-confirm; do
 .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
 .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --allow-incomplete --no-report
done

# 12:45 ET: existing forward plan80fits complete. Shared scorer separates learned targets.
sbatch --job-name=covid-ed-forward-score --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=01:00:00 --output=output/slurm/covid-ed-forward-score-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python scripts/rank_covid_ed.py -e covid-ed-forward --no-report'
# Mixture plan: mixtures-forward.json, no refitting.
sbatch --job-name=covid-ed-forward-mixtures --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=01:30:00 --output=output/slurm/covid-ed-forward-mixtures-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-ed-20261015/mixtures-forward.json --out data/experiments/covid-ed-forward-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-ed-forward-mixtures'
.venv/bin/python -m chromantis.experiment.planner status -e covid-ed-forward
.venv/bin/python scripts/rank_covid_ed.py -e covid-ed-forward --no-report
# Group ranking: data/experiments/covid-ed-forward-mixtures/ranking/headline-rankings.csv

# 13:15 ET: target-routing plan in scripts/score_covid_target_routes.py.
# Source plan covid-ed-forward and mixtures-forward.json above; no refitting.
sbatch --job-name=covid-ed-target-routes --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=01:00:00 --output=output/slurm/covid-ed-target-routes-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python scripts/score_covid_target_routes.py && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-ed-target-routes'
.venv/bin/python -m chromantis.experiment.planner status -e covid-ed-forward
.venv/bin/python scripts/rank_covid_ed.py -e covid-ed-forward --no-report
# Routed forecast rank: data/experiments/covid-ed-target-routes/ranking/hub-relative-scores.csv

# 13:45 ET adaptive ED-only combinations and provisional production recipes.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-ed-specialists --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-ed-20261015/specialists.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-ed-production --problem problems/us-covid-production.json --study experiments/covid-ed-20261015/production.json --device cuda
sbatch --job-name=covid-ed-followup-H100 --array=0-1 --nodelist=g1803jles02 --dependency=afterany:4998183 scripts/covid_ed_followup.sbatch
sbatch --job-name=covid-ed-switch scripts/covid_ed_switch.sbatch 4998183
sbatch --job-name=covid-ed-confirm-mixtures --dependency=afterok:5010819 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=01:30:00 --output=output/slurm/covid-ed-confirm-mixtures-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; .venv/bin/python scripts/rank_covid_ed.py -e covid-ed-confirm --no-report && .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-ed-20261015/mixtures-confirm.json --out data/experiments/covid-ed-confirm-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-ed-confirm-mixtures'
for experiment in covid-ed-specialists covid-ed-confirm; do
 .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
 .venv/bin/python scripts/rank_covid_ed.py -e "$experiment" --allow-incomplete --no-report
done
.venv/bin/python -m chromantis.experiment.planner status -e covid-ed-production
.venv/bin/python -m chromantis.experiment.planner rank -e covid-ed-production --no-report
# Confirmation mixture plan: mixtures-confirm.json; scorer writes OUT/ranking.

# 14:15 ET matched interaction study and ED-only all-season fits.
.venv/bin/python -m chromantis.experiment.planner plan -e covid-ed-combined --problem problems/us-covid-forward-2025-26-reported.json --study experiments/covid-ed-20261015/combined.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e covid-ed-production-specialists --problem problems/us-covid-production.json --study experiments/covid-ed-20261015/production-specialists.json --device cuda
sbatch --job-name=covid-ed-combined-L40 --array=0-3 --nodelist=g1803jles01 --dependency=afterany:4998182 scripts/covid_ed_combined.sbatch
# Replacement5018127 accepted before releasing old reserve workers.
scancel 4998182
for experiment in covid-ed-combined covid-ed-production-specialists; do
 .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
 .venv/bin/python scripts/rank_covid_ed.py -e "$experiment" --allow-incomplete --no-report
done

# 14:45 ET saved-fit plans: mixtures-specialists.json and mixtures-combined.json.
# Uses completed specialist/combined training plans above; no refitting.
sbatch --job-name=covid-ed-final-mixtures --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=01:00:00 --output=output/slurm/covid-ed-final-mixtures-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; for branch in specialists combined; do .venv/bin/python scripts/rank_covid_ed.py -e covid-ed-${branch} --no-report && .venv/bin/python -m chromantis.evaluation.ensembles experiments/covid-ed-20261015/mixtures-${branch}.json --out data/experiments/covid-ed-${branch}-mixtures && .venv/bin/python scripts/score_covid_summer.py --ensemble-directory data/experiments/covid-ed-${branch}-mixtures || exit 1; done'
for experiment in covid-ed-specialists covid-ed-combined; do
 .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
 .venv/bin/python scripts/rank_covid_ed.py -e "$experiment" --no-report
done
# Mixture ranks: data/experiments/covid-ed-{specialists,combined}-mixtures/ranking/

# Local provisional export, source covid-ed-production plan above. No publication.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 .venv/bin/python -m chromantis.production run --release production/releases/covid-ed-fourth-root-candidate-20261015.json --dataset data/operational-20261014/processed/panel.npz --issuance 2026-10-14 --jobs 1 --no-pending

# 15:15 ET local export with explicit per-recipe output targets. No refit/publication.
# Sources: overnight production04 and current production plans, hashes fixed in releases.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 .venv/bin/python -m chromantis.production run --release production/releases/covid-target-routed-candidate-20261015.json --dataset data/operational-20261014/processed/panel.npz --issuance 2026-10-14 --jobs 1 --no-pending

# 15:45 ET final CPU score collection, after both GPU arrays stop at20:10UTC.
# Existing study plans above; no new training or changes to evaluation.
sbatch --job-name=covid-ed-final-ranks --dependency=afterany:5018127:5010816 --partition=jlessler --qos=normal --cpus-per-task=4 --mem=48G --time=02:00:00 --output=output/slurm/covid-ed-final-ranks-%j.log --wrap='export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; for experiment in covid-ed-forward covid-ed-screen covid-ed-confirm covid-ed-specialists covid-ed-combined; do .venv/bin/python scripts/rank_covid_ed.py -e "$experiment" --no-report || exit 1; done; .venv/bin/python -m chromantis.experiment.planner rank -e covid-reserve --allow-incomplete --no-report'
for experiment in covid-ed-forward covid-ed-screen covid-ed-confirm covid-ed-specialists covid-ed-combined; do
 .venv/bin/python -m chromantis.experiment.planner status -e "$experiment"
 .venv/bin/python scripts/rank_covid_ed.py -e "$experiment" --no-report
done
.venv/bin/python -m chromantis.experiment.planner rank -e covid-reserve --allow-incomplete --no-report
