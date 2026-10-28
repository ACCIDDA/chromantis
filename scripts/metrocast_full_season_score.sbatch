#!/bin/bash
#SBATCH --partition=general
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
#SBATCH --output=output/slurm/%x-%j.log
set -euo pipefail
export PYTHONPATH="$PWD/src"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python scripts/score_metrocast_full_season.py -e "$1" --paths "${@:2}"
.venv/bin/python -m chromantis.experiment.planner rank -e "$1" --allow-incomplete --no-report
