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
The [fitting diagram](reference/model-details.md#fitting-and-model-selection)
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
rsync -a chadi@longleaf.unc.edu:/proj/jlessler/projects/tapestry-all/tapestry/docs/experiments/ docs/experiments/
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
The [model details](reference/model-details.md#fitting-and-model-selection)
show the split and its information boundaries. Other fold kinds are described
in the [problem guide](multipathogen-pipeline.md#fold-kinds).

## Dated implementation notes

The audit and migration records below describe the code and decisions at their
stated dates. They explain why the current procedure took this form, including
findings that concerned training routes later removed.

### Audit log, 5 October 2026

Scope: the new `evaluation/standard.py`, its input construction and report callers,
and the local frozen Hub tables. This was a code and data-support audit; no model
was trained, no checkpoint was evaluated, and no existing score was recomputed.
The items below are unresolved findings, not changes to the evaluation protocol.

- **Finalized input fills assume more than archive completeness.** `episodes`
  replaces any missing archived target/covariate value with the finalized panel
  value where the assumed schedule permits it. It cannot distinguish an archive
  gap from an observation that was genuinely unpublished. In particular, giving
  2024–25 ED inputs through T-0 implements the chosen 2026–27 availability regime,
  not the information available to historical Hub submissions. Even for a genuine
  archive gap, the finalized value need not equal the original report. Comparisons
  with submitted Hub forecasts therefore mix information regimes. A footnote
  measures exposure to this assumption; it does not remove the advantage. Keep
  this retrospective experiment distinct from an evaluation using archived inputs
  only, with unavailable cells masked. Prediction labels remain finalized truth.
- **The frozen support is not the full Hub task calendar.** Its manifest explicitly
  restricts tasks to complete ensemble quantiles, frozen Hub truth, and overlap
  with the old B0 forecasts. `pairwise` uses this restricted set both for the 75%
  qualification denominator and for scores. For 2025–26 RSV admissions, local
  support contains September 27 followed by November 22, with all intervening
  reference dates absent. `hub_windows` also imposes these holes on raw WIS,
  including ED scores against panel truth. Treat results as rankings on the frozen
  subset; establish an independent task calendar before claiming full-season or
  official eligibility. The observed Google COVID coverage of 74.71% in 2025–26
  is coverage of this subset, not verified full-season eligibility.
- **Nowcast-corrected forecast evaluation does not honor each Hub's cutoff.**
  `augmentation.prepare` computes corrections once from the main FluSight panel,
  then `evaluate_hubs` applies that same correction function to every Hub's
  episodes. For reference dates December 27, 2025 and January 3, 2026, the configured
  FluSight cutoff is one day later than the COVID/RSV cutoff. Those corrections
  can incorporate reports unavailable at the latter deadlines. Corrections need
  their own Hub-specific inputs and cache identity. This concerns evaluation inputs
  for the forecast model retrained with `reporting_augmentation=nowcast`; its
  held-out prediction labels are unchanged. Also, `corrected` preserves `filled`
  after replacing values, so the saved mask no longer describes the final input
  values. No affected run's score impact was measured in this audit.
- **Finality flags change meaning for vintage-trained models.** Reported episodes
  set `known_final=available`, even for provisional reports. A forecast model
  trained with `input_mode=vintaged` and `supplied_final=True` learned that recent
  reported values have a false finality flag, but receives true flags at evaluation.
  This is a second evaluation-input treatment beyond replacing the values. Preserve
  the trained meaning or identify and evaluate this flag intervention explicitly.
  Models with `supplied_final=False` do not consume this flag.
- **Raw WIS can silently average away invalid predictions.** Unlike the frozen-task
  path, `raw_wis` does not validate finite, ordered, in-range quantiles. Pandas mean
  drops NaN WIS while `tasks` still counts those rows; seed summaries also skip NaN.
  It does not enforce identical raw task keys and truth across runs. This matters
  especially for targets/seasons without frozen Hub checks. Require valid scores
  on common tasks before averaging. Log transformation also clips negatives to
  zero instead of rejecting them. The inspected frozen truth and quantile tables
  contain no negative values or missing truth; this finding is about unguarded
  run outputs, not an observed corruption of those frozen tables.
- **Input-fill reporting loses cross-pathogen exposure.** `evaluate_hubs` retains
  each target channel's fill mask only at that channel's own Hub deadline. A joint
  model sees all six channels at the output pathogen's deadline. The stored masks
  cannot recover those other-channel fills when deadlines differ, and `input_fills`
  filters each input channel by its own pathogen's scoring dates. Save and summarize
  all input channels separately for each forecast Hub and its scored origins.

Other interpretation limits: log(count + 1), unchanged ED proportions, 80% states/DC
and 20% US weighting, and applying FluSight's pairwise method to COVID/RSV are
explicit research choices. Raw WIS uses panel truth while Hub comparisons use frozen
Hub truth, so differences between the tables are not purely normalization effects.
Each seed/configuration creates a different pairwise comparison pool; averaging
Google's scores across those pools produces a summary, not one common-pool ranking.
The WIS implementation matches its documented interval-score formula on inspection.

**Resolution, 5 October 2026 (user review).** Kept as accepted research choices:
the shared nowcast correction across Hub deadlines (affects only
`reporting_augmentation=nowcast` evaluation, two holiday rounds), restricted frozen
support for the Hub-relative and pairwise tables (no official-eligibility claim), and
finalized fills with T-0 ED (a retrospective regime, not historical real-time
performance). Fixed:

- *Raw-WIS window.* Raw WIS scores outside the Hub, so its window is now every
  Saturday from the season's first to last Hub admissions reference date, not the
  frozen subset's dates (2025–26 RSV now includes September 27 – November 15).
- *Final flag.* Reported score episodes keep the training meaning of
  `known_final`: models trained with `input_mode=vintaged` see their newest
  `asof_weeks` weeks marked non-final, older weeks final; all other training modes
  marked every available cell final. Only models with `supplied_final=True` read it.
- *Fill accounting.* A nowcast that replaces a value clears its `filled` mark.
  Forecast files keep `filled_<hub>`/`available_<hub>` for every selected input history
  at each Hub's deadline; `input_fills` reports, per target, its own history and all
  input histories read at its Hub's deadline (`all_targets_share`).

- *Raw-WIS guards.* Raw WIS now rejects duplicate tasks, non-finite, negative or
  decreasing quantiles, invalid truth and ED values above 1, and log scoring rejects
  negative values instead of clipping them. Every run must score the same tasks with
  the same truth (a hash of task keys and truth per target and season), or ranking
  stops.


## Protocol of the B7 relaunch (7 October 2026)

On 7 October 2026, the individual-model relaunch adopted a prescribed 2025–26
reporting process in every held-out season (`error_reference=2025-2026`,
now `evaluation.inputs=prescribed` in `us-flu-short-term-prescribed.json`; at the time this
was the recipe field `evaluation_inputs`, earlier `evaluation_vintaging`). Training and evaluation admission and ED histories
are artificially revised throughout their lookback, including histories with
real archived reports. Future prediction labels remain the September research
latest values. Kinsa is unchanged, and FluSurv is omitted. The epidemic folds
remain exchangeable leave-one-season-out folds, evaluating 2023–24, 2024–25 and
2025–26 and training on the other three completed seasons including 2022–23.

Revision donors match only the permitted flu admission/ED signals. By default
one donor release is shared across locations and matched on normalized level
and recent change without calendar. The closest seasonal donor release is
excluded in every recipient season. Adjacent error windows may share reference
weeks: the 2025–26 reporting process is prescribed separately, and only errors,
not donor epidemic trajectories or future labels, are transported. This rule
replaced the absolute-date full-window exclusion on 7 October 2026 because that
exclusion removed winter donors only when evaluating 2025–26. Missing donor residuals
use genuine age-aligned evidence at the same location, then national/native
location pools; they do not default to unrevised later values. The prescribed
revision calibration is separate from the epidemic training-season mask.

The default nowcaster is a small tree trained on synthetic preliminary
histories, with research latest training histories as reconstruction labels.
It corrects two admission and ED weeks. The focused 30-minute screen compares
four weeks and a residual MLP on the three-block sampled MLP, plus removal of
forecaster calendar inputs on sampled and direct-quantile leaders. A is trained behind its
cross-fitted corrector; B retains raw synthetic-history joint reconstruction
training, so its correction-estimator/window comparisons change its scoring
inputs without changing the neural fitting treatment. All forecasters are
refitted. Their modern training and epoch selection use the existing
Q95-normalized native loss plus 0.5 times log(1 + admissions) loss; ED stays
native. Historical ILI initialization and the existing training geography
weights are retained.

## Restructuring log, 8 October 2026

Every submitted model (System2, B7) and every experiment since B3 used one training
route, the former B3 "pilot" route. On the user's instruction ("each thing done once
and well"; delete unused code rather than store it), the package was reduced to that
route and one path per step:

- **Deleted training routes:** plain finalized/vintaged fits, B2 "weekend" revision
  experiments, fixed-checkpoint replay with nowcast inputs (`replay_from`), standalone
  nowcasting, nowcast-to-forecast pipelines and per-signal finalizers, with their
  modules (`experiment/{fitting,weekend,replay,finalization,two_stage,baseline,nowcast_baseline,augmentation}.py`,
  `model/{finalization,context_nowcast,revision_uncertainty,baselinenowcast,pipeline,revision_regression}.py`,
  `dataset/finalization.py`), their scenario fields and the `finalized`/`finalized_available`
  episode modes. Strings naming those fields now raise. The finality-flag and
  estimated-input network channels went with them. Their experiment pages remain as
  dated reports. To reproduce them, use git history (last commit before the restructuring:
  `8616acc`) or the `src/` snapshot stored with each Longleaf experiment
  (`data/experiments/<name>/code`). The B3–B7 changes and scripts that were never committed
  are not kept elsewhere: the local backup archive was deleted on 9 October 2026 at the
  user's request.
- **Renamed:** `experiment/pilot.py` → `experiment/fit.py`; its scoring and ranking moved
  to `evaluation/ranking.py`; the reporting-error scoping (`ScopedErrors`) merged into
  `dataset/reporting_error.py`.
- **Evaluation:** `totals.py`, `plots.py`, `report_layout.py`, `effects.py`, `reports.py`
  replaced by `ranking.py` and `report.py`; the WIS and Hub-relative helpers moved into
  `standard.py`. The B0 80/20 composite ranking and matched-effects tables were removed.
- **Scripts:** about 50 experiment-specific planners, replays, ensemble scorers and report
  scripts (B4–B7, peak study, audits) were replaced by study files, `planner replay`,
  `evaluation.ensembles` and `chromantis.production`.
- **Verification:** re-exporting the 7 October B7 forecasts through the new code reproduced
  the submitted CSV byte for byte (SHA256 `cdee271c…`); replaying one production
  checkpoint per B7 recipe on CPU gave identical forecasts with old and new code; a short
  fit of each B7 recipe gave identical training losses. All tests pass.
- **Renamed (same day, user decision):** `pilot_method` → `training_histories`
  (`two_stage` → `corrected`), `pilot_nowcaster` → `corrector_examples` + `corrector_model`,
  `evaluation_vintaging` → `evaluation_inputs`, `revision_*`/`vintage_seasons` → `error_*`,
  `evaluation_replicates` → `evaluation_draws`, `nowcast_weeks` → `reconstruction_weeks`,
  `nowcast_noise*` → `correction_noise*`. Every report from B3 on now has a model-choices
  A–F table linked to [the explanation](reference/model-choices.md).
- **Review, 9 October 2026 (user agreed):** `training_histories` bundled three choices and was
  split into `history_source`, `history_correction` and `reconstruction_labels`; the forecast
  view became a recipe field (`forecast_view`, default `corrected`), and ranking, reports and
  production use only that view (previously each configuration's best view was picked after
  scoring); protocol tables describe every configuration with its training seasons per fold,
  evaluated seasons and labels; ensembles record their own `forecast_view`, and scoring no
  longer assumes a `raw` forecast file exists (ensembles may hold only `corrected`).
- **Old names dropped, 9 October 2026 (user decision):** instead of translating old field names
  forever, the records still in use were rewritten to the current names and the translation
  code was removed. Rewritten, on Longleaf and in the local copies: the B7 folds
  (`b7-folds-20261007`), B7 production fits and operational forecasts
  (`b7-production-20261007`, `b7-operational-20261007`), and the System2 production fits and
  operational forecasts (`b6-production-system2-20261007`, `b6-operational-20261007/system2`):
  scenario strings in `jobs.csv`, `runs.csv`, run and fold manifests and operational manifests;
  run folders renamed to the current run ids (e.g. B7 production
  `…-8561787f0cec` → `…-e60aa9e03e00`, `…-5af694f72554` → `…-ffdcc78fdeae`,
  `…-d29b75ad47f9` → `…-c2af77a5341a`); ranking folders and view symlinks deleted (regenerated by
  `planner rank`). `model.pt`, correction trees and pinned code snapshots were not touched, so
  checkpoint hashes are unchanged; the metadata inside `model.pt` keeps the old string as
  provenance, so `fit --resume` cannot continue these (all are complete). The pre-migration
  record backups were deleted after the checks, at the user's request. Checks: the planner reads
  all three experiments (B7 folds 16 complete / 4 stopped, as before; B7 production 30; System2 90); all
  120 operational manifests parse and point to existing checkpoints; replaying one checkpoint
  per recipe of both releases gives forecasts identical to the pre-migration replays; re-exporting
  the 7 October forecasts reproduces both submitted files byte for byte (B7 `cdee271c…`,
  System2 `b68b3422…`); `python -m chromantis.production run` completes for B7. Every other
  experiment (B3–B6, older B7 checks) is history: its reports remain, the planner can no longer
  read it, and rerunning means a new experiment. The B4 fallback release was deleted. A System2
  release (`production/releases/system2-20261007.json`, the 80 submitted checkpoints) was added.
  Docs cleanup (9 October 2026, user decision): deleted interim B6 snapshot pages
  (`b6-extension-score-*`, `b6-candidate-ensembles-*`, `b6-broad-*`), settings-only folders
  linked from nowhere (`b6-search`, `b6-extension-check`, `b6-matched`, `b6-specialists`,
  `b7-revisions*`), `b7-plan` (never run), `training-audit` (tables without a page),
  `submission-peer-review`, `b3-vintage-flu-1000-design`, `performance-ideas`,
  `flusight-selection-review` (superseded by the submission choice review), and the root
  notes `implementation-plan.md`, `icare.md`, `todo.md`. Report folders keep their page,
  figures and tables up to 1 MB; larger tables stay in the ranking folder (`report.py`). The
  runs index is curated by hand.
  The B7 fold experiment was then renamed `b7-fast-20261007` → `b7-folds-20261007` (Longleaf
  folder and its records, the report folder `docs/experiments/b7-folds-20261007/`, the study
  files `experiments/b7-folds-20261007.json` and `experiments/b7-folds-ensembles.json`); the planner
  and the ensembles file read it. Its report pages keep the label "B7-fast" in their text.
- **Unchanged:** defaults, the saved correction-tree pickles, the WIS mathematics and the
  mixture rule. Run folders are named by `Scenario.run_id`.
