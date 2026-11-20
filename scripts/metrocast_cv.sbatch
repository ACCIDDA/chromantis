#!/bin/bash
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=110G
#SBATCH --time=09:00:00
#SBATCH --output=output/slurm/%x-%A_%a.log
# Season-CV tree-search worker (2026-10-21). Each iteration asks metrocast_cv_tree.py for
# work: an experiment with pending fits, or SCORE (score finished runs), or a newly planned round.
set -uo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 PYTHONUNBUFFERED=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
stop=$(date -d "${STOP_UTC:-2026-10-22 12:40:00 UTC}" +%s)
lanes=${LANES:-8}
while (( $(date +%s) < stop )); do
    export PYTHONPATH="$PWD/src:$PWD/scripts"
    if ! work=$(.venv/bin/python scripts/metrocast_cv_tree.py next); then
        echo "planning failed; retry in 60 s" >&2; sleep 60; continue
    fi
    case "$work" in
        STOP) break ;;
        WAIT) sleep 30; continue ;;
        SCORE) .venv/bin/python scripts/metrocast_cv_score.py --device cuda --max-runs 12 || sleep 30; continue ;;
    esac
    export PYTHONPATH="$PWD/data/experiments/$work/code/src"
    remaining=$((stop - $(date +%s))); (( remaining > 0 )) || break
    echo "Starting $work with $lanes lanes at $(date -Is)"
    timeout --signal=TERM --kill-after=30 "$remaining" \
        .venv/bin/python -m chromantis.experiment.dispatch -e "$work" --lanes "$lanes" --gpu-count 6 || true
done
