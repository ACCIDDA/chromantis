# Datasets, problems and model configurations

A pathogen can support several forecasting questions. Predicting COVID-19
admissions over four weeks and predicting a season-long trajectory require
different horizons, labels and evaluation. Chromantis represents that distinction
with a *problem* file. Every candidate in a study is compared under the same
problem.

Three definitions connect the stored data to a fitted model:

| Definition | Contents | Location |
|---|---|---|
| Dataset | Available signals, units, pathogen groups, input/covariate sets and report-archive support | `datasets/*.json` |
| Problem | Selected targets, panel, locations, horizons, folds, evaluation inputs and primary score | `problems/*.json` |
| Configuration, or recipe | Architecture, transforms, reporting-error treatment, correction, optimizer and training budget | Scenario string in the study file |

Changing targets, inputs, horizons, folds or the primary score creates a new
problem. A configuration describes how to learn that problem. The
[workflow](workflow.md) gives the commands for planning and running a study.

## Define the dataset and problem

A dataset names each signal and its unit, optional Hub target and default
training weight. It groups signals into named input and covariate sets and
records whether archived reports exist with `report_vintages`.

A problem selects those signals and names a panel and location/population file.
US respiratory problems can share `data/processed/panel.npz` and
`data/metadata/locations.csv`. A local-area problem points to its own files,
allowing its build to leave the state panel unchanged. The problem fixes future
labels, horizons, evaluation folds, information available at prediction time
and the score used to rank candidates.

The loader in `src/chromantis/problem.py` checks signal names, folds, units and
score consistency. A log-scale primary score requires a count target. A Hub
comparison must match the primary target's Hub. The weekly evaluator requires
consecutive model offsets `1, 2, …, n`, with at least four weeks, because its
output positions correspond to Hub horizons 0 onward.

The repository includes short-term flu, COVID-19, RSV and joint-respiratory
problems, prescribed-input flu problems, production problems and a rolling-origin
flu example. Choose the definition whose scientific assumptions match the
intended study rather than inheriting a previous study's defaults.

## Fold kinds

The `folds.kind` field determines training and evaluation weeks. The same split
also controls the inner validation used to select a training duration.

| Kind | Fold definition | Training data for fold `f` | Evaluation data |
|---|---|---|---|
| `leave_one_season_out` | CDC epiweeks 31–30, such as `2024-2025` | Other seasons in `training_ids` | Season `f`, with weekly reference dates in October–May |
| `leave_one_period_out` | Named nonoverlapping periods | Other periods in `training_ids` | Every week of period `f` |
| `rolling_origin` | Named evaluation windows | Weeks before the first week of `f` | Every week of window `f` |

Period endpoints are week-ending Saturdays. Weeks outside every period are
unused for period folds. Inner validation positions count from the beginning
of each training season or period, or from the first training week for rolling
origin. `training_window=recent2` and `last2` apply only to season folds.

Reporting errors and frozen Hub comparisons still depend on season folds:
their calibration and saved support are organized by CDC season. The loader
rejects incompatible combinations. The
[architecture guide](architecture.md#challenge-5-knowing-what-a-comparison-actually-measures)
explains how retrospective and forward splits change the interpretation of a
score.

## Choose the evaluation inputs

`evaluation.inputs` specifies what a fitted model receives at prediction time.

| Value | Evaluation histories | Reporting-error stage |
|---|---|---|
| `reported` | Archived reports under the documented deadline and fill policy | Enabled |
| `prescribed` | Shared artificial preliminary histories | Enabled |
| `finalized` | Reference histories under the source publication schedule | Disabled |

Reported and prescribed evaluation require `report_vintages: true`. With
finalized evaluation, the configuration must train on reference histories and
use raw inputs: `history_source=finalized`, `forecast_view=raw`, without
`error_reference`, `correction_noise` or stress views. Planning rejects other
combinations. These folds save `model.pt`, raw `forecasts.npz` and a manifest;
`nowcaster.pkl` contains no correction model.

A problem with `comparison.kind = "none"` produces raw scores and their
breakdowns, leaving Hub-relative and pairwise tables empty.

## Choose the evaluator

`weekly_quantile_wis` scores weekly quantiles, with the standard primary and
coverage diagnostics on the first four future weeks. `season_peak` scores peak
week and size for one count target over a specified CDC-week window. The peak
evaluator requires leave-one-season-out folds, finalized inputs and
`forecast.season_window_epiweeks`.

An outcome such as accumulated burden or an outbreak-specific decision needs
an evaluator that matches its question. Changing a label or primary score in
prose cannot change the computation used by an existing evaluator.

## Plan and release

`plan --problem ...` copies the problem and dataset definitions into the
experiment directory and records hashes for the panel, locations and frozen
comparison support. Slurm runs the planned code snapshot and refuses to fit
if pinned inputs change. `planner rank` uses the current ranking code, following
the 9 October 2026 decision.

A release names its problem. Checkpoint replay checks that problem against the
hash saved during training. Checkpoints predating the problem-hash requirement
need fresh fits. The October B7 models were subsequently retrained through this
route; the [submission log](submissions.md) records the released checkpoints.

## Add a new forecasting setting

Choose the case or healthcare outcome, units, geography, forecast dates,
horizons and folds first. Examine the reporting archive before choosing an
input treatment. A dataset with revised outbreak histories alone should declare
`report_vintages: false` and use finalized evaluation.

Add source catalog entries and extraction adapters, build the panel at its own
path, then define the problem and primary score. Fit a simple configuration and
score an unpublished forecast before expanding the search. A proposed Ebola
application, for example, would need explicit outbreak definitions and either
outbreak-held-out periods or rolling-origin windows. Influenza's reporting-error
process and season boundaries would require a scientific justification there.

## Implementation record: 9 October 2026

The original migration checked 19 combinations of flu season-fold settings
against the previous week-role implementation and obtained identical roles.
It also ran one-epoch CPU checks for two cases:

- A COVID admissions/ED model trained on 2022–23, 2023–24 and 2025–26, with
  artificial reporting errors and corrected training histories, then produced
  eight-week forecasts from 2024–25 archived reports and completed ranking.
- A rolling-origin flu model trained on weeks before 4 October 2025 with
  reference histories, then produced forecasts from reference inputs over
  4 October 2025–30 May 2026 and completed scoring for 34 forecast dates.

Those runs checked execution and alignment; their one-epoch scores were not
performance evidence. At the time, work remained on other geographic builders,
non-season reporting errors and additional evaluators. Later applications should
be judged from their own implementation and reports.

The migration removed task fields such as `forecast_targets`, `pathogen_inputs`,
`forecast_weeks` and `evaluation_seasons` from recipe strings. Old artifacts are
rerun with current code rather than translated through a compatibility layer.
Slurm jobs already running retain their pinned snapshots.
