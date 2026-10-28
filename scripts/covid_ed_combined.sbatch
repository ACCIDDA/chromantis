#!/bin/bash
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=110G
#SBATCH --time=04:00:00
#SBATCH --output=output/slurm/%x-%A_%a.log
set -euo pipefail
# Every allocation has its next stages already in Slurm's saved job script.
# UTC timestamp is 4:10 PM America/New_York, 15 October 2026.
stop=$(date -d '2026-10-15 20:10:00 UTC' +%s)
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 PYTHONUNBUFFERED=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
for experiment in covid-ed-combined covid-ed-production-specialists covid-reserve; do
    remaining=$((stop - $(date +%s)))
    (( remaining > 0 )) || exit 0
    export PYTHONPATH="$PWD/data/experiments/$experiment/code/src"
    echo "Starting $experiment at $(date -Is), ${remaining}s until stop"
    timeout --signal=TERM --kill-after=30 "$remaining" .venv/bin/python -m chromantis.experiment.dispatch -e "$experiment" --lanes 8 --gpu-count 6 --retry-failed || rc=$?
    if [[ ${rc:-0} == 124 || ${rc:-0} == 137 ]]; then exit 0; fi
    # Rank on CPU separately; failures do not strand the reserved GPUs.
    if [[ ${SLURM_ARRAY_TASK_ID:-0} == 0 ]]; then
        sbatch --job-name="$experiment-progress" scripts/rank.sbatch "$experiment" --allow-incomplete --no-report || true
    fi
    unset rc
 done
