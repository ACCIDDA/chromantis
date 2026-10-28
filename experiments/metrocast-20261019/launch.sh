#!/bin/bash
set -euo pipefail
cd /hickory/proj/jlessler/projects/tapestry-all/metrocast-20261019
export PYTHONPATH="$PWD/src"
if (( $(date +%s) >= $(date -d '2026-10-21 13:30:00 UTC' +%s) )); then
    echo 'The authorized research window has ended.'
    exit 0
fi
if squeue -a -h -u "$USER" -o '%j' | grep -q '^metrocast-tree-'; then
    echo 'MetroCast workers are already queued or running; use metrocast_tree.py status.'
    exit 0
fi
# Plan the initial study if necessary. Later studies are planned by the GPU workers.
.venv/bin/python scripts/metrocast_tree.py next
# The second allocation on each node is queued before the first starts training.
# Each allocation already contains the recursive next-round loop in its saved script.
l40=$(LANES=4 sbatch --parsable --job-name=metrocast-tree-l40 --array=0-3 \
    --nodelist=g1803jles01 scripts/metrocast_tree.sbatch)
h100=$(LANES=8 sbatch --parsable --job-name=metrocast-tree-h100 --array=0-1 \
    --nodelist=g1803jles02 scripts/metrocast_tree.sbatch)
l40next=$(LANES=4 sbatch --parsable --job-name=metrocast-tree-l40-next --array=0-3 \
    --nodelist=g1803jles01 --dependency="afterany:$l40" scripts/metrocast_tree.sbatch)
h100next=$(LANES=8 sbatch --parsable --job-name=metrocast-tree-h100-next --array=0-1 \
    --nodelist=g1803jles02 --dependency="afterany:$h100" scripts/metrocast_tree.sbatch)
printf 'L40=%s\nH100=%s\nL40_NEXT=%s\nH100_NEXT=%s\n' "$l40" "$h100" "$l40next" "$h100next" \
    | tee experiments/metrocast-20261019/slurm-jobs.txt
.venv/bin/python scripts/metrocast_tree.py status
