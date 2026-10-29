# Chromantis

Chromantis is a Python research package for epidemic forecasting. It uses
incomplete and revisable surveillance histories to predict hospital admissions
and the share of emergency-department visits attributed to influenza, COVID-19
or RSV. Applications include current-week nowcasts, four-week forecasts,
influenza season peaks and local ED forecasts.

- [Documentation](https://accidda.github.io/chromantis/)
- [Architecture](docs/architecture.md): model, figures, training and evaluation
- [Workflow](docs/workflow.md): acquire, build, plan, launch and rank
- [Model runs](docs/experiments/index.md): dated forecasting reports; nowcasting section
- [Data](docs/data/index.md) and [interactive staircase](https://accidda.github.io/chromantis/data/staircase/)
- [Setup](docs/setup.md)

```bash
uv sync
.venv/bin/python -m chromantis.dataset.build show
.venv/bin/python -m chromantis.experiment.planner status -e b-2-t0
```

`planner rank` summarizes saved experiment results. Reports live in
`docs/experiments/`; model artifacts live in `data/experiments/`. Weekly state
releases use saved correction trees to adjust recent observed reports, then
neural models predict the current week and subsequent weeks. Supplying new
reports to a saved release does not retrain it. See the workflow for planning,
launching, checking and resuming research runs.
