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
deadline=time.monotonic()+7*3600
while True:
    records=collect(Path('data/experiments')/sys.argv[1])
    if records and all(r['status']=='complete' for r in records): break
    if any(r['status']=='failed' for r in records) or time.monotonic()>deadline:
        raise RuntimeError('Current-season fits failed or export wait expired; inspect and resume')
    time.sleep(60)
PY
.venv/bin/python scripts/export_metrocast_current.py -e "$1"
.venv/bin/python -m chromantis.experiment.planner rank -e "$1" --no-report
