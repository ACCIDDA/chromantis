#!/bin/bash
#SBATCH --job-name=ebola-noise-bt
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=output/slurm/%x-%A_%a.log
# One task of scripts/ebola_noise_backtest.py per array element (90 = 5 folds x 3 recipes x 2 seeds x 3 noise strengths).
#   sbatch --array=0-89 scripts/ebola_noise_backtest.sbatch
set -euo pipefail
export PYTHONPATH=$PWD/src PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4
.venv/bin/python scripts/ebola_noise_backtest.py --task $SLURM_ARRAY_TASK_ID --out ${OUT:-output/ebola-noise-backtest} --device cuda
