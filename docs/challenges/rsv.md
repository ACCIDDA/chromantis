# RSV Forecast Hub

CDC's [RSV Forecast Hub](https://github.com/CDCgov/rsv-forecast-hub) collects weekly
forecasts of laboratory-confirmed RSV hospital admissions (`wk inc rsv hosp`, NHSN counts)
and the proportion of emergency-department visits attributed to RSV
(`wk inc rsv prop ed visits`, NSSP, between 0 and 1), for the states, DC, Puerto Rico and
the United States. Each forecast gives 23 quantiles and, optionally, 200 sample
trajectories. Forecasts are due Wednesdays at 11 PM Eastern; the reference date is the
following Saturday. The season began 23 September 2026. Admission quantiles are required;
ED and samples are optional. The reviewed sources do not say whether scoring uses
admissions or log admissions ([Respiratory hub rules](../reference/hub-scoring-2026-2027.md)).

## Status

| Item | Value |
|---|---|
| Public model | ACCIDDA-Chromantis |
| Submitted | 17, 24 and 31 October 2026 |
| Current model | Four-recipe mixture, release `production/releases/rsv-four-20261014.json` (40 fits) |
| Latest file | 31 October 2026, [PR 673](https://github.com/CDCgov/rsv-forecast-hub/pull/673), merged 28 October |
| What we submit | 52 locations (no Puerto Rico), horizons 0–3, both targets, quantiles and 200 samples |

Submissions by `jcblemai`, `emprzy` and `jlessler` merge automatically once Hub validation
passes (designated users in the model metadata).

## Current model

Four recipes, ten seeds each (40 fits), mixed with equal weight per recipe and per seed:

- `Ball_c0w512`: width-512 direct-quantile MLP with neighbouring-state exchange, trained on
  the actual archived reports.
- `Bw`: width-256 direct-quantile MLP.
- `A4c0`: width-192 sampled MLP with corrected histories and Kinsa.
- `A4i`: A4 with all six admission and ED histories (flu, COVID and RSV).

**Training.** Every fit was trained on 2022–23 through 2025–26 with no season held out, on a
panel in which NHSN RSV admissions before 2024-11-02 are treated as unobserved because
reporting was voluntary. The admission and ED training histories were made preliminary with artificial errors from the 2025–26 RSV reporting process. The
prediction labels are the latest finalized future RSV admissions and ED shares (September
2026 panel).

**Each week.** The saved fits are not retrained; they read that Wednesday's reports with the
two newest weeks corrected (`corrected` view). Direct-quantile values are ordered by the
sampled recipes' trajectories (Schaake shuffle) to give the 200 samples.

## How it was chosen

Tree search `rsv-tree-20261013` (`experiments/rsv-tree-20261013/protocol.json`), rooted at
the flu finalists plus a covariate branch. Each of 2024–25 and 2025–26 was held out in turn;
selection used the states/DC log-admission WIS of each seed mixture (lower is better). The
selected mixture scored 0.3105 on artificial preliminary inputs and 0.3114 replayed on
archived 2024–25 and 2025–26 reports. There is no report page for this search yet.

## Submission log

Newest first. The shared data pulls of each Wednesday are on
[Weekly data pulls](weekly-inputs.md).

### Reference date 31 October 2026

**Same model as 24 October.** [PR 673](https://github.com/CDCgov/rsv-forecast-hub/pull/673) was opened at 18:27 EDT from branch `submit-2026-10-31` of the fork (commit `582d152a`, "ACCIDDA-Chromantis 2026-10-31", no PR description). Hub validation, the designated-user authorization check and the `approve-and-merge` job passed; it was merged at 18:34 EDT on 28 October.

- **Model:** release `production/releases/rsv-four-20261014.json`, the four-recipe mixture described in the 17 October entry (40 fits, trained on 2022-23 through 2025-26, no refit), run on the 28 October RSV panel with the `corrected` view.
- **Last week's file, scored:** the 24 October file at horizon 0, against the first report for the week ending 24 October. US admissions median 1,068 against 874 observed. On the 51 state/DC tasks, its mean WIS divided by RSVHub-baseline's was 0.94 on log admissions (rank 5 of 11; RSVHub-ensemble 0.87) and 1.24 on counts (rank 8; ensemble 1.07); on ED share 1.24 (rank 3 of 3; ensemble 1.00). Lower is better. Same one-off script as for flu.
- **File:** `production/submissions/2026-10-31/rsv/2026-10-31-ACCIDDA-Chromantis.parquet`, SHA256 `f86c4d062840b47f336ecedcb511aec8c3ddd422b36898f80602a3aed52b7409`; the CSV beside it has the same rows. Quantiles and 200 sample trajectories per location, horizons 0-3, 52 locations, admissions and ED share. US admissions medians: 1,221; 1,472; 1,769; 2,148, at the 67th percentile of the 6 Hub models available when it was run.
- **Record:** interval PDFs and the peer comparison (Hub clone `63bb1955`, 8 same-week models) in `production/submissions/2026-10-31/rsv/`.


### Reference date 24 October 2026

**Same model as 17 October.** [PR 657](https://github.com/CDCgov/rsv-forecast-hub/pull/657) was opened at 21:11 EDT from branch `submit-2026-10-24` of the fork (commit `9eda861`, "ACCIDDA-Chromantis 2026-10-24"). Hub validation, the designated-user authorization check and the `approve-and-merge` job passed; merged at 21:20 EDT the same evening.

- **Model:** release `production/releases/rsv-four-20261014.json`, the four-recipe mixture described in the 17 October entry (40 fits, trained on 2022-23 through 2025-26, no refit), run on the 21 October RSV panel with the `corrected` view.
- **Last week's file, scored:** for the week ending 17 October (first report), US admissions median 774 against 788 observed. On the 51 state/DC tasks, its mean WIS divided by RSVHub-baseline's was 0.75 on log admissions (rank 1 of 10; RSVHub-ensemble 0.81) and 0.55 on counts (rank 2); on ED share 0.82 (rank 3 of 6; ensemble 0.71). Lower is better.
- **File:** `production/submissions/2026-10-24/rsv/2026-10-24-ACCIDDA-Chromantis.parquet`, SHA256 `b08d1cfa2f7ab5f92b68b3caacfa785c829bcf86562b64b8d4481cd31c8849a8`; the CSV beside it has the same rows. Quantiles and 200 sample trajectories per location, horizons 0-3, 52 locations, admissions and ED share. US admissions medians: 1,068; 1,282; 1,537; 1,863, at the 83rd to 92nd percentile of the 10-12 Hub models available.
- **Record:** interval PDFs and the peer comparison (Hub clone `b145a6a`, 14 same-week models including open PRs) in `production/submissions/2026-10-24/rsv/`.


### Reference date 17 October 2026

**First RSV submission.** [PR 641](https://github.com/CDCgov/rsv-forecast-hub/pull/641) was opened on 14 October 2026 at 19:10 EDT from the fork's `main` (commit `0e8c4c2b`, "ACCIDDA-Chromantis 2026-10-17"). It adds the model metadata `model-metadata/ACCIDDA-Chromantis.yml` and the forecast. The RSV Hub asks for new-model metadata by 4 PM ET on the first Wednesday, so this PR missed that time. It was merged on 15 October 2026 at 12:39 UTC.

- **Model:** release `production/releases/rsv-four-20261014.json`, a mixture of four recipes with seeds 42-51 each. Equal weight per recipe and per seed; predictive distributions are mixed.
  - Ball_c0w512: width-512 direct-quantile MLP with neighbouring-state exchange, trained on the actual archived reports.
  - Bw: width-256 direct-quantile MLP.
  - A4c0: width-192 sampled MLP with corrected histories and Kinsa.
  - A4i: A4 with all six admission and ED histories.
- **Training and labels:** every fit was trained on 2022-23 through 2025-26, with no held-out season, on `panel-rsv.npz`. In that panel, NHSN RSV admissions before 2024-11-02 are treated as unobserved because reporting was voluntary. Training admission and ED histories were made preliminary with artificial errors from the prescribed 2025-26 RSV reporting process. Labels: latest finalized future RSV admissions and ED share (September 2026 panel). The recipes were selected by tree search `rsv-tree-20261013`. Held-out states/DC log-admission WIS was 0.3105 on artificial preliminary inputs and 0.3114 replayed on archived 2024-25 and 2025-26 reports (lower is better). These are retrospective comparisons, not prospective estimates.
- **Operational inputs:** issuance 14 October 2026. Panel `data/operational-20261014/processed/panel-rsv.npz`, SHA256 `cdf70c024b395ed73504428e5aa43a316d312b3bce74f7cb4cefe25e93dc5b6a`. It is the 14 October operational panel (the same pulls as the [17 October FluSight entry](flusight-weekly.md#reference-date-17-october-2026)) with the same pre-2024-11-02 RSV admission mask as in training. Inputs are the reports visible at the RSV Hub deadline; the RSV Hub's target data `as_of` 2026-10-14 covers weeks through 10 October. View: `corrected`.
- **File:** `production/submissions/2026-10-17/rsv/2026-10-17-ACCIDDA-Chromantis.parquet`, SHA256 `ac28391d2608b9b99600b5020cb5fc9e3f34946198add643ef21c96e8a98ddd3`. It is the Hub's first Parquet from us; the CSV beside it has the same rows.
  - 9,568 quantile rows and 83,200 sample rows: horizons 0-3, 52 locations (no Puerto Rico), `wk inc rsv hosp` and `wk inc rsv prop ed visits`.
  - Samples are 200 trajectories per location, with id `<state>_<k>` shared by both targets and all horizons.
  - The two sampled recipes give whole network draws, picked at evenly spaced ranks at each location. The two direct-quantile recipes give values at evenly spaced levels (0.01-0.99) of their seed-mixture quantiles. These values are ordered by the sampled recipes' trajectories (Schaake shuffle).
  - Sample medians and 10%/90% matched the exported quantiles. Sample 2.5%/97.5% were about 10% narrower.
  - `hubValidations` was not run locally; the PR's Hub CI validates.
- **Record:** the interval PDFs and the peer comparison are in `production/submissions/2026-10-17/rsv/`. The comparison was redrawn on 14 October after 19:30 EDT from Hub clone `8dd45ebb`, with 12 merged same-week models.
- **Metadata update:** on a Hub maintainer's request, `designated_github_users: [jcblemai, emprzy, jlessler]` was added (commit `87cd3c8` on the fork's `main`, same PR) so future submissions by them can auto-merge.
