#!/bin/bash
#SBATCH --job-name=covid-tree-mix
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=output/slurm/%x-%j.log

# Score equal mixtures of saved forecasts, without refitting.
#   sbatch scripts/covid_tree_mix.sbatch GROUPS.json OUT
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 PYTHONPATH=src
.venv/bin/python -m chromantis.evaluation.ensembles "$1" --out "$2"
