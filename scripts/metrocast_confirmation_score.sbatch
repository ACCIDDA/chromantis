#!/bin/bash
#SBATCH --partition=general
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=10:00:00
#SBATCH --output=output/slurm/%x-%j.log
set -euo pipefail
export PYTHONPATH="$PWD/src"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python - "$1" <<'PY'
import sys,time
from pathlib import Path
from chromantis.experiment.planner import collect
end=time.monotonic()+7*3600
while True:
    rows=collect(Path('data/experiments')/sys.argv[1])
    if rows and all(r['status']=='complete' for r in rows): break
    if any(r['status']=='failed' for r in rows) or time.monotonic()>=end:
        raise RuntimeError('Confirmation fits failed or remain unfinished after seven hours; inspect and resume scoring')
    time.sleep(60)
PY
if [[ "$1" == metrocast-california-confirm-* ]]; then
    .venv/bin/python scripts/score_metrocast_california.py -e "$1" --confirmation
elif [[ "$1" == metrocast-full-season-confirm-* || "$1" == metrocast-utah-confirm-* ]]; then
    .venv/bin/python scripts/score_metrocast_full_season.py -e "$1" --paths --confirmation
fi
if [[ "$1" != metrocast-california-confirm-* && "$1" != metrocast-utah-confirm-* ]]; then
    .venv/bin/python scripts/score_metrocast_confirmation.py -e "$1"
fi
.venv/bin/python -m chromantis.experiment.planner rank -e "$1" --no-report
