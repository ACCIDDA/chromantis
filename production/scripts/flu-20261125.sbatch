#!/bin/bash
#SBATCH --job-name=flu-1125
#SBATCH --partition=jlessler
#SBATCH --qos=normal
#SBATCH --nodelist=g1803jles02
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=200G
#SBATCH --time=06:00:00
#SBATCH --output=output/slurm/%x-%j.log
# 25 Nov issuance (reference date 28 Nov): masked A (new release), B7 at half strength for comparison, Peak8 peak targets.
cd /hickory/proj/jlessler/projects/tapestry-all/tapestry
P=data/operational-20261125/processed/panel.npz
O=production/output/2026-11-25
mkdir -p $O
.venv/bin/python -m chromantis.dataset.build build --data-root data/operational-20261125 --workers 8 \
  --output $P > data/operational-20261125/build.log 2>&1 || { echo "FAILED build"; exit 1; }
sha256sum $P
.venv/bin/python -m chromantis.production.season_peak --checkpoints data/production-fits/peak-production-20261014 \
  --dataset $P --issuance 2026-11-25 --samples 6000 --out $O/peak-production-20261014 > $O/peak.log 2>&1 && echo "DONE peak" &
.venv/bin/python -m chromantis.production run --release production/releases/b7-cs050.json --dataset $P \
  --issuance 2026-11-25 --jobs 8 --no-plots > $O/b7-cs050.log 2>&1 && echo "DONE b7-cs050" || echo "FAILED b7-cs050"
.venv/bin/python -m chromantis.production run --release production/releases/masked-a-20261122.json --dataset $P \
  --issuance 2026-11-25 --jobs 40 --no-pending --compare-csv $O/b7-cs050/2026-11-28-ACCIDDA-Chromantis.csv \
  > $O/masked-a-20261122.log 2>&1 && echo "DONE masked-a" || echo "FAILED masked-a"
wait; echo ALL DONE
