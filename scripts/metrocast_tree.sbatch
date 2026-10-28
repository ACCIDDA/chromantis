#!/bin/bash
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=110G
#SBATCH --time=17:00:00
#SBATCH --output=output/slurm/%x-%A_%a.log
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CHROMANTIS_TORCH_THREADS=1 PYTHONUNBUFFERED=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
stop=$(date -d '2026-10-21 13:30:00 UTC' +%s)
lanes=${LANES:-4}
export PYTHONPATH="$PWD/src"
.venv/bin/python -c 'import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))'
while (( $(date +%s) < stop )); do
    export PYTHONPATH="$PWD/src"
    if ! experiment=$(.venv/bin/python scripts/metrocast_tree.py next); then
        echo "Tree planning failed; retrying in 60 seconds" >&2
        sleep 60
        continue
    fi
    [[ "$experiment" != STOP ]] || break
    export PYTHONPATH="$PWD/data/experiments/$experiment/code/src"
    remaining=$((stop - $(date +%s)))
    (( remaining > 0 )) || break
    echo "Starting $experiment with $lanes lanes at $(date -Is)"
    # Every allocation can advance to another planned branch while peers finish.
    timeout --signal=TERM --kill-after=30 "$remaining" \
        .venv/bin/python -m chromantis.experiment.dispatch -e "$experiment" --lanes "$lanes" --gpu-count 6 || rc=$?
    if [[ ${rc:-0} == 124 || ${rc:-0} == 137 ]]; then break; fi
    unset rc
done
