# Run on Longleaf. Do not re-plan completed experiments or launch duplicate workers.
cd /hickory/proj/jlessler/projects/tapestry-all/ebola-20261026
export PYTHONPATH="$PWD/src"

# ebola-screen-r000; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r000 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-000-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r000 --array=0-3 scripts/jlessler.sbatch ebola-screen-r000
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r000
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r000 --allow-incomplete --no-report

# ebola-screen-r001; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r001 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-001-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r001 --array=0-3 scripts/jlessler.sbatch ebola-screen-r001
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r001
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r001 --allow-incomplete --no-report

# ebola-screen-r002; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r002 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-002-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r002 --array=0-3 scripts/jlessler.sbatch ebola-screen-r002
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r002
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r002 --allow-incomplete --no-report

# ebola-screen-r003; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r003 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-003-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r003 --array=0-3 scripts/jlessler.sbatch ebola-screen-r003
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r003
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r003 --allow-incomplete --no-report

# ebola-screen-r004; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r004 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-004-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r004 --array=0-3 scripts/jlessler.sbatch ebola-screen-r004
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r004
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r004 --allow-incomplete --no-report

# ebola-screen-r005; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r005 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-005-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r005 --array=0-3 scripts/jlessler.sbatch ebola-screen-r005
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r005
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r005 --allow-incomplete --no-report

# ebola-screen-r006; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r006 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-006-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r006 --array=0-3 scripts/jlessler.sbatch ebola-screen-r006
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r006
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r006 --allow-incomplete --no-report

# ebola-screen-r007; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r007 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-007-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r007 --array=0-3 scripts/jlessler.sbatch ebola-screen-r007
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r007
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r007 --allow-incomplete --no-report

# ebola-screen-r008; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r008 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-008-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r008 --array=0-3 scripts/jlessler.sbatch ebola-screen-r008
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r008
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r008 --allow-incomplete --no-report

# ebola-screen-r009; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r009 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-009-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r009 --array=0-3 scripts/jlessler.sbatch ebola-screen-r009
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r009
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r009 --allow-incomplete --no-report

# ebola-screen-r010; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r010 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-010-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r010 --array=0-3 scripts/jlessler.sbatch ebola-screen-r010
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r010
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r010 --allow-incomplete --no-report

# ebola-screen-r011; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r011 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-011-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r011 --array=0-3 scripts/jlessler.sbatch ebola-screen-r011
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r011
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r011 --allow-incomplete --no-report

# ebola-screen-r012; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r012 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-012-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r012 --array=0-3 scripts/jlessler.sbatch ebola-screen-r012
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r012
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r012 --allow-incomplete --no-report

# ebola-screen-r013; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r013 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-013-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r013 --array=0-3 scripts/jlessler.sbatch ebola-screen-r013
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r013
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r013 --allow-incomplete --no-report

# ebola-screen-r014; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r014 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-014-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r014 --array=0-3 scripts/jlessler.sbatch ebola-screen-r014
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r014
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r014 --allow-incomplete --no-report

# ebola-screen-r015; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r015 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-015-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r015 --array=0-3 scripts/jlessler.sbatch ebola-screen-r015
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r015
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r015 --allow-incomplete --no-report

# ebola-screen-r016; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r016 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-016-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r016 --array=0-3 scripts/jlessler.sbatch ebola-screen-r016
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r016
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r016 --allow-incomplete --no-report

# ebola-screen-r017; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r017 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-017-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r017 --array=0-3 scripts/jlessler.sbatch ebola-screen-r017
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r017
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r017 --allow-incomplete --no-report

# ebola-screen-r018; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r018 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-018-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r018 --array=0-3 scripts/jlessler.sbatch ebola-screen-r018
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r018
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r018 --allow-incomplete --no-report

# ebola-screen-r019; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r019 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-019-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r019 --array=0-3 scripts/jlessler.sbatch ebola-screen-r019
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r019
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r019 --allow-incomplete --no-report

# ebola-screen-r020; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r020 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-020-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r020 --array=0-3 scripts/jlessler.sbatch ebola-screen-r020
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r020
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r020 --allow-incomplete --no-report

# ebola-screen-r021; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r021 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-021-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r021 --array=0-3 scripts/jlessler.sbatch ebola-screen-r021
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r021
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r021 --allow-incomplete --no-report

# ebola-screen-r022; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r022 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-022-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r022 --array=0-3 scripts/jlessler.sbatch ebola-screen-r022
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r022
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r022 --allow-incomplete --no-report

# ebola-screen-r023; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r023 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-023-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r023 --array=0-3 scripts/jlessler.sbatch ebola-screen-r023
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r023
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r023 --allow-incomplete --no-report

# ebola-screen-r024; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r024 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-024-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r024 --array=0-3 scripts/jlessler.sbatch ebola-screen-r024
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r024
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r024 --allow-incomplete --no-report

# ebola-screen-r025; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r025 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-025-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r025 --array=0-3 scripts/jlessler.sbatch ebola-screen-r025
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r025
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r025 --allow-incomplete --no-report

# ebola-screen-r026; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r026 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-026-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r026 --array=0-3 scripts/jlessler.sbatch ebola-screen-r026
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r026
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r026 --allow-incomplete --no-report

# ebola-screen-r027; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r027 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-027-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r027 --array=0-3 scripts/jlessler.sbatch ebola-screen-r027
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r027
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r027 --allow-incomplete --no-report

# ebola-screen-r028; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r028 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-028-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r028 --array=0-3 scripts/jlessler.sbatch ebola-screen-r028
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r028
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r028 --allow-incomplete --no-report

# ebola-screen-r029; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-screen-r029 --problem problems/ebola-bdbv-screen.json --study experiments/ebola-20261026/round-029-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-screen-r029 --array=0-3 scripts/jlessler.sbatch ebola-screen-r029
.venv/bin/python -m chromantis.experiment.planner status -e ebola-screen-r029
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-screen-r029 --allow-incomplete --no-report

# ebola-confirm-r030; actual execution uses the already queued ebola_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-confirm-r030 --problem problems/ebola-bdbv-confirm.json --study experiments/ebola-20261026/round-030-confirm.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-confirm-r030 --array=0-3 scripts/jlessler.sbatch ebola-confirm-r030
.venv/bin/python -m chromantis.experiment.planner status -e ebola-confirm-r030
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-confirm-r030 --allow-incomplete --no-report

# ebola-rescore-multi: 150 best + 50 random search recipes + root reference, 3 seeds, five windows.
.venv/bin/python -m chromantis.experiment.planner plan -e ebola-rescore-multi --problem problems/ebola-multi-outbreak.json --study experiments/ebola-20261026/rescore-multi.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=ebola-rescore-multi --array=0-3 --nodelist=g1803jles01 scripts/jlessler.sbatch ebola-rescore-multi
LANES=8 GPUS=6 sbatch --job-name=ebola-rescore-multi --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch ebola-rescore-multi
.venv/bin/python -m chromantis.experiment.planner status -e ebola-rescore-multi
.venv/bin/python -m chromantis.experiment.planner rank -e ebola-rescore-multi --allow-incomplete --no-report
