#!/bin/bash
#SBATCH --job-name=peak-logtiming-score
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodelist=g1803jles02
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=output/slurm/%x-%j.log
set -euo pipefail
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1
.venv/bin/python -m chromantis.experiment.planner status -e season-peak-logtiming
.venv/bin/python -m chromantis.experiment.planner rank -e season-peak-logtiming --no-report
.venv/bin/python scripts/score_peak_logtiming.py
