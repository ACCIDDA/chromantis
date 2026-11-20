# Research workflow

A Chromantis study compares candidate models under one forecasting problem.
The problem fixes the outcomes, horizons, training and evaluation splits, and
score. Candidates vary the model or its training procedure. The experiment
manager records the data and code, dispatches fits and gathers their results.

Run the commands below from the repository root after completing [setup](setup.md).
The [architecture guide](architecture.md) explains the methods; the
[scenario reference](reference/scenario.md) lists configuration fields.

## Before starting an experiment

Choose the outcome and units, training seasons, prediction labels, treatment
of training histories, evaluation inputs and season, and primary score. These
choices determine what the comparison can tell you. Save the problem and
candidate definitions before fitting, and use a new experiment name when the
data or scientific protocol changes.

A fit learns weights. A replay supplies different evaluation inputs to saved
weights. Production supplies new operational reports to a released set of fits.
Combining saved predictive distributions also keeps the original weights.
The [fitting diagram](architecture.md#fitting-and-model-selection)
shows the steps from candidate search to release fitting.

| Work | Package entry point |
|---|---|
| Acquire sources and build a dated panel | `chromantis.data`, `chromantis.dataset.build` |
| Specify candidates and seeds | `experiments/<name>.json` |
| Plan, launch and resume fits | `chromantis.experiment.planner`, `scripts/jlessler.sbatch` |
| Replay saved fits on different inputs | `planner replay` |
| Score, rank and report | `planner rank` |
| Combine saved forecasts | `chromantis.evaluation.ensembles` |
| Issue forecasts from a release | `chromantis.production` |

## Acquire and build

Training reads a saved panel. Refresh the sources when preparing a new dataset,
then build and check the panel before planning an experiment.

```bash
.venv/bin/python -m chromantis.data --data-root data pull delphi_nhsn delphi_nssp \
    delphi_claims_inpatient delphi_claims_outpatient delphi_nwss delphi_nwss_aux \
    hub_flusight_current hub_covid_current hub_rsv_current pophive_kinsa_ili \
    delphi_fluview_ilinet delphi_fluview_clinical delphi_flusurv
.venv/bin/python -m chromantis.dataset.build nwss-indices --data-root data
.venv/bin/python -m chromantis.dataset.build build --data-root data
.venv/bin/python -m chromantis.dataset.build show
.venv/bin/python -m chromantis.dataset.build check
.venv/bin/python -m chromantis.dataset.analyze_dataset
```

The [data guide](data/index.md) describes source selection and publication lags.
Wastewater indices have a separate build step and need rebuilding when their
input snapshots change. Use `build --truth-day` to pin the reference resolution
date. Planned runs verify file hashes, so a rebuilt panel needs a new experiment.
Panels predating the 5 October 2026 per-Hub deadline implementation are rejected
at fitting.

## Scenarios

A scenario is a comma-separated string of `key=value` fields. Omitted fields
use the `Scenario` defaults. The [model-choice reference](reference/model-choices.md)
explains the six choices used in experiment reports:

| Choice | What it controls |
|---|---|
| A: training histories | Reference, archived or artificially preliminary inputs; training correction; auxiliary recent-history labels |
| B: reporting-error source | Seasons supplying the artificial revision patterns |
| C: affected signals | Which training signals receive those errors |
| D: correction model | The examples and model used to estimate revisions |
| E: evaluation inputs | Archived reports or prescribed artificial histories, fixed by the problem |
| F: forecast view | How reports are treated when ranking or deploying the fit |

Each configuration is ranked in its own `forecast_view`, which defaults to
`corrected`. Other views provide diagnostics: `raw`, `half` and optional
`calibrated`, `sampled`, `delayed` and `nokinsa`. National Kinsa inputs are copied
to locations with their original availability; state covariates retain their
native geography.

## Plan, launch and resume

A study file lists candidate scenarios and seeds. The example below uses the
short-term flu problem and a study at `experiments/my-study.json`:

```bash
.venv/bin/python -m chromantis.experiment.planner plan -e my-study --problem problems/us-flu-short-term.json --study experiments/my-study.json --device cuda
sbatch --job-name=my-study --array=0-3 scripts/jlessler.sbatch my-study
.venv/bin/python -m chromantis.experiment.planner status -e my-study
.venv/bin/python -m chromantis.experiment.planner rank -e my-study
```

You can also pass a scenario string with `plan -s SCENARIO`. The planner saves
candidate definitions, seeds, the study, data/support hashes and a source snapshot
under `data/experiments/<name>/`. Slurm jobs run that snapshot. Replanning
replaces it, so resume an existing experiment through `status` rather than
planning it again.

Two seeds, 42 and 43 by default, provide a first screen. Confirm three to five
promising configurations in a new experiment with five seeds, for example
`--seeds 42 43 44 45 46`. The [B2 seed study](experiments/b-2-t0/index.md) motivated
this policy: close rankings can change with the training seed. A study may need
more confirmation when its candidates remain close.

### Resume an interrupted run

`status` prints the resubmission command for unfinished tasks, including
`--retry-failed` where needed. With prescribed evaluation histories, an interrupted
attempt can reuse completed fold models and forecast views. Its `run.json`
records `resumed`, `resumed_after` and the exact command. Other scenarios start
a new attempt. This shared resume path replaced `scripts/resume_b7.py` on
8 October 2026.

### Run locally or change concurrency

For local execution, plan with `--device cpu` or `mps`, then launch with
`.venv/bin/python -m chromantis.experiment.planner run -e my-study`. Local runs
use the working tree. Slurm uses the planned source snapshot and can fit several
processes per GPU. The [setup guide](setup.md#gpu-execution) lists the resources
and concurrency settings.

Notifications are enabled by default. `NTFY=0` disables them; `NTFY_URL` chooses
the topic. The launcher queues a summary after the job, including after timeout
or cancellation.

## Replay fitted models on other inputs

Use `planner replay -e NAME --inputs reported` to give every completed fold fit
archived Wednesday reports without retraining. `--inputs synthetic` uses the
prescribed artificial histories instead. Results go to
`data/experiments/NAME/replay-<inputs>/`, mirroring the saved attempts. Each replay
manifest records `refit: false`.

Rank a replay with `planner rank -e NAME --inputs reported`. Its ranking is
separate from the original fits' ranking, so the input change remains visible.

## Analyze a run

`planner rank` scores saved forecasts and produces ranking tables and a report.
All runs must share task keys and reference outcomes in every evaluated season;
the scorer stops when those conditions fail. Only each configuration's declared
forecast view receives a rank. Other input views remain diagnostic rows.

The ranking directory, `ranking-<hash>/`, contains:

| File | Contents |
|---|---|
| `headline-rankings.csv` | Configuration and input view, mean and standard deviation over seeds, full scenario strings and `deployed` flag |
| `headline-seed-scores.csv` | Primary score for each seed |
| `metric-seed-scores.csv` | WIS components and interval coverage for each seed |
| `headline-season-scores.csv` | Scores by season |
| `score-details.csv` | Scores by month, horizon and location in the declared forecast view |
| `hub-relative-scores.csv` | Scores relative to the Hub ensemble |
| `hub-pairwise-scores.csv` | Pairwise rankings against qualifying Hub models |
| `distribution-scores.csv` | Coverage, with states/DC and US reported separately |

A complete experiment also produces `docs/experiments/<name>/index.md`, including
training/evaluation definitions, rankings, comparison plots, forecast fans and
the fold layout. Handwritten text between the report's write-up markers survives
regeneration. The generator leaves pages without those markers untouched.

`--allow-incomplete` and `--seeds` create exploratory rankings without a report.
`--no-report` writes tables only. Per-seed, per-location and per-view score caches
stay in the run folders on Longleaf. Documentation holds the report, figures and
summary tables of at most 1 MB each. This size policy, adopted on 9 October 2026,
keeps raw score dumps out of the repository.

Copy completed reports back from Longleaf with:

```bash
rsync -a chadi@longleaf.unc.edu:/hickory/proj/jlessler/projects/tapestry-all/tapestry/docs/experiments/ docs/experiments/
```

## Ensembles of saved forecasts

`python -m chromantis.evaluation.ensembles GROUPS.json --out DIR` combines saved
forecasts without retraining. Each configuration has equal weight, divided
equally among its seeds. The `vincent` rule averages quantiles; `mixture` pools
predictive distributions. The production exporter uses the same combination
implementation.

The groups file identifies experiments, scenarios and seeds, or explicit run
folders. Set `"inputs": "reported"` for archived-report replays. See
`experiments/b7-folds-ensembles.json` for an example. Each ensemble is saved as
a run folder and ranked by the shared scorer under `DIR/ranking/`.

## Standard evaluation

The problem chooses evaluation inputs. A reported-input evaluation uses archived
Wednesday reports; a prescribed-input evaluation supplies shared artificial
histories; a finalized-input evaluation uses reference histories on the source
schedule. The rules below describe the reported-input protocol introduced on
5 October 2026 and the scoring tables used across studies.

### Deadlines and available inputs

Each pathogen uses its own Hub's deadline: Wednesday at 23:00 US Eastern except
for the [documented holiday extensions](data/index.md#deadlines). Extensions
change the report cutoff while retaining the nominal Wednesday and preceding
Saturday. Training examples use the FluSight deadline.

The [assumed publication schedule](data/index.md) allows all six target signals
through the latest completed Saturday, including ED in every season. ILINet,
clinical labs and FluSurv lag one week; Vermont inpatient claims are excluded.
These assumptions describe the chosen reporting regime. ED reports in 2024–25,
for example, actually arrived a week later.

Where the schedule permits a value but the archive lacks it, the builder uses
the later reference value and records a fill. Values absent from the reference
panel remain missing. Report figures mark fill shares with a star. These fills
can give a retrospective model information unavailable to historical Hub
forecasters; the footnote measures exposure to that assumption.

Scoring uses 512 forecast samples per forecast, fixed by `planner.EVAL_MEMBERS`.
`plan` no longer accepts `--eval-members`.

### Scores and task sets

| Output | Comparison and scale |
|---|---|
| `headline-*.csv` | Raw WIS against the research reference panel, with states/DC and US separate; the primary ordering uses state/DC log-admission WIS |
| `hub-relative-scores.csv` | Each location's total WIS divided by the Hub ensemble's on matched frozen tasks; state/DC ratios averaged equally, US separate |
| `hub-pairwise-scores.csv` | FluSight's 2025–26 pairwise method on the frozen support: models need 75% task coverage; geometric mean of shared-task mean-WIS ratios, normalized by the Hub baseline |
| `score-details.csv`, `distribution-scores.csv` | WIS and weekly/four-week interval coverage by month, horizon and location |
| Starred input-fill footnote | Fill shares by season, signal and Hub deadline, for the target's history, all selected histories and covariates |

Admission scores are reported in counts and after `log(1 + admissions)`;
ED scores retain proportions. Lower WIS is better. A relative score of 1 means
parity with the ensemble, or with the baseline for pairwise scores. Coverage
should be assessed against the stated interval level.

The headline calendar covers October–May reference dates at horizons 0–3.
Hub comparisons use frozen tasks and Hub reference outcomes; raw WIS uses the
research panel's reference outcomes. The task support and truth therefore differ
between tables. Each seed enters the pairwise Hub pool separately. Models below
the coverage threshold are listed as nonqualifying; Google models carry a
`Google_*` flag.

The log offset of 1 and the use of the FluSight pairwise method for COVID and
RSV are research choices. The old 80% states/DC–20% US composite ranking was
removed on 8 October 2026; training geography weights are a separate setting.
Old runs need refitting before comparison under a changed protocol.

## Cross-validation

The problem defines permitted training and evaluation folds. For season folds,
the inner split hides three weeks out of every 16, starting after the first
four weeks, to choose an epoch count. A fresh fit then uses all permitted
training weeks. Each outer evaluation season supplies no neural training labels.
The [model details](architecture.md#fitting-and-model-selection)
show the split and its information boundaries. Other fold kinds are described
in the [problem guide](multipathogen-pipeline.md#fold-kinds).
