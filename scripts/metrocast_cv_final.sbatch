#!/bin/bash
#SBATCH --partition=general
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=output/slurm/%x-%j.log
# Runs after the 2026-10-22 CV workers end: final rankings and the 4-week recipe-mixture check.
export PYTHONPATH="$PWD/src:$PWD/scripts" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
out=experiments/metrocast-cv-20261021/final-summary-20261022.txt
{ date -u; echo '## 4-week track'; TRACK=short .venv/bin/python scripts/metrocast_cv_score.py --device cpu --max-runs 400
  TRACK=short .venv/bin/python scripts/metrocast_cv_tree.py status | tail -16
  echo '## 4-week recipe mixtures'; .venv/bin/python scripts/metrocast_cv_mixture.py
  echo '## full-season track'; TRACK=long .venv/bin/python scripts/metrocast_cv_score.py --device cpu --max-runs 400
  TRACK=long .venv/bin/python scripts/metrocast_cv_tree.py status | tail -16; } > $out 2>&1
