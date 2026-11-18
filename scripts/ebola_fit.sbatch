#!/bin/bash
#SBATCH --job-name=ebola-fit
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=03:00:00
#SBATCH --output=output/slurm/%x-%A_%a.log
# One seed of RECIPE (default top035) per array element (42-45), on one GPU each; a seed takes 30 s to 3 min.
#   RECIPE=top004_r026_child20 sbatch --export=ALL --array=0-3 scripts/ebola_fit.sbatch
set -euo pipefail
export PYTHONPATH=$PWD/src PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4
seed=$((42 + SLURM_ARRAY_TASK_ID))
.venv/bin/python scripts/ebola_project.py fit --recipe ${RECIPE:-top035_r020_child09} --seeds $seed --out ${OUT:-data/ebola/ensemble-2026-11-21} --hub hub --device cuda --input-noise ${NOISE:-0.5}
