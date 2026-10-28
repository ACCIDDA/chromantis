#!/bin/bash
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=output/slurm/covid-data-replay-%A_%a.log
set -euo pipefail
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1
.venv/bin/python -m chromantis.experiment.planner replay -e covid-data --inputs reported --device cpu --seeds "$((54 + SLURM_ARRAY_TASK_ID))"
