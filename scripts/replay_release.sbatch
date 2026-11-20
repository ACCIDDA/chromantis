#!/bin/bash
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=output/slurm/%x-%j.log
export PYTHONPATH=src OMP_NUM_THREADS=8
.venv/bin/python scripts/replay_release.py "$@"
