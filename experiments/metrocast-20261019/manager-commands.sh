
# metrocast-screen-r000; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r000 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-000-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r000 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r000
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r000 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r000
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r000
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r000 --allow-incomplete --no-report

# metrocast-screen-r001; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r001 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-001-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r001 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r001
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r001 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r001
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r001
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r001 --allow-incomplete --no-report

# metrocast-screen-r002; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r002 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-002-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r002 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r002
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r002 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r002
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r002
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r002 --allow-incomplete --no-report

# metrocast-screen-r003; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r003 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-003-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r003 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r003
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r003 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r003
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r003
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r003 --allow-incomplete --no-report

# metrocast-screen-r004; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r004 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-004-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r004 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r004
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r004 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r004
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r004
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r004 --allow-incomplete --no-report

# metrocast-screen-r005; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r005 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-005-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r005 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r005
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r005 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r005
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r005
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r005 --allow-incomplete --no-report

# metrocast-screen-r006; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r006 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-006-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r006 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r006
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r006 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r006
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r006
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r006 --allow-incomplete --no-report

# metrocast-screen-r007; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r007 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-007-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r007 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r007
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r007 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r007
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r007
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r007 --allow-incomplete --no-report

# metrocast-screen-r008; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r008 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-008-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r008 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r008
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r008 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r008
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r008
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r008 --allow-incomplete --no-report

# metrocast-screen-r009; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r009 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-009-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r009 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r009
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r009 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r009
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r009
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r009 --allow-incomplete --no-report

# metrocast-screen-r010; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r010 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-010-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r010 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r010
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r010 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r010
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r010
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r010 --allow-incomplete --no-report

# metrocast-screen-r011; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r011 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-011-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r011 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r011
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r011 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r011
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r011
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r011 --allow-incomplete --no-report

# metrocast-screen-r012; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r012 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-012-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r012 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r012
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r012 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r012
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r012
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r012 --allow-incomplete --no-report

# metrocast-screen-r013; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r013 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-013-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r013 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r013
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r013 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r013
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r013
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r013 --allow-incomplete --no-report

# metrocast-screen-r014; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r014 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-014-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r014 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r014
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r014 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r014
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r014
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r014 --allow-incomplete --no-report

# metrocast-screen-r015; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r015 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-015-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r015 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r015
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r015 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r015
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r015
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r015 --allow-incomplete --no-report

# metrocast-screen-r016; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r016 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-016-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r016 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r016
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r016 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r016
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r016
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r016 --allow-incomplete --no-report

# metrocast-screen-r017; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r017 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-017-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r017 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r017
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r017 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r017
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r017
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r017 --allow-incomplete --no-report

# metrocast-screen-r018; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r018 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-018-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r018 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r018
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r018 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r018
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r018
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r018 --allow-incomplete --no-report

# metrocast-screen-r019; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r019 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-019-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r019 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r019
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r019 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r019
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r019
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r019 --allow-incomplete --no-report

# metrocast-screen-r020; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r020 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-020-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r020 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r020
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r020 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r020
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r020
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r020 --allow-incomplete --no-report

# metrocast-screen-r021; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r021 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-021-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r021 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r021
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r021 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r021
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r021
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r021 --allow-incomplete --no-report

# metrocast-screen-r022; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r022 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-022-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r022 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r022
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r022 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r022
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r022
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r022 --allow-incomplete --no-report

# metrocast-screen-r023; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r023 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-023-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r023 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r023
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r023 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r023
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r023
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r023 --allow-incomplete --no-report

# metrocast-screen-r024; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r024 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-024-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r024 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r024
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r024 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r024
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r024
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r024 --allow-incomplete --no-report

# metrocast-screen-r025; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r025 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-025-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r025 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r025
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r025 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r025
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r025
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r025 --allow-incomplete --no-report

# metrocast-screen-r026; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r026 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-026-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r026 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r026
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r026 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r026
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r026
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r026 --allow-incomplete --no-report

# metrocast-screen-r027; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r027 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-027-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r027 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r027
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r027 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r027
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r027
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r027 --allow-incomplete --no-report

# metrocast-screen-r028; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r028 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-028-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r028 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r028
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r028 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r028
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r028
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r028 --allow-incomplete --no-report

# metrocast-screen-r029; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r029 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-029-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r029 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r029
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r029 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r029
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r029
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r029 --allow-incomplete --no-report

# metrocast-screen-r030; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r030 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-030-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r030 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r030
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r030 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r030
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r030
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r030 --allow-incomplete --no-report

# metrocast-screen-r031; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r031 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-031-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r031 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r031
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r031 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r031
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r031
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r031 --allow-incomplete --no-report

# metrocast-screen-r032; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r032 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-032-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r032 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r032
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r032 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r032
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r032
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r032 --allow-incomplete --no-report

# metrocast-screen-r033; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r033 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-033-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r033 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r033
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r033 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r033
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r033
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r033 --allow-incomplete --no-report

# metrocast-screen-r034; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r034 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-034-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r034 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r034
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r034 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r034
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r034
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r034 --allow-incomplete --no-report

# metrocast-screen-r035; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r035 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-035-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r035 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r035
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r035 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r035
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r035
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r035 --allow-incomplete --no-report

# metrocast-screen-r036; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r036 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-036-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r036 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r036
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r036 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r036
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r036
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r036 --allow-incomplete --no-report

# metrocast-screen-r037; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r037 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-037-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r037 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r037
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r037 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r037
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r037
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r037 --allow-incomplete --no-report

# metrocast-screen-r038; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r038 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-038-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r038 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r038
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r038 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r038
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r038
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r038 --allow-incomplete --no-report

# metrocast-screen-r039; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r039 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-039-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r039 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r039
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r039 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r039
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r039
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r039 --allow-incomplete --no-report

# metrocast-screen-r040; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r040 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-040-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r040 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r040
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r040 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r040
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r040
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r040 --allow-incomplete --no-report

# metrocast-screen-r041; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r041 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-041-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r041 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r041
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r041 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r041
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r041
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r041 --allow-incomplete --no-report

# metrocast-screen-r042; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r042 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-042-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r042 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r042
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r042 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r042
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r042
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r042 --allow-incomplete --no-report

# metrocast-screen-r043; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r043 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-043-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r043 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r043
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r043 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r043
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r043
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r043 --allow-incomplete --no-report

# metrocast-screen-r044; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r044 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-044-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r044 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r044
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r044 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r044
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r044
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r044 --allow-incomplete --no-report

# metrocast-screen-r045; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r045 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-045-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r045 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r045
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r045 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r045
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r045
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r045 --allow-incomplete --no-report

# metrocast-screen-r046; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r046 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-046-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r046 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r046
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r046 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r046
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r046
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r046 --allow-incomplete --no-report

# metrocast-screen-r047; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r047 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-047-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r047 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r047
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r047 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r047
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r047
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r047 --allow-incomplete --no-report

# metrocast-screen-r048; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r048 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-048-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r048 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r048
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r048 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r048
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r048
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r048 --allow-incomplete --no-report

# metrocast-screen-r049; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r049 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-049-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r049 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r049
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r049 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r049
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r049
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r049 --allow-incomplete --no-report

# metrocast-screen-r050; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r050 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-050-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r050 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r050
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r050 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r050
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r050
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r050 --allow-incomplete --no-report

# metrocast-screen-r051; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r051 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-051-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r051 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r051
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r051 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r051
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r051
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r051 --allow-incomplete --no-report

# metrocast-screen-r052; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r052 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-052-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r052 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r052
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r052 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r052
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r052
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r052 --allow-incomplete --no-report

# metrocast-screen-r053; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r053 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-053-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r053 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r053
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r053 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r053
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r053
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r053 --allow-incomplete --no-report

# metrocast-county-benchmark-r054; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-county-benchmark-r054 --problem problems/metrocast-county-benchmark.json --study experiments/metrocast-20261019/round-054-county-benchmark.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-county-benchmark-r054 --array=0-3 scripts/jlessler.sbatch metrocast-county-benchmark-r054
LANES=8 GPUS=6 sbatch --job-name=metrocast-county-benchmark-r054 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-county-benchmark-r054
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-benchmark-r054
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-benchmark-r054 --allow-incomplete --no-report

# metrocast-full-season-r055; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-r055 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-055-full-season.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-r055 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-r055
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-r055 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-r055
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-r055
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-r055 --allow-incomplete --no-report

# County ensemble replay/scoring; submitted job 5857324. Training plan/launch above.
sbatch --job-name=metrocast-county-ensemble-score scripts/metrocast_county_score.sbatch metrocast-county-benchmark-r054
.venv/bin/python scripts/score_metrocast_county_benchmark.py -e metrocast-county-benchmark-r054
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-benchmark-r054
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-benchmark-r054 --no-report

# metrocast-screen-r056; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r056 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-056-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r056 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r056
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r056 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r056
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r056
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r056 --allow-incomplete --no-report

# metrocast-full-season-memory-r057; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-memory-r057 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-057-full-season-memory.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-memory-r057 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-memory-r057
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-memory-r057 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-memory-r057
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-memory-r057
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-memory-r057 --allow-incomplete --no-report

# metrocast-county-sharing-r058; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-county-sharing-r058 --problem problems/metrocast-county-benchmark.json --study experiments/metrocast-20261019/round-058-county-sharing.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-county-sharing-r058 --array=0-3 scripts/jlessler.sbatch metrocast-county-sharing-r058
LANES=8 GPUS=6 sbatch --job-name=metrocast-county-sharing-r058 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-county-sharing-r058
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-sharing-r058
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-sharing-r058 --allow-incomplete --no-report

# Submitted batch job 5857594; ensemble comparison for cross-county sharing
sbatch --job-name=metrocast-county-ensemble-score scripts/metrocast_county_score.sbatch metrocast-county-sharing-r058
.venv/bin/python scripts/score_metrocast_county_benchmark.py -e metrocast-county-sharing-r058

# metrocast-county-delay-r059; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-county-delay-r059 --problem problems/metrocast-county-benchmark.json --study experiments/metrocast-20261019/round-059-county-delay.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-county-delay-r059 --array=0-3 scripts/jlessler.sbatch metrocast-county-delay-r059
LANES=8 GPUS=6 sbatch --job-name=metrocast-county-delay-r059 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-county-delay-r059
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-delay-r059
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-delay-r059 --allow-incomplete --no-report

# Submitted batch job 5857664; delayed training input comparison
sbatch --job-name=metrocast-county-ensemble-score scripts/metrocast_county_score.sbatch metrocast-county-delay-r059
.venv/bin/python scripts/score_metrocast_county_benchmark.py -e metrocast-county-delay-r059

# Submitted batch job 5857906; long-horizon WIS and joint-path energy. Training plan above.
sbatch --job-name=metrocast-full-season-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-r055
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-full-season-r055 --paths
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-r055
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-r055 --allow-incomplete --no-report

# Submitted batch job 5857941; retry after scorer quantile-axis assertion caught NumPy indexing reorder; model fits unchanged.
sbatch --job-name=metrocast-full-season-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-r055

# metrocast-county-context-r060; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-county-context-r060 --problem problems/metrocast-county-context.json --study experiments/metrocast-20261019/round-060-county-context.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-county-context-r060 --array=0-3 scripts/jlessler.sbatch metrocast-county-context-r060
LANES=8 GPUS=6 sbatch --job-name=metrocast-county-context-r060 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-county-context-r060
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-context-r060
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-context-r060 --allow-incomplete --no-report

# Submitted batch job 5871570; state and regional context, strict archived-input ensemble comparison
sbatch --job-name=metrocast-county-ensemble-score scripts/metrocast_county_score.sbatch metrocast-county-context-r060
.venv/bin/python scripts/score_metrocast_county_benchmark.py -e metrocast-county-context-r060

# metrocast-screen-r061; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r061 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-061-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r061 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r061
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r061 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r061
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r061
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r061 --allow-incomplete --no-report

# metrocast-full-season-delay-r062; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-delay-r062 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-062-full-season-delay.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-delay-r062 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-delay-r062
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-delay-r062 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-delay-r062
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-delay-r062
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-delay-r062 --allow-incomplete --no-report

# metrocast-county-delay-refine-r063; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-county-delay-refine-r063 --problem problems/metrocast-county-benchmark.json --study experiments/metrocast-20261019/round-063-county-delay-refine.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-county-delay-refine-r063 --array=0-3 scripts/jlessler.sbatch metrocast-county-delay-refine-r063
LANES=8 GPUS=6 sbatch --job-name=metrocast-county-delay-refine-r063 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-county-delay-refine-r063
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-delay-refine-r063
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-delay-refine-r063 --allow-incomplete --no-report

# Archived county ensemble scoring and long-horizon / intact-path scoring.
sbatch --job-name=metrocast-county-delay-refine-score scripts/metrocast_county_score.sbatch metrocast-county-delay-refine-r063
# Submitted batch job 5891250
sbatch --job-name=metrocast-full-season-memory-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-memory-r057
# Submitted batch job 5891251
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-memory-r057
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-memory-r057 --allow-incomplete --no-report
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-full-season-memory-r057 --paths
.venv/bin/python scripts/score_metrocast_county_benchmark.py -e metrocast-county-delay-refine-r063

# metrocast-screen-r064; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r064 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-064-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r064 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r064
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r064 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r064
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r064
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r064 --allow-incomplete --no-report

# metrocast-california-pilot-r065; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-california-pilot-r065 --problem problems/metrocast-california-pilot.json --study experiments/metrocast-20261019/round-065-california-pilot.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-california-pilot-r065 --array=0-3 scripts/jlessler.sbatch metrocast-california-pilot-r065
LANES=8 GPUS=6 sbatch --job-name=metrocast-california-pilot-r065 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-california-pilot-r065
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-california-pilot-r065
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-california-pilot-r065 --allow-incomplete --no-report

# All24 memory-replacement fits complete; finish four-seed long-horizon scores.
sbatch --job-name=metrocast-full-season-memory-complete-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-memory-r057
# Submitted batch job 5892037
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-memory-r057
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-memory-r057 --no-report

sbatch --job-name=metrocast-california-pilot-score scripts/metrocast_california_score.sbatch metrocast-california-pilot-r065
# Submitted batch job 5892144
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-california-pilot-r065
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-california-pilot-r065 --no-report
.venv/bin/python scripts/score_metrocast_california.py -e metrocast-california-pilot-r065

# metrocast-panel-context-r066; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-panel-context-r066 --problem problems/metrocast-panel-context.json --study experiments/metrocast-20261019/round-066-panel-context.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-panel-context-r066 --array=0-3 scripts/jlessler.sbatch metrocast-panel-context-r066
LANES=8 GPUS=6 sbatch --job-name=metrocast-panel-context-r066 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-panel-context-r066
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-panel-context-r066
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-panel-context-r066 --allow-incomplete --no-report

sbatch --job-name=metrocast-full-season-delay-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-delay-r062 --wait
# Submitted batch job 5892948
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-delay-r062
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-delay-r062 --no-report
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-full-season-delay-r062 --paths

# metrocast-screen-r067; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r067 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-067-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r067 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r067
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r067 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r067
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r067
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r067 --allow-incomplete --no-report

# metrocast-full-season-sharing-r068; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-sharing-r068 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-068-full-season-sharing.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-sharing-r068 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-sharing-r068
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-sharing-r068 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-sharing-r068
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-sharing-r068
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-sharing-r068 --allow-incomplete --no-report

sbatch --job-name=metrocast-full-season-sharing-r068-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-sharing-r068 --wait
# Submitted batch job 5893586
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-full-season-sharing-r068 --paths

# Equal-weight intact-draw seed mixtures; existing trained models, no refit.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-county-delay-r059 --problem problems/metrocast-county-benchmark.json --study experiments/metrocast-20261019/round-059-county-delay.json --device cuda
sbatch --job-name=metrocast-county-delay-r059-mixture-score scripts/metrocast_county_score.sbatch metrocast-county-delay-r059 --mixtures
# Submitted batch job 5894489
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-delay-r059
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-delay-r059 --no-report

# Equal-weight intact-draw seed mixtures; existing trained models, no refit.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-county-delay-refine-r063 --problem problems/metrocast-county-benchmark.json --study experiments/metrocast-20261019/round-063-county-delay-refine.json --device cuda
sbatch --job-name=metrocast-county-delay-refine-r063-mixture-score scripts/metrocast_county_score.sbatch metrocast-county-delay-refine-r063 --mixtures
# Submitted batch job 5894490
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-county-delay-refine-r063
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-county-delay-refine-r063 --no-report

# Equal-weight intact-draw seed mixtures; existing trained models, no refit.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-memory-r057 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-057-full-season-memory.json --device cuda
sbatch --job-name=metrocast-full-season-memory-r057-mixture-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-memory-r057
# Submitted batch job 5894492
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-memory-r057
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-memory-r057 --no-report

# Equal-weight intact-draw seed mixtures; existing trained models, no refit.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-delay-r062 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-062-full-season-delay.json --device cuda
sbatch --job-name=metrocast-full-season-delay-r062-mixture-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-delay-r062
# Submitted batch job 5894493
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-delay-r062
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-delay-r062 --no-report

# metrocast-screen-r069; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r069 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-069-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r069 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r069
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r069 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r069
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r069
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r069 --allow-incomplete --no-report

# metrocast-full-season-direct-refine-r070; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-direct-refine-r070 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-070-full-season-direct-refine.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-direct-refine-r070 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-direct-refine-r070
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-direct-refine-r070 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-direct-refine-r070
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-direct-refine-r070
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-direct-refine-r070 --allow-incomplete --no-report

sbatch --job-name=metrocast-full-season-direct-refine-r070-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-direct-refine-r070 --wait
# Submitted batch job 5895667
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-full-season-direct-refine-r070 --paths

# metrocast-screen-r071; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r071 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-071-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r071 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r071
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r071 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r071
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r071
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r071 --allow-incomplete --no-report

# Current-input export diagnostic using existing development checkpoints; no model refit or outcome scoring.
# Plan: reuse the completed r057 and r065 plans recorded above; do not replan or change their snapshots.
# Launch:
sbatch --partition=general --nodes=1 --ntasks=1 --cpus-per-task=2 --mem=12G --time=00:20:00 --job-name=metrocast-export-check --output=output/slurm/%x-%j.log --wrap='export PYTHONPATH="$PWD/src"; export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1; .venv/bin/python scripts/check_metrocast_export.py'
# Status/rank of the reused fits (diagnostic has no future truth to rank):
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-memory-r057
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-memory-r057 --no-report
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-california-pilot-r065
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-california-pilot-r065 --no-report
cat output/metrocast/export-diagnostic/checks.json

# Retry export diagnostic after fixing tuple location lookup in own-state archive replay.
sbatch --partition=general --nodes=1 --ntasks=1 --cpus-per-task=2 --mem=12G --time=00:20:00 --job-name=metrocast-export-check --output=output/slurm/%x-%j.log --wrap='export PYTHONPATH="$PWD/src"; export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1; .venv/bin/python scripts/check_metrocast_export.py'
# Submitted batch job 5896452

# Diagnostic now reads each development checkpoint fold from its manifest (CA winter pilot differs from ED season).
sbatch --partition=general --nodes=1 --ntasks=1 --cpus-per-task=2 --mem=12G --time=00:20:00 --job-name=metrocast-export-check --output=output/slurm/%x-%j.log --wrap='export PYTHONPATH="$PWD/src"; export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1; .venv/bin/python scripts/check_metrocast_export.py'
# Submitted batch job 5896466

# metrocast-screen-r072; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r072 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-072-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r072 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r072
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r072 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r072
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r072
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r072 --allow-incomplete --no-report

# metrocast-full-season-direct-refine-r073; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-direct-refine-r073 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-073-full-season-direct-refine.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-direct-refine-r073 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-direct-refine-r073
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-direct-refine-r073 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-direct-refine-r073
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-direct-refine-r073
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-direct-refine-r073 --allow-incomplete --no-report

sbatch --job-name=metrocast-full-season-direct-refine-r073-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-direct-refine-r073 --wait
# Submitted batch job 5897008
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-full-season-direct-refine-r073 --paths

# Peak size/timing diagnostic from cached intact draws; no retraining, frozen selection unchanged.
# Existing plan below is a reference; do not replan completed fits.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-memory-r057 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-057-full-season-memory.json --device cuda
sbatch --job-name=metrocast-full-season-memory-r057-peaks scripts/metrocast_full_season_score.sbatch metrocast-full-season-memory-r057
# Submitted batch job 5897467
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-memory-r057
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-memory-r057 --no-report

# Peak size/timing diagnostic from cached intact draws; no retraining, frozen selection unchanged.
# Existing plan below is a reference; do not replan completed fits.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-direct-refine-r070 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-070-full-season-direct-refine.json --device cuda
sbatch --job-name=metrocast-full-season-direct-refine-r070-peaks scripts/metrocast_full_season_score.sbatch metrocast-full-season-direct-refine-r070
# Submitted batch job 5897468
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-direct-refine-r070
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-direct-refine-r070 --no-report

# metrocast-utah-proposed-fullseason-r074; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-utah-proposed-fullseason-r074 --problem problems/metrocast-utah-proposed-fullseason.json --study experiments/metrocast-20261019/round-074-utah-proposed-fullseason.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-utah-proposed-fullseason-r074 --array=0-3 scripts/jlessler.sbatch metrocast-utah-proposed-fullseason-r074
LANES=8 GPUS=6 sbatch --job-name=metrocast-utah-proposed-fullseason-r074 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-utah-proposed-fullseason-r074
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-utah-proposed-fullseason-r074
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-utah-proposed-fullseason-r074 --allow-incomplete --no-report

sbatch --job-name=metrocast-utah-proposed-fullseason-r074-score scripts/metrocast_full_season_score.sbatch metrocast-utah-proposed-fullseason-r074 --wait
# Submitted batch job 5897598
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-utah-proposed-fullseason-r074 --paths

# metrocast-screen-r075; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r075 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-075-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r075 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r075
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r075 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r075
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r075
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r075 --allow-incomplete --no-report

# Utah current-input diagnostic: reuse r074 development plan, no refit or future-outcome scoring.
# Existing plan (do not replan): .venv/bin/python -m chromantis.experiment.planner plan -e metrocast-utah-proposed-fullseason-r074 --problem problems/metrocast-utah-proposed-fullseason.json --study experiments/metrocast-20261019/round-074-utah-proposed-fullseason.json --device cuda
sbatch --partition=general --nodes=1 --ntasks=1 --cpus-per-task=2 --mem=12G --time=00:20:00 --job-name=metrocast-utah-export-check --output=output/slurm/%x-%j.log '--wrap=export PYTHONPATH="$PWD/src"; export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1; .venv/bin/python scripts/check_metrocast_export.py --kind utah'
# Submitted batch job 5898987
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-utah-proposed-fullseason-r074
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-utah-proposed-fullseason-r074 --allow-incomplete --no-report
cat output/metrocast/export-diagnostic/utah-checks.json

# metrocast-utah-proposed-fullseason-r076; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-utah-proposed-fullseason-r076 --problem problems/metrocast-utah-proposed-fullseason.json --study experiments/metrocast-20261019/round-076-utah-proposed-fullseason.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-utah-proposed-fullseason-r076 --array=0-3 scripts/jlessler.sbatch metrocast-utah-proposed-fullseason-r076
LANES=8 GPUS=6 sbatch --job-name=metrocast-utah-proposed-fullseason-r076 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-utah-proposed-fullseason-r076
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-utah-proposed-fullseason-r076
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-utah-proposed-fullseason-r076 --allow-incomplete --no-report

sbatch --job-name=metrocast-utah-proposed-fullseason-r076-score scripts/metrocast_full_season_score.sbatch metrocast-utah-proposed-fullseason-r076 --wait
# Submitted batch job 5899048

# metrocast-full-season-sharing-r077; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-sharing-r077 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-077-full-season-sharing.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-sharing-r077 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-sharing-r077
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-sharing-r077 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-sharing-r077
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-sharing-r077
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-sharing-r077 --allow-incomplete --no-report

sbatch --job-name=metrocast-full-season-sharing-r077-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-sharing-r077 --wait
# Submitted batch job 5900499

# California uniform seed mixture: reuse completed fits and cached intact paths; no retraining.
# Existing plan (do not replan): .venv/bin/python -m chromantis.experiment.planner plan -e metrocast-california-pilot-r065 --problem problems/metrocast-california-pilot.json --study experiments/metrocast-20261019/round-065-california-pilot.json --device cuda
sbatch --job-name=metrocast-california-mixture-score scripts/metrocast_california_score.sbatch metrocast-california-pilot-r065
# Submitted batch job 5900915
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-california-pilot-r065
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-california-pilot-r065 --no-report

# metrocast-screen-r078; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r078 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-078-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r078 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r078
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r078 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r078
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r078
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r078 --allow-incomplete --no-report

# metrocast-screen-r079; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r079 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-079-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r079 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r079
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r079 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r079
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r079
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r079 --allow-incomplete --no-report

# metrocast-california-pilot-r080; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-california-pilot-r080 --problem problems/metrocast-california-pilot.json --study experiments/metrocast-20261019/round-080-california-pilot.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-california-pilot-r080 --array=0-3 scripts/jlessler.sbatch metrocast-california-pilot-r080
LANES=8 GPUS=6 sbatch --job-name=metrocast-california-pilot-r080 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-california-pilot-r080
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-california-pilot-r080
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-california-pilot-r080 --allow-incomplete --no-report

sbatch --job-name=metrocast-california-pilot-r080-score scripts/metrocast_california_score.sbatch metrocast-california-pilot-r080
# Submitted batch job 5902644

# metrocast-screen-r081; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r081 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-081-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r081 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r081
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r081 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r081
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r081
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r081 --allow-incomplete --no-report

# metrocast-full-season-direct-refine-r082; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-direct-refine-r082 --problem problems/metrocast-flu-full-season.json --study experiments/metrocast-20261019/round-082-full-season-direct-refine.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-direct-refine-r082 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-direct-refine-r082
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-direct-refine-r082 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-direct-refine-r082
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-direct-refine-r082
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-direct-refine-r082 --allow-incomplete --no-report

sbatch --job-name=metrocast-full-season-direct-refine-r082-score scripts/metrocast_full_season_score.sbatch metrocast-full-season-direct-refine-r082 --wait
# Submitted batch job 5903558

# metrocast-screen-r083; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r083 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-083-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r083 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r083
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r083 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r083
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r083
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r083 --allow-incomplete --no-report

# metrocast-screen-r084; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r084 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-084-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r084 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r084
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r084 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r084
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r084
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r084 --allow-incomplete --no-report

# metrocast-screen-r085; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r085 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-085-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r085 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r085
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r085 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r085
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r085
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r085 --allow-incomplete --no-report

# metrocast-screen-r086; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r086 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-086-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r086 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r086
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r086 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r086
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r086
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r086 --allow-incomplete --no-report

# metrocast-screen-r087; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r087 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-087-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r087 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r087
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r087 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r087
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r087
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r087 --allow-incomplete --no-report

# metrocast-screen-r088; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r088 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-088-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r088 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r088
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r088 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r088
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r088
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r088 --allow-incomplete --no-report

# metrocast-screen-r089; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r089 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-089-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r089 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r089
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r089 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r089
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r089
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r089 --allow-incomplete --no-report

# metrocast-screen-r090; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r090 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-090-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r090 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r090
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r090 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r090
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r090
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r090 --allow-incomplete --no-report

# metrocast-screen-r091; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r091 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-091-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r091 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r091
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r091 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r091
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r091
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r091 --allow-incomplete --no-report

# metrocast-screen-r092; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r092 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-092-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r092 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r092
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r092 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r092
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r092
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r092 --allow-incomplete --no-report

# metrocast-screen-r093; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r093 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-093-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r093 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r093
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r093 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r093
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r093
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r093 --allow-incomplete --no-report

# metrocast-screen-r094; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r094 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-094-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r094 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r094
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r094 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r094
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r094
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r094 --allow-incomplete --no-report

# metrocast-screen-r095; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r095 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-095-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r095 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r095
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r095 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r095
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r095
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r095 --allow-incomplete --no-report

# metrocast-screen-r096; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r096 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-096-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r096 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r096
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r096 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r096
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r096
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r096 --allow-incomplete --no-report

# metrocast-screen-r097; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r097 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-097-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r097 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r097
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r097 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r097
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r097
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r097 --allow-incomplete --no-report

# metrocast-screen-r098; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r098 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-098-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r098 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r098
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r098 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r098
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r098
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r098 --allow-incomplete --no-report

# metrocast-screen-r099; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r099 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-099-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r099 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r099
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r099 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r099
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r099
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r099 --allow-incomplete --no-report

# metrocast-screen-r100; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r100 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-100-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r100 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r100
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r100 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r100
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r100
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r100 --allow-incomplete --no-report

# metrocast-screen-r101; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r101 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-101-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r101 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r101
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r101 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r101
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r101
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r101 --allow-incomplete --no-report

# metrocast-screen-r102; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r102 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-102-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r102 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r102
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r102 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r102
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r102
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r102 --allow-incomplete --no-report

# metrocast-screen-r103; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r103 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-103-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r103 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r103
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r103 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r103
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r103
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r103 --allow-incomplete --no-report

# metrocast-screen-r104; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r104 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-104-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r104 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r104
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r104 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r104
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r104
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r104 --allow-incomplete --no-report

# metrocast-screen-r105; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r105 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-105-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r105 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r105
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r105 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r105
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r105
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r105 --allow-incomplete --no-report

# metrocast-screen-r106; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r106 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-106-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r106 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r106
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r106 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r106
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r106
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r106 --allow-incomplete --no-report

# metrocast-screen-r107; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r107 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-107-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r107 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r107
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r107 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r107
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r107
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r107 --allow-incomplete --no-report

# metrocast-screen-r108; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r108 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-108-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r108 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r108
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r108 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r108
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r108
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r108 --allow-incomplete --no-report

# metrocast-screen-r109; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r109 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-109-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r109 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r109
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r109 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r109
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r109
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r109 --allow-incomplete --no-report

# metrocast-screen-r110; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r110 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-110-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r110 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r110
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r110 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r110
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r110
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r110 --allow-incomplete --no-report

# metrocast-screen-r111; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r111 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-111-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r111 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r111
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r111 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r111
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r111
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r111 --allow-incomplete --no-report

# metrocast-screen-r112; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r112 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-112-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r112 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r112
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r112 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r112
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r112
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r112 --allow-incomplete --no-report

# metrocast-screen-r113; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r113 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-113-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r113 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r113
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r113 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r113
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r113
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r113 --allow-incomplete --no-report

# metrocast-screen-r114; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r114 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-114-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r114 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r114
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r114 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r114
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r114
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r114 --allow-incomplete --no-report

# metrocast-screen-r115; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r115 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-115-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r115 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r115
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r115 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r115
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r115
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r115 --allow-incomplete --no-report

# metrocast-screen-r116; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r116 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-116-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r116 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r116
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r116 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r116
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r116
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r116 --allow-incomplete --no-report

# metrocast-screen-r117; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r117 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-117-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r117 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r117
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r117 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r117
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r117
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r117 --allow-incomplete --no-report

# metrocast-screen-r118; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r118 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-118-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r118 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r118
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r118 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r118
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r118
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r118 --allow-incomplete --no-report

# metrocast-screen-r119; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r119 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-119-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r119 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r119
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r119 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r119
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r119
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r119 --allow-incomplete --no-report

# metrocast-screen-r120; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r120 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-120-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r120 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r120
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r120 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r120
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r120
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r120 --allow-incomplete --no-report

# metrocast-screen-r121; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r121 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-121-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r121 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r121
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r121 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r121
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r121
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r121 --allow-incomplete --no-report

# metrocast-confirm-r122; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-confirm-r122 --problem problems/metrocast-flu-confirm.json --study experiments/metrocast-20261019/round-122-confirm.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-confirm-r122 --array=0-3 scripts/jlessler.sbatch metrocast-confirm-r122
LANES=8 GPUS=6 sbatch --job-name=metrocast-confirm-r122 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-confirm-r122
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-confirm-r122
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-confirm-r122 --allow-incomplete --no-report

sbatch --job-name=metrocast-confirm-r122-score scripts/metrocast_confirmation_score.sbatch metrocast-confirm-r122
# Submitted batch job 6005040
.venv/bin/python scripts/score_metrocast_confirmation.py -e metrocast-confirm-r122

# metrocast-full-season-confirm-r123; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-full-season-confirm-r123 --problem problems/metrocast-flu-full-season-confirm.json --study experiments/metrocast-20261019/round-123-full-season-confirm.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-full-season-confirm-r123 --array=0-3 scripts/jlessler.sbatch metrocast-full-season-confirm-r123
LANES=8 GPUS=6 sbatch --job-name=metrocast-full-season-confirm-r123 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-full-season-confirm-r123
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-full-season-confirm-r123
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-full-season-confirm-r123 --allow-incomplete --no-report

sbatch --job-name=metrocast-full-season-confirm-r123-score scripts/metrocast_confirmation_score.sbatch metrocast-full-season-confirm-r123
# Submitted batch job 6005229
.venv/bin/python scripts/score_metrocast_confirmation.py -e metrocast-full-season-confirm-r123
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-full-season-confirm-r123 --paths --confirmation

# metrocast-confirm-delay-r124; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-confirm-delay-r124 --problem problems/metrocast-flu-confirm.json --study experiments/metrocast-20261019/round-124-confirm-delay.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-confirm-delay-r124 --array=0-3 scripts/jlessler.sbatch metrocast-confirm-delay-r124
LANES=8 GPUS=6 sbatch --job-name=metrocast-confirm-delay-r124 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-confirm-delay-r124
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-confirm-delay-r124
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-confirm-delay-r124 --allow-incomplete --no-report

sbatch --job-name=metrocast-confirm-delay-r124-score scripts/metrocast_confirmation_score.sbatch metrocast-confirm-delay-r124
# Submitted batch job 6005344
.venv/bin/python scripts/score_metrocast_confirmation.py -e metrocast-confirm-delay-r124

# metrocast-context-confirm-r125; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-context-confirm-r125 --problem problems/metrocast-panel-context-confirm.json --study experiments/metrocast-20261019/round-125-context-confirm.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-context-confirm-r125 --array=0-3 scripts/jlessler.sbatch metrocast-context-confirm-r125
LANES=8 GPUS=6 sbatch --job-name=metrocast-context-confirm-r125 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-context-confirm-r125
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-context-confirm-r125
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-context-confirm-r125 --allow-incomplete --no-report

sbatch --job-name=metrocast-context-confirm-r125-score scripts/metrocast_confirmation_score.sbatch metrocast-context-confirm-r125
# Submitted batch job 6005468
.venv/bin/python scripts/score_metrocast_confirmation.py -e metrocast-context-confirm-r125

# metrocast-california-confirm-r126; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-california-confirm-r126 --problem problems/metrocast-california-confirm.json --study experiments/metrocast-20261019/round-126-california-confirm.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-california-confirm-r126 --array=0-3 scripts/jlessler.sbatch metrocast-california-confirm-r126
LANES=8 GPUS=6 sbatch --job-name=metrocast-california-confirm-r126 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-california-confirm-r126
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-california-confirm-r126
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-california-confirm-r126 --allow-incomplete --no-report

sbatch --job-name=metrocast-california-confirm-r126-score scripts/metrocast_confirmation_score.sbatch metrocast-california-confirm-r126
# Submitted batch job 6005484
.venv/bin/python scripts/score_metrocast_california.py -e metrocast-california-confirm-r126 --confirmation

# metrocast-utah-confirm-r127; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-utah-confirm-r127 --problem problems/metrocast-utah-confirm.json --study experiments/metrocast-20261019/round-127-utah-confirm.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-utah-confirm-r127 --array=0-3 scripts/jlessler.sbatch metrocast-utah-confirm-r127
LANES=8 GPUS=6 sbatch --job-name=metrocast-utah-confirm-r127 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-utah-confirm-r127
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-utah-confirm-r127
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-utah-confirm-r127 --allow-incomplete --no-report

sbatch --job-name=metrocast-utah-confirm-r127-score scripts/metrocast_confirmation_score.sbatch metrocast-utah-confirm-r127
# Submitted batch job 6005659
.venv/bin/python scripts/score_metrocast_full_season.py -e metrocast-utah-confirm-r127 --paths --confirmation

# metrocast-current-fourweek-r128; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-current-fourweek-r128 --problem problems/metrocast-current-fourweek.json --study experiments/metrocast-20261019/round-128-current-fourweek.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-current-fourweek-r128 --array=0-3 scripts/jlessler.sbatch metrocast-current-fourweek-r128
LANES=8 GPUS=6 sbatch --job-name=metrocast-current-fourweek-r128 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-current-fourweek-r128
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-current-fourweek-r128
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-current-fourweek-r128 --allow-incomplete --no-report

sbatch --job-name=metrocast-current-fourweek-r128-export scripts/metrocast_current_export.sbatch metrocast-current-fourweek-r128
# Submitted batch job 6006262
.venv/bin/python scripts/export_metrocast_current.py -e metrocast-current-fourweek-r128

# metrocast-current-fullseason-r129; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-current-fullseason-r129 --problem problems/metrocast-current-fullseason.json --study experiments/metrocast-20261019/round-129-current-fullseason.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-current-fullseason-r129 --array=0-3 scripts/jlessler.sbatch metrocast-current-fullseason-r129
LANES=8 GPUS=6 sbatch --job-name=metrocast-current-fullseason-r129 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-current-fullseason-r129
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-current-fullseason-r129
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-current-fullseason-r129 --allow-incomplete --no-report

sbatch --job-name=metrocast-current-fullseason-r129-export scripts/metrocast_current_export.sbatch metrocast-current-fullseason-r129
# Submitted batch job 6006967
.venv/bin/python scripts/export_metrocast_current.py -e metrocast-current-fullseason-r129

# metrocast-current-california-r130; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-current-california-r130 --problem problems/metrocast-current-california.json --study experiments/metrocast-20261019/round-130-current-california.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-current-california-r130 --array=0-3 scripts/jlessler.sbatch metrocast-current-california-r130
LANES=8 GPUS=6 sbatch --job-name=metrocast-current-california-r130 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-current-california-r130
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-current-california-r130
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-current-california-r130 --allow-incomplete --no-report

sbatch --job-name=metrocast-current-california-r130-export scripts/metrocast_current_export.sbatch metrocast-current-california-r130
# Submitted batch job 6009101
.venv/bin/python scripts/export_metrocast_current.py -e metrocast-current-california-r130

# metrocast-current-utah-r131; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-current-utah-r131 --problem problems/metrocast-current-utah.json --study experiments/metrocast-20261019/round-131-current-utah.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-current-utah-r131 --array=0-3 scripts/jlessler.sbatch metrocast-current-utah-r131
LANES=8 GPUS=6 sbatch --job-name=metrocast-current-utah-r131 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-current-utah-r131
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-current-utah-r131
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-current-utah-r131 --allow-incomplete --no-report

sbatch --job-name=metrocast-current-utah-r131-export scripts/metrocast_current_export.sbatch metrocast-current-utah-r131
# Submitted batch job 6009433
.venv/bin/python scripts/export_metrocast_current.py -e metrocast-current-utah-r131

# metrocast-screen-r132; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r132 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-132-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r132 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r132
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r132 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r132
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r132
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r132 --allow-incomplete --no-report

# metrocast-screen-r133; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r133 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-133-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r133 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r133
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r133 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r133
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r133
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r133 --allow-incomplete --no-report

# metrocast-screen-r134; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r134 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-134-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r134 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r134
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r134 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r134
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r134
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r134 --allow-incomplete --no-report

# metrocast-screen-r135; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r135 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-135-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r135 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r135
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r135 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r135
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r135
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r135 --allow-incomplete --no-report

# metrocast-screen-r136; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r136 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-136-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r136 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r136
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r136 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r136
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r136
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r136 --allow-incomplete --no-report

# metrocast-screen-r137; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r137 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-137-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r137 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r137
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r137 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r137
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r137
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r137 --allow-incomplete --no-report

# metrocast-screen-r138; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r138 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-138-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r138 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r138
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r138 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r138
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r138
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r138 --allow-incomplete --no-report

# metrocast-screen-r139; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r139 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-139-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r139 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r139
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r139 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r139
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r139
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r139 --allow-incomplete --no-report

# metrocast-screen-r140; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r140 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-140-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r140 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r140
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r140 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r140
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r140
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r140 --allow-incomplete --no-report

# metrocast-screen-r141; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r141 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-141-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r141 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r141
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r141 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r141
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r141
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r141 --allow-incomplete --no-report

# metrocast-screen-r142; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r142 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-142-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r142 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r142
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r142 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r142
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r142
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r142 --allow-incomplete --no-report

# metrocast-screen-r143; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r143 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-143-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r143 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r143
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r143 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r143
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r143
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r143 --allow-incomplete --no-report

# metrocast-screen-r144; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r144 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-144-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r144 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r144
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r144 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r144
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r144
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r144 --allow-incomplete --no-report

# metrocast-screen-r145; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r145 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-145-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r145 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r145
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r145 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r145
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r145
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r145 --allow-incomplete --no-report

# metrocast-screen-r146; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r146 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-146-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r146 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r146
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r146 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r146
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r146
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r146 --allow-incomplete --no-report

# metrocast-screen-r147; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r147 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-147-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r147 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r147
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r147 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r147
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r147
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r147 --allow-incomplete --no-report

# metrocast-screen-r148; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r148 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-148-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r148 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r148
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r148 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r148
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r148
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r148 --allow-incomplete --no-report

# metrocast-screen-r149; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r149 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-149-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r149 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r149
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r149 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r149
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r149
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r149 --allow-incomplete --no-report

# metrocast-screen-r150; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r150 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-150-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r150 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r150
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r150 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r150
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r150
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r150 --allow-incomplete --no-report

# metrocast-screen-r151; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r151 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-151-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r151 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r151
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r151 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r151
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r151
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r151 --allow-incomplete --no-report

# metrocast-screen-r152; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r152 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-152-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r152 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r152
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r152 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r152
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r152
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r152 --allow-incomplete --no-report

# metrocast-screen-r153; actual execution uses the already queued metrocast_tree.sbatch workers.
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-screen-r153 --problem problems/metrocast-flu-screen.json --study experiments/metrocast-20261019/round-153-screen.json --device cuda
LANES=4 GPUS=6 sbatch --job-name=metrocast-screen-r153 --array=0-3 scripts/jlessler.sbatch metrocast-screen-r153
LANES=8 GPUS=6 sbatch --job-name=metrocast-screen-r153 --array=0-1 --nodelist=g1803jles02 scripts/jlessler.sbatch metrocast-screen-r153
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-screen-r153
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-screen-r153 --allow-incomplete --no-report
