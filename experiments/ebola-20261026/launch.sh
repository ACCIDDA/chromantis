#!/bin/bash
set -euo pipefail
cd /hickory/proj/jlessler/projects/tapestry-all/ebola-20261026
export PYTHONPATH="$PWD/src"
if squeue -a -h -u "$USER" -o '%j' | grep -q '^ebola-tree-'; then
    echo 'Ebola workers are already queued or running; use ebola_tree.py status.'
    exit 0
fi
.venv/bin/python scripts/ebola_tree.py next
# Each allocation loops over rounds until the stop time; a second allocation per GPU is queued
# behind the first so a crash or time limit does not leave the GPU idle.
l40=$(LANES=4 sbatch --parsable --job-name=ebola-tree-l40 --array=0-3 --nodelist=g1803jles01 scripts/ebola_tree.sbatch)
h100=$(LANES=8 sbatch --parsable --job-name=ebola-tree-h100 --array=0-1 --nodelist=g1803jles02 scripts/ebola_tree.sbatch)
l40next=$(LANES=4 sbatch --parsable --job-name=ebola-tree-l40-next --array=0-3 --nodelist=g1803jles01 \
    --dependency="afterany:$l40" scripts/ebola_tree.sbatch)
h100next=$(LANES=8 sbatch --parsable --job-name=ebola-tree-h100-next --array=0-1 --nodelist=g1803jles02 \
    --dependency="afterany:$h100" scripts/ebola_tree.sbatch)
printf 'L40=%s\nH100=%s\nL40_NEXT=%s\nH100_NEXT=%s\n' "$l40" "$h100" "$l40next" "$h100next" \
    | tee experiments/ebola-20261026/slurm-jobs.txt
.venv/bin/python scripts/ebola_tree.py status
