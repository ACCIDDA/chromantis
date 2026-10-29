# From a research question to a submitted forecast

A successful search produces more than a winning score. It leaves enough
information to explain why the model was chosen, reproduce the comparison and
identify the weights behind each submitted forecast. Chromantis uses problem
files, study files and release manifests to carry that record from research
into weekly operation.

The procedure below grew out of the October 2026 influenza search. The submitted
three-configuration mixture is recorded as B7; its public Hub name is
ACCIDDA-Chromantis. Branching *configuration search* refers to the sequence of
experiments. The gradient-boosted trees used to correct reports are separate
models.

## Define the comparison

The researcher chooses the outcomes and units, available inputs, training and
evaluation seasons, prediction labels, and score. Record those choices before
fitting. For reporting revisions, specify which signals are changed and which
seasons supply the errors. For evaluation, specify the weeks included and the
information available at each forecast deadline.

The protocol should name the primary score, tie-breakers and any measures used
only as diagnostics. Changing these choices starts a new comparison. A problem
file holds the task and evaluation design; a study file lists candidates and
seeds. The [problem guide](multipathogen-pipeline.md) describes their fields.

## Screen and confirm candidates

An assistant can propose configurations within the agreed question and compute
budget. Code fits the models and calculates every loss and score. Start with two
seeds and shared artificial reporting draws where that protocol applies. Change
one factor at a time when the aim is to identify its effect.

Repeat three to five promising candidates with five new seeds before choosing
among close results. More seeds reveal sensitivity to training randomness.
They cannot remove the selection bias created by searching the same epidemic
seasons repeatedly.

## Compare saved forecasts

Replay candidate fits on the same archived reports without retraining. Score
individual models and mixtures on identical tasks. Name the candidate set and
saved forecasts in the comparison: recommendations based on different candidate
sets answer different questions. That mismatch contributed to conflicting
recommendations during the 7 October influenza search.

The [workflow](workflow.md) gives the planner, replay and ranking commands.
Use its saved tables to write the interpretation, with the model, training
seasons, input treatments, prediction labels and evaluation inputs beside each
result.

## Fit a release

The researcher chooses the models and records the reason in the study's decision
list. Fresh fits then train the selected configurations on all completed
training seasons. The October flu mixture used ten seeds per configuration;
other problems can use a different count.

The release manifest lists exact checkpoint paths and hashes, preprocessing,
correction models and the combination rule. A change to a configuration,
correction model or training set produces a new release. Weekly input updates
reuse the release's saved weights.

## Issue forecasts each week

Refresh the sources, run the release on the new panel and export the Hub file.
Draw the forecast and peer-comparison graphs for researcher review. Submit a
file from the current release before the deadline. A decision to replace a file
after the deadline belongs in the submission record, with its timing and reason.

The [submission log](submissions.md) records generation, submission, merge,
replacement and renaming. Keep each submitted file and any superseded version,
with the input snapshot and file hashes. A weekly forecast should be traceable
to both its fitted models and the reports those models received.

## Keep the research record small

| Record | Location |
|---|---|
| Candidates, seeds and protocol | `experiments/<study>.json` |
| Saved-forecast combination groups | `experiments/<study>-ensembles.json` |
| Chosen fits, hashes and export rule | `production/releases/<name>.json` |
| Results and decision list | `docs/experiments/<study>/index.md` |
| Issuance and publication history | `docs/submissions.md` |
| Submitted and replaced files | `production/submissions/`, including `superseded/` |

A decision entry names the choice, evidence files, candidate set, proposer and
decision maker. When a branch stops, record whether time, failure or results
caused it. Research interpretations belong inside the report's write-up markers
so regeneration preserves them.

Keep study definitions, release manifests, the submission log and submitted
files in version control. Checkpoints, output caches and Hub clones stay outside
it. The shared planner, scorer and exporter handle each stage; new studies add
configuration files rather than their own scheduling or scoring systems.

## Adapt the procedure to another problem

Choose the new scientific assumptions before carrying over a flu configuration.
Reporting errors, Kinsa inputs, ILI pretraining, seasons and loss weights all
need a reason in the new setting. Reuse or build a dataset, write the problem,
check its reporting evidence, then fit and score a simple unpublished forecast.
That first run checks whether the full procedure represents the intended task.

## Records from the October influenza search

The notes below describe decisions and open issues as recorded on 8–9 October
2026. They preserve the origin of the workflow; later submission records may
supersede the operational details.

## Who did what for B7 (5–8 October 2026)

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


## Open gaps from B7

- **October was not evaluated.** You asked for October in the headline evaluation, but B7's selecting
  comparison started at the 23 November 2024 and 22 November 2025 reference dates. B7 was chosen
  without evidence on the early-season weeks it is now forecasting.
- **The selection score changed during the search:** first the 80/20 states/US mix, then all
  locations, then the log-admission loss, then "most likely to perform well this year." Step 1 now
  fixes the score before screening.
- **Hub metadata is out of date:** it says two recipes, five seeds and averaged quantiles. Updating
  it is deferred until the recipe settles (decision of 8 October 2026).
- **Package name:** the repository, documentation, Python package and commands use `chromantis`.

## History

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
