"""Inspect every allocated MetroCast GPU, including jobs in the hidden partition."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess


def main():
    text = subprocess.check_output(
        ['squeue', '-a', '-r', '-h', '-u', os.environ['USER'], '-o', '%A %j %T'], text=True)
    jobs = [line.split()[0] for line in text.splitlines()
            if line.split()[1].startswith('metrocast-tree') and line.split()[2] == 'RUNNING']

    def probe(job):
        try:
            p = subprocess.run(
                ['srun', '--jobid=' + job, '--overlap', '--ntasks=1', '--cpus-per-task=1',
                 'nvidia-smi', '--query-gpu=uuid,name,utilization.gpu,memory.used,memory.total',
                 '--format=csv,noheader,nounits'], text=True, capture_output=True, timeout=40)
            return dict(job=job, returncode=p.returncode, gpu=p.stdout.strip(), error=p.stderr.strip())
        except subprocess.TimeoutExpired:
            return dict(job=job, error='GPU status probe timed out')

    records = list(ThreadPoolExecutor(6).map(probe, jobs))
    result = dict(time=datetime.now(timezone.utc).isoformat(), running_allocations=len(jobs), probes=records)
    path = Path('experiments/metrocast-20261019/gpu-checks.jsonl')
    with path.open('a') as out:
        out.write(json.dumps(result) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
