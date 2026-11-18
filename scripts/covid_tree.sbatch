#!/bin/bash
#SBATCH --job-name=covid-tree
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=110G
#SBATCH --time=2-00:00:00
#SBATCH --output=output/slurm/%x-%A_%a.log

# Fit several experiments in order on one array spanning every lab GPU, so the GPUs never wait
# for a person between rounds. The worker that finds no run left to fit queues its CPU scoring;
# runs that failed after retries do not hold scoring back (30 Oct: one crashed recipe blocked a round).
#   sbatch --array=0-5 scripts/covid_tree.sbatch EXPERIMENT [EXPERIMENT ...]
set -uo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 PYTHONUNBUFFERED=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
for experiment in "$@"; do
    export PYTHONPATH="$PWD/data/experiments/$experiment/code/src"
    echo "Starting $experiment at $(date -Is)"
    .venv/bin/python -m chromantis.experiment.dispatch -e "$experiment" --lanes 8 --gpu-count 6 --retry-failed
    if .venv/bin/python -m chromantis.experiment.planner status -e "$experiment" \
            | awk -F'\t' 'NF>=5 && $1!="complete" && $1!="failed" {left++} END {exit left>0}' \
            && mkdir "data/experiments/$experiment/scoring.lock" 2>/dev/null; then
        sbatch --job-name="$experiment-score" scripts/covid_tree_score.sbatch "$experiment"
    fi
done
