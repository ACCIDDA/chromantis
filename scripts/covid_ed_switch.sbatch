#!/bin/bash
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=output/slurm/covid-switch-%j.log
set -euo pipefail
# Replacement GPU arrays must already be queued with afterany on these old arrays.
.venv/bin/python - "$@" <<'PY'
import csv, json, subprocess, sys, time
from pathlib import Path

def complete(name):
    p=Path('data/experiments')/name
    jobs=list(csv.DictReader((p/'jobs.csv').open()))
    expected={(j['scenario'],int(seed)) for j in jobs for seed in j['seeds'].split()}
    finished=set()
    for path in p.glob('*/s*/attempt-*/run.json'):
        r=json.loads(path.read_text())
        if r['status']=='complete': finished.add((r['scenario'],r['seed']))
    print(name,len(finished & expected),'/',len(expected),flush=True)
    return expected <= finished
while True:
    ready=[complete(n) for n in ['covid-ed-confirm']]
    if all(ready):
        subprocess.run(['scancel',*sys.argv[1:]],check=True)
        print('ED confirmation fits complete; released GPUs to dependent follow-up arrays.',flush=True)
        break
    time.sleep(30)
PY
