#!/bin/bash
#SBATCH --job-name=flu-search-score
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=output/slurm/%x-%j.log

# Rank one finished flu-search experiment on its own evaluation inputs (archived reports for the main problem,
# artificial 2023-24 reports for the guard). No replay.
set -euo pipefail
experiment=${1:?usage: sbatch scripts/flu_search_score.sbatch EXPERIMENT}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1
export PYTHONPATH="$PWD/data/experiments/$experiment/code/src"
.venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --no-report --allow-incomplete
