#!/bin/bash
#SBATCH --job-name=flu-search
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=110G
#SBATCH --time=2-00:00:00
#SBATCH --output=output/slurm/%x-%A_%a.log

# Flu search (flu-search-20261120): fit several experiments in order on one array spanning the lab GPUs,
# as scripts/covid_tree.sbatch. The worker that finds an experiment finished queues its CPU scoring
# (scripts/flu_search_score.sbatch); element 0 queues an ntfy summary for the whole array (NTFY=0 disables).
#   [LANES=3] sbatch --array=0-5 scripts/flu_search.sbatch EXPERIMENT [EXPERIMENT ...]   (fewer lanes for memory-heavy recipes)
set -uo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 PYTHONUNBUFFERED=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
if [ "${NTFY:-1}" != "0" ] && [ "${SLURM_ARRAY_TASK_ID:-0}" = "${SLURM_ARRAY_TASK_MIN:-0}" ]; then
    sbatch --job-name="$1-notify" --dependency="afterany:${SLURM_ARRAY_JOB_ID:-$SLURM_JOB_ID}" --kill-on-invalid-dep=yes \
        scripts/notify.sbatch "$1" "${SLURM_ARRAY_JOB_ID:-$SLURM_JOB_ID}" >/dev/null 2>&1 || echo 'warning: no ntfy summary' >&2
fi
for experiment in "$@"; do
    export PYTHONPATH="$PWD/data/experiments/$experiment/code/src"
    echo "Starting $experiment at $(date -Is)"
    .venv/bin/python -m chromantis.experiment.dispatch -e "$experiment" --lanes "${LANES:-8}" --gpu-count 6 --retry-failed
    if .venv/bin/python -m chromantis.experiment.planner status -e "$experiment" \
            | awk -F'\t' 'NF>=5 && $1!="complete" && $1!="failed" {left++} END {exit left>0}' \
            && mkdir "data/experiments/$experiment/scoring.lock" 2>/dev/null; then
        sbatch --job-name="$experiment-score" scripts/flu_search_score.sbatch "$experiment"
    fi
done
