# Development

Most research changes belong in a study definition or an existing package
module. A candidate configuration goes in a study file. A new analysis belongs
in `chromantis.evaluation`, where the planner and saved-forecast ensembles can
use it. The research and production paths share their combination code.

## Repository layout

| Directory | Contents |
|---|---|
| `src/chromantis/data` | Source acquisition, snapshots, readers and shared selection |
| `src/chromantis/dataset` | Panels, examples, folds, reporting errors and ILI archive |
| `src/chromantis/model` | Networks, scenarios, objectives and correction trees |
| `src/chromantis/experiment` | Fit procedure, training loop, planner and GPU dispatch |
| `src/chromantis/evaluation` | Scoring, rankings, forecast mixtures and reports |
| `src/chromantis/production` | Release inference, Hub export and submission plots |
| `src/chromantis/explorer` | Source index, API and browser interface |
| `experiments` | Study definitions and ensemble groups |
| `production` | Releases, submissions, metadata and ignored Hub clones |
| `scripts` | Cluster launch, notifications, explorer publishing and docs tools |
| `docs/experiments` | Experiment reports and their evidence |

Replace obsolete code when introducing its successor. The
[8 October restructuring record](workflow.md#restructuring-log-8-october-2026)
explains the consolidation into the shared training, scoring and release paths.

## Research iteration

Use research runs and inspection for routine validation. Focus tests on errors
that could silently change a scientific conclusion: loss and score mathematics,
weights, leakage, and units or alignment. Run the relevant checks when those
calculations change. Plotting and routine execution do not need a general
regression suite.

Use `planner rank` or `evaluation.ensembles` for experiment analysis and the
saved ranking tables for written results. Keep interpretations inside report
write-up markers. Dataset diagnostics use `chromantis.dataset.analyze_dataset`.

## Documentation

Preview the site or check a build with:

```bash
uv run --no-dev --extra docs mkdocs serve
uv run --no-dev --extra docs mkdocs build --strict
```

The build uses saved documentation assets and needs no training data. Each
experiment's `report.json` supplies an ISO date, title and `stage` (`nowcast` or
`forecast`). Add one line per phase to the hand-curated
`docs/experiments/index.md`. The `scripts/docs_hooks.py` hook orders sidebar
reports by their stated dates.

The docs embed the availability staircase. The source explorer is published
at `/explorer/` from saved exports under `docs/explorer/data/` and the interface
under `src/chromantis/explorer/static/`. Run
`scripts/update_published_explorer.sh` to refresh that export; a docs build uses
what is already committed.

## Publishing

The Documentation GitHub Action runs a strict build on pull requests and `main`.
Builds on `main` publish through GitHub Pages, whose publishing source is GitHub
Actions. The publication process uses the saved site contents without training
models or downloading surveillance sources.
