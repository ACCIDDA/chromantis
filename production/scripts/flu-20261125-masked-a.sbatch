#!/bin/bash
#SBATCH --job-name=flu-1125a
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodelist=g1803jles02
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=200G
#SBATCH --time=06:00:00
#SBATCH --output=output/slurm/%x-%j.log
# 25 Nov issuance (reference date 28 Nov): masked A on the coverage panel (its fits were trained on the coverage problem).
cd /hickory/proj/jlessler/projects/tapestry-all/tapestry
R=data/operational-20261125
P=$R/processed/panel-coverage.npz
O=production/output/2026-11-25
.venv/bin/python -m chromantis.dataset.build build --data-root $R --spec datasets/respiratory-us-weekly-coverage.json \
  --workers 8 --output $P > $R/build-coverage.log 2>&1 || { echo "FAILED build"; exit 1; }
sha256sum $P
.venv/bin/python -m chromantis.production run --release production/releases/masked-a-20261122.json --dataset $P \
  --issuance 2026-11-25 --jobs 40 --no-pending --compare-csv $O/b7-cs050/2026-11-28-ACCIDDA-Chromantis.csv \
  > $O/masked-a-20261122.log 2>&1 && echo "DONE masked-a" || echo "FAILED masked-a"
echo ALL DONE
