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
| Submitted | 17, 24 and 31 October, 7 and 14 November 2026 |
| Current model | The same 40 fits with the tree correction at half strength, release `production/releases/rsv-four-cs050.json` (from 14 November; `rsv-four-20261014.json`, full strength, before) |
| Latest file | 14 November 2026, [PR 721](https://github.com/CDCgov/rsv-forecast-hub/pull/721), opened 12 November |
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
sampled recipes' trajectories (Schaake shuffle) to give the 200 samples. From 14 November the
trees' log-correction is multiplied by 0.5 (release field `correction_strength`, no retraining),
because at full strength the 17 October to 7 November files forecast too high (see the
14 November entry).

## Inputs and nowcast

| Input | `Ball_c0w512` | `Bw` | `A4c0` | `A4i` |
|---|---|---|---|---|
| Histories read (12 weeks) | RSV, flu and COVID admissions and ED share | RSV, flu and COVID admissions and ED share | RSV admissions and ED share | RSV, flu and COVID admissions and ED share |
| Correction of the newest reported weeks | Yes at issuance. Trained on uncorrected histories, and also learns the final values of the last four history weeks | Yes at issuance. Trained on uncorrected histories, and also learns the final values of the last four history weeks | Yes: saved trees, also used on its training histories | Yes: saved trees, also used on its training histories |
| Other pathogens | Flu and COVID | Flu and COVID | No | Flu and COVID |
| Additional data (covariates) | None | None | National Kinsa | National Kinsa |
| Extra training data | None | None | None | None |
| Sharing across locations | Four neighbouring states | Four neighbouring states | None | None |
| Other features | Population; no calendar | Calendar, population | Population; no calendar | Calendar, population |

**Nowcast.** There is no separate nowcast model. Saved trees estimate the revisions to the two
newest reported RSV admission and ED weeks; flu and COVID histories are read as reported, with
no correction. The neural network then predicts the week still unreported (Hub horizon 0).

**Training histories.** `Ball_c0w512` trained on actual archived reports where they exist and
on histories with artificial reporting errors elsewhere; the other three trained on artificial
errors only.

**RSV admissions before 2 November 2024** are treated as unobserved in both inputs and labels,
because reporting was voluntary. RSV ED share starts in October 2022.

**Kinsa** is a national influenza-like illness series, not specific to RSV, with the same values
copied to every state ([details](flusight-weekly.md#inputs-and-nowcast)).

**Not used.** The panel's RSV-specific sources (RSV-NET and NREVSS positivity), wastewater,
claims, ILINet, clinical-laboratory positivity and FluSurv-NET; no submitted RSV model reads
them.

## How it was chosen

Tree search `rsv-tree-20261013` (`experiments/rsv-tree-20261013/protocol.json`), rooted at
the flu finalists plus a covariate branch. Each of 2024–25 and 2025–26 was held out in turn;
selection used the states/DC log-admission WIS of each seed mixture (lower is better). The
selected mixture scored 0.3105 on artificial preliminary inputs and 0.3114 replayed on
archived 2024–25 and 2025–26 reports. There is no report page for this search yet.

## Submission log

Newest first. The shared data pulls of each Wednesday are on
[Weekly data pulls](weekly-inputs.md).

### Reference date 14 November 2026

**Same 40 fits, tree correction at half strength.** [PR 721](https://github.com/CDCgov/rsv-forecast-hub/pull/721) was opened at about 17:15 EST on Thursday 12 November from branch `submit-2026-11-14` of the fork (commit `f32d85e`, "ACCIDDA-Chromantis 2026-11-14", no PR description). The Hubs released the data for the week ending 7 November on Thursday 12 November, a day late after Veterans Day, and took forecasts that day, but the configured window still closed on Wednesday 11 November at 23:59 EST. So `validate-submission` failed on `submission_time` only (every check on the file passed), as it did on every other team's Thursday PR, which the Hub maintainers merged by hand. Authorization and `approve-and-merge` passed.

- **Model:** release `production/releases/rsv-four-cs050.json`: the 40 fits of `rsv-four-20261014` (described under Current model, no refit) with the saved trees' log-correction of the two newest reported RSV admission and ED weeks multiplied by 0.5. View `corrected`, issuance 11 November.
- **Operational inputs:** root `data/operational-20261111/` (pulled by the flu session on 12 November, 16:51-17:02 EST: Delphi NHSN and NSSP, FluSight, RSV and COVID Hub target data, Kinsa). RSV panel `processed/panel-rsv.npz`, NHSN RSV admissions before 2 November 2024 masked as in training, SHA256 `39e8c421c4160372ddddb9afdccacb7013606e2707cfc640f0ab3a659b458b77`.
- **Why half strength.** The 40 fits were rerun with strength 0.5 and 0 on the 14, 21, 28 October and 4 November issuances, each on that week's operational RSV panel (no retraining), and every version was scored with the Hub's models against the Hub's target data of 12 November (weeks through 7 November), states and DC, horizons 0-3. Pairwise relative WIS, baseline = 1, lower is better, each version ranked alone among 17 models (10 for ED):

  | Correction strength | Log admissions | Admissions | ED share | US admissions mean WIS | States/DC medians ÷ observed |
  |---|---|---|---|---|---|
  | 1 (as submitted) | 0.768 (rank 9) | 0.807 (9) | 0.831 | 96 | 1.090 |
  | 0.5 | 0.785 (11) | 0.765 (6) | 0.793 | 81 | 1.051 |
  | 0 | 0.926 (15) | 0.752 (6) | 0.766 | 69 | 1.006 |
  | RSVHub-ensemble | 0.692 | 0.693 | 0.671 | 69 | 1.014 |

  The trees cause the excess (medians 9% above the data at strength 1, 1% at 0), but removing them makes log admissions much worse. Half strength gives up 0.017 on log admissions for better admission counts, ED share and US scores. The flu forecast made the same choice on 4 November. Four issuances whose newest weeks are still being revised.
- **Earlier files, scored the same way** (Hub target data of 12 November): over all four files, pairwise relative WIS 0.768 on log admissions (rank 9 of 17; RSVHub-ensemble 0.692), 0.807 on counts (rank 9), 0.831 on ED share (rank 8 of 10). The 7 November file at horizon 0: US median 1,468 against 1,207 first reported.
- **Hospitals reporting** (NHSN, all pathogens, sum over states and DC, against the median 3-5 weeks earlier in the same release): 0.871 for the week ending 7 November and 0.960 for the week before, against 0.882-0.887 and 0.966-0.979 in the four previous Wednesday releases. The holiday reduced reporting only slightly, by less than the trees' correction, so inputs were not adjusted.
- **File:** `production/submissions/2026-11-14/rsv/2026-11-14-ACCIDDA-Chromantis.parquet`, SHA256 `1a41e25469b3643ac2d726b2e1fa3c33904bd69958d229685362a60e90bd181a`; the CSV beside it has the same rows. 9,568 quantile and 83,200 sample rows: 52 locations, horizons 0-3, admissions and ED share. US admissions medians 1,686; 2,042; 2,451; 2,949 (full strength: 1,739; 2,104; 2,523; 3,029) after 1,207 reported for the week ending 7 November. The 10 other Hub models available had horizon-0 US medians of 1,390-1,746.
- **Record:** interval PDFs and the peer comparison (Hub clone `c2381bf`) in `production/submissions/2026-11-14/rsv/`.

### Reference date 7 November 2026

**Same model as 31 October.** [PR 694](https://github.com/CDCgov/rsv-forecast-hub/pull/694) was opened at 16:58 EST from branch `submit-2026-11-07` of the fork (commit `1ec40f91`, "ACCIDDA-Chromantis 2026-11-07", no PR description), based on the Hub's `main` of that afternoon (`8f4a336`). Hub validation, the designated-user authorization check and the `approve-and-merge` job passed; it was merged at 17:02 EST on 4 November.

- **Model:** release `production/releases/rsv-four-20261014.json`, the four-recipe mixture described in the 17 October entry (40 fits, trained on 2022-23 through 2025-26, no refit), run on the 4 November RSV panel with the `corrected` view.
- **Operational inputs:** [4 November pulls](weekly-inputs.md#operational-inputs-issuance-4-november-2026-reference-date-7-november), RSV panel with NHSN RSV admissions before 2 November 2024 masked.
- **Last week's file, scored:** the 31 October file at horizon 0, against the first report for the week ending 31 October. US admissions median 1,221 against 1,032 observed (the 24 October file gave 1,068 against 883 for its own horizon 0, and 1,282 for the week ending 31 October). On the 51 state/DC tasks, its mean WIS divided by RSVHub-baseline's was 0.86 on log admissions, 1.09 on counts and 0.93 on ED share (lower is better). All submitted files so far (17, 24 and 31 October), scored on every observed task against the 4 November data: pairwise relative WIS 0.788 on log admissions (rank 4 of 12; RSVHub-ensemble 0.766), 0.797 on counts (rank 4; 0.725), 0.797 on ED share (rank 7 of 9; 0.656). Same one-off script as for flu. The 17 October file did better than the baseline on all three (0.52-0.73 at horizons 0-2); the 24 and 31 October files forecast too high.
- **File:** `production/submissions/2026-11-07/rsv/2026-11-07-ACCIDDA-Chromantis.parquet`, SHA256 `71af854e2501deba4b678e455bf91bf44d5fc5619e8da537cec7886fee9e64de`; the CSV beside it has the same rows. Quantiles and 200 sample trajectories per location, horizons 0-3, 52 locations, admissions and ED share, 92,768 rows. US admissions medians: 1,468; 1,782; 2,146; 2,594, at the 80th percentile of the 5 Hub models available when it was run. The horizon-0 median is 1.42 times the last observation, while US admissions grew about 1.17 times per week over the last two weeks and the week ending 24 October was revised up 0.7% in one week; the user chose to submit it unchanged.
- **Record:** interval PDFs and the peer comparison (Hub clone `c5f5f65c`, 6 same-week models) in `production/submissions/2026-11-07/rsv/`.

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
