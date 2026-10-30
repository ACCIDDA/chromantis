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

The [challenge pages](challenges/index.md) records generation, submission, merge,
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
| Issuance and publication history | `docs/challenges/<challenge>.md` |
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
