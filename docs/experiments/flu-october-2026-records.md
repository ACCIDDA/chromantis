# October 2026 influenza campaign: working records

These records were kept on the how-to pages while the FluSight weekly model was being built
(5–9 October 2026). They describe the code, decisions and open issues at their stated dates
and explain why the current procedure took its form; later records on the
[challenge pages](../challenges/index.md) may supersede their operational details. They were
moved here on 29 October 2026 from [Workflow](../workflow.md),
[Reusable research workflow](../reusable-research-workflow.md) and
[Multi-pathogen pipeline](../multipathogen-pipeline.md), unchanged except for heading levels
and link paths.

## From the workflow page

### Dated implementation notes

The audit and migration records below describe the code and decisions at their
stated dates. They explain why the current procedure took this form, including
findings that concerned training routes later removed.

#### Audit log, 5 October 2026

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


### Protocol of the B7 relaunch (7 October 2026)

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

### Restructuring log, 8 October 2026

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
  A–F table linked to [the explanation](../reference/model-choices.md).
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

## From the reusable research workflow

### Records from the October influenza search

The notes below describe decisions and open issues as recorded on 8–9 October
2026. They preserve the origin of the workflow; later submission records may
supersede the operational details.

### Who did what for B7 (5–8 October 2026)

| You decided | LLMs did |
|---|---|
| Assumptions: sources at T-X, ED at T-0, Kinsa not revised, 2025–26-like revisions, seasons interchangeable (no season is special) | Turned them into scenario settings; audited the code against them |
| Evaluation: per-Hub deadlines, 512 samples, natural and log scores, two seeds as default, include October, US and states reported separately (replacing the 80% states / 20% US mix), coverage is not a veto | Built the scorer and reports |
| Training objective: add the log-admission loss with weight 0.5 | Implemented it |
| Time budgets ("30 minutes", "20 more minutes", "done by 9") | Chose concrete candidates, pruned optional runs, resumed unfinished runs |
| Drop the FluSurv recipe; submit System2 on time; then "replace it" with B7 | Recommended System2 (Codex, 22:43), then B7 (Claude, then Codex, 23:58) |
| Model name, metadata flag, less code in the upload step | Wrote export, comparison graphs and git pushes |

The LLMs also ran some branches on their own initiative. One example is the peak/full-season model
study on 7 October, which you stopped at 22:05. The training audit was written by Claude (session
`dc5f13dc`). You gave the same audit prompt to Codex, then pasted Claude's findings into Codex with
your corrections at 01:05. Codex implemented the fixes. Keep such hand-offs in the decision list; a
pasted recommendation is not evidence that the person who pasted it originated it.


### Open gaps from B7

- **October was not evaluated.** You asked for October in the headline evaluation, but B7's selecting
  comparison started at the 23 November 2024 and 22 November 2025 reference dates. B7 was chosen
  without evidence on the early-season weeks it is now forecasting.
- **The selection score changed during the search:** first the 80/20 states/US mix, then all
  locations, then the log-admission loss, then "most likely to perform well this year." Step 1 now
  fixes the score before screening.
- **Hub metadata is out of date:** it says two recipes, five seeds and averaged quantiles. Updating
  it is deferred until the recipe settles (decision of 8 October 2026).
- **Package name:** the repository, documentation, Python package and commands use `chromantis`.

### History

- **8 October, first version (Codex).** A long proposal (about 3,600 words) with a development-history
  table, an actor field on every candidate, a separate `search.py`, and a full conversation evidence
  table.
- **8 October, rewrite (Claude).** At the user's request, the doc was cut to the workflow, roles,
  files and open gaps. Changes in this version:
  - corrected the Hub name;
  - corrected the audit authorship;
  - marked October as unmet;
  - added the on-time step, the candidate-set rule, target types and the git requirement;
  - removed `search.py` and the per-candidate actor fields.
- **8 October, package restructured (user decision: each step done once, unused code deleted).**
  The code changes proposed here were implemented; see the restructuring log.
- **8 October, second cut (user decision).** Replaced `decisions.jsonl` with a decision list on the
  study's report page and dropped the per-issuance JSON; the submission log plus the CSV is the
  record. The pathogen file is deferred until the second pathogen starts.
- **9 October, multi-pathogen plan (user decision).** Replaced the proposed pathogen file with
  separate dataset and problem contracts. Raw acquisition remains shared; dataset building creates
  named panels with covariates; each problem fixes targets, inputs, horizons, folds, and one primary
  evaluation; model recipes contain only training and model choices.
- **Evidence.** Claude sessions under `~/.claude/projects/-Users-chadi-Research-Tapestry/`
  (`eac542c9`, `bb6f8636`, `bd6c581f`, `6f220c65`, `2f2e91bb`, `dc5f13dc`, `1586eaad`, `73b3b686`,
  `fb4d71df`, `17ba82cf`) and Codex sessions under `~/.codex/sessions/2026/10/` (`5f6f69deae1c`,
  `afad9b37ac79`, `4d97e52b9c1b`, `d5ef40a4646d`, `f164be8480f1`), Eastern time.

## From the multi-pathogen pipeline

### Implementation record: 9 October 2026

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
