#!/bin/bash
#SBATCH --job-name=covid-tree-score
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=output/slurm/%x-%j.log

# Rank a finished experiment. A prescribed-input experiment is also replayed, without
# refitting, on archived Wednesday reports (one process per seed), then ranked again.
set -euo pipefail
experiment=${1:?usage: sbatch scripts/covid_tree_score.sbatch EXPERIMENT}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1
export PYTHONPATH="$PWD/data/experiments/$experiment/code/src"
.venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --no-report --allow-incomplete
if grep -q '"inputs": "prescribed"' "data/experiments/$experiment/problem.json"; then
    seeds=$(.venv/bin/python -c "
import csv
print(*sorted({s for r in csv.DictReader(open('data/experiments/$experiment/jobs.csv')) for s in r['seeds'].split()}))")
    for seed in $seeds; do
        .venv/bin/python -m chromantis.experiment.planner replay -e "$experiment" --inputs reported --device cpu --seeds "$seed" &
    done
    wait
    .venv/bin/python -m chromantis.experiment.planner rank -e "$experiment" --inputs reported --no-report --allow-incomplete
fi
