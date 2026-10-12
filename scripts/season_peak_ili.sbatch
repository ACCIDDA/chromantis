#!/bin/bash
#SBATCH --job-name=season-peak-ili-score
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodelist=g1803jles02
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=output/slurm/%x-%j.log
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
.venv/bin/python -m chromantis.experiment.planner status -e season-peak-ili
.venv/bin/python -m chromantis.experiment.planner rank -e season-peak-ili --no-report
.venv/bin/python scripts/finish_season_peak_ili.py
