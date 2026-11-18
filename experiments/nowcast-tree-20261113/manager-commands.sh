# Ledger of the commands run for nowcast-tree-20261113. Longleaf campaign folder:
#   /hickory/proj/jlessler/projects/tapestry-all/nowcast-20261113  (own .venv copied from covid-20261030;
#   data/evaluation/b0_hub_comparison_q23 links to the main checkout). Code and panel are rsynced from the Mac.
# 2026-11-13: research panel with hospital counts (built on the Mac, rsynced)
.venv/bin/python -m chromantis.dataset.build build --data-root data/operational-20261111 --spec datasets/respiratory-us-weekly-coverage.json \
    --truth-day 2026-11-12 --workers 4 --output data/processed/panel-coverage.npz   # SHA256 912d8c30...
# 2026-11-13: round 1 and its forward check, chained on one array over the six lab GPUs (job 9136360)
export PYTHONPATH=src
.venv/bin/python -m chromantis.experiment.planner plan -e nowcast-tree-20261113-r01 --problem problems/us-flu-short-term-coverage.json \
    --study experiments/nowcast-tree-20261113/round-01.json --device cuda
.venv/bin/python -m chromantis.experiment.planner plan -e nowcast-tree-20261113-fwd01 --problem problems/us-flu-forward-2025-26-coverage.json \
    --study experiments/nowcast-tree-20261113/round-01.json --device cuda
sbatch --job-name=nowcast-tree-r01 --array=0-5 scripts/covid_tree.sbatch nowcast-tree-20261113-r01 nowcast-tree-20261113-fwd01
.venv/bin/python -m chromantis.experiment.planner status -e nowcast-tree-20261113-r01
.venv/bin/python -m chromantis.experiment.planner rank -e nowcast-tree-20261113-r01 --allow-incomplete --no-report
