
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
