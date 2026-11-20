
# metrocast-cvlong-r001 (run by metrocast_cv.sbatch workers)
.venv/bin/python -m chromantis.experiment.planner plan -e metrocast-cvlong-r001 --problem problems/metrocast-flu-cv-long.json --study experiments/metrocast-cv-long-20261022/cv-r001.json --device cuda
.venv/bin/python -m chromantis.experiment.planner status -e metrocast-cvlong-r001
.venv/bin/python -m chromantis.experiment.planner rank -e metrocast-cvlong-r001 --allow-incomplete --no-report
