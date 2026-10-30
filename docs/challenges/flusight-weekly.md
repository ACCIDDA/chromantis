# FluSight: weekly influenza admissions and ED share

CDC's [FluSight Forecast Hub](https://github.com/cdcepi/FluSight-forecast-hub) collects
weekly forecasts of two influenza targets for the 50 states, DC, Puerto Rico and the
United States: laboratory-confirmed hospital admissions (`wk inc flu hosp`, NHSN, integer
counts) and the proportion of emergency-department visits attributed to influenza
(`wk inc flu prop ed visits`, NSSP, between 0 and 1). Each forecast gives 23 quantiles
per location, target and horizon. Forecasts are due Wednesdays at 11 PM Eastern; the
reference date is the following Saturday. The 2026–27 challenge runs 7 October 2026 to
26 May 2027. Targets, formats and the published scoring rules are on
[Respiratory hub rules](../reference/hub-scoring-2026-2027.md). Season-peak targets go in
the same file and have their own page, [Season peak](flusight-peak.md).

## Status

| Item | Value |
|---|---|
| Public model | ACCIDDA-Chromantis (the 10 October file was submitted as ACCIDDA-EpiLoom and renamed on the Hub on 8 October) |
| Submitted | 10, 17, 24 and 31 October 2026 |
| Current model | B7 refit, release `production/releases/b7-20261009.json` (30 fits) |
| Latest file | 31 October 2026, [PR 3943](https://github.com/cdcepi/FluSight-forecast-hub/pull/3943), merged 28 October |
| What we submit | 52 locations (no Puerto Rico), horizons 0–3, both targets, quantiles only |

## Current model

Three neural-network recipes, ten seeds each (30 fits), mixed with equal weight per
recipe and per seed:

- `A_blocks3`: width-96 sampled MLP with a three-block decoder and Kinsa.
- `B5_confirmed_candidate_1`: width-96 sampled MLP with Kinsa, pretrained on historical
  state ILI before August 2022.
- `B_width256`: width-256 direct-quantile MLP with neighbouring-state exchange, no Kinsa.

**Training.** Every fit was trained on the four completed seasons 2022–23 through 2025–26,
with no season held out. The admission and ED training histories were made to look like
preliminary reports by adding artificial errors drawn from the 2025–26 reporting process.
The prediction labels are the latest finalized future flu admissions and ED shares
(September 2026 panel).

**Each week.** The saved fits are not retrained. They read that Wednesday's reports; the
two newest admission and ED weeks are first corrected by the correction trees saved with
each fit (the `corrected` view). The architecture and these recipes are described on
[Architecture](../architecture.md).

## Inputs and nowcast

| Input | `A_blocks3` | `B5_confirmed_candidate_1` | `B_width256` |
|---|---|---|---|
| Histories read | 12 weeks of flu admissions and ED share | 10 weeks of flu admissions and ED share | 12 weeks of flu admissions and ED share |
| Correction of the newest reported weeks | Yes: saved trees, also used on its training histories | Yes: saved trees, also used on most of its training histories (10% left uncorrected) | Yes at issuance: saved trees. Trained on uncorrected histories, and also learns the final values of the last four history weeks |
| Other pathogens | No | No | No |
| Additional data (covariates) | National Kinsa | National Kinsa | None |
| Extra training data | None | Pretrained on state ILI from before August 2022 | None |
| Sharing across locations | None | None | Four neighbouring states |
| Other features | Calendar, population | Calendar, population, multiscale level and slope features | Calendar, population |

**Nowcast.** There is no separate nowcast model. Two things cover recent weeks. Before the
neural network runs, small gradient-boosted trees estimate the revisions to the two newest
reported admission and ED weeks; the same adjusted history then gives the forecast, so the
forecast's uncertainty does not include a range of possible revisions. The neural network
then predicts the week still unreported (Hub horizon 0) as the first of its four weeks.

**Kinsa** is a national influenza-like illness series from PopHIVE, with no state values, so the
same values are copied to every state and read as six summary features. A week counts only
once all seven of its days are visible. Kinsa gets no artificial reporting errors in training
and no correction at issuance.

**Not used.** The data panel also holds wastewater (NWSS), insurance-claims inpatient and outpatient shares, ILINet, clinical-laboratory positivity and FluSurv-NET; no submitted flu model reads them. Bes, the model submitted for
17 October only, read no covariates.

## How it was chosen

- 5–7 October: B3–B7 recipe searches on the flu short-term problem, ending with the
  three-recipe B7 mixture: [B7 folds](../experiments/b7-folds-20261007/index.md),
  [B7 production](../experiments/b7-production-20261007/index.md), and
  [why B7 replaced the on-time System2 file](../experiments/submission-choice-review-20261007.md).
- 10–12 October: tree search `tree-20261010` around the B3–B7 recipes
  (`experiments/tree-20261010/protocol.json`). Its best single recipe, Bes, was submitted
  for 17 October only. There is no report page for this search yet.
- 21 and 28 October: B7 replaced Bes after Bes over-forecast the week ending 17 October;
  the reasons and the one-week scores are in the 24 and 31 October entries below.
- Other flu experiments are listed on [Model runs](../experiments/index.md#flusight-weekly-influenza).

## Submission log

Newest first. Each entry states the fitted checkpoints, training seasons and treatments,
prediction labels, operational inputs, file hash and Hub PR record. The shared data pulls
of each Wednesday are on [Weekly data pulls](weekly-inputs.md).

### Reference date 31 October 2026

**Same B7 + Peak8 model as 24 October**, chosen over Bes on the user's decision on 28 October. [PR 3943](https://github.com/cdcepi/FluSight-forecast-hub/pull/3943) was opened at 18:26 EDT from branch `submit-2026-10-31` of the fork (commit `519b0f38`, "ACCIDDA-Chromantis 2026-10-31", no PR description), based on the Hub's `main` of that evening. Hub validation (`validate-submission`) passed; merged at 19:44 EDT on 28 October.

- **Why B7 rather than Bes:** both recipes raise the two newest admission and ED weeks with correction trees saved with each fit. Run on the four 2026-27 issuances (7-28 October), summed over states and DC, B7's trees raise the newest admission week 1.095-1.104 times and Bes's 1.131-1.141 times. Those weeks have since been revised 1.054-1.070 times after one to three weeks. In November-December 2025 (the archive holds no 2025-26 first reports before the 12 November issuance), national first reports were revised up 3-10% after one week and ended 8-16% above first report; 2026-27 first reports have been revised up 5.3-5.4% after one week. B7's correction matches that pattern; Bes's over-corrects admissions by about 4 points. B7's US week-0 median is about 1.24 times its corrected last week, close to recent observed growth (about 1.23 per week); Bes's is about 1.39 times. ED revisions (1-3% after one week) were similar in both seasons. These are four issuances with incomplete revisions, not a scored comparison. The unsubmitted Bes file is in `production/output/2026-10-28/bes-20261010/`, with `bes-vs-b7/`.
- **Season-peak targets:** in the same file, see [Season peak](flusight-peak.md).
- **Weekly model:** release `production/releases/b7-20261009.json`, the B7 three recipes as in the 24 October entry (30 fits, trained on 2022-23 through 2025-26 with the prescribed 2025-26 reporting errors, labels latest finalized future flu admissions and ED share). No refit: the saved fits were run on the 28 October reports, newest two admission and ED weeks corrected by each fit's saved trees (`corrected` view). Equal weight per recipe and per seed; predictive distributions mixed.
- **Last week's file, scored:** the 24 October file at horizon 0, against the first report for the week ending 24 October. US admissions median 6,200 against 6,006 observed. On the 51 state/DC tasks, its mean WIS divided by FluSight-baseline's was 0.66 on log admissions (rank 13 of 58 models; FluSight-ensemble 0.66) and 0.63 on counts (rank 4 of 58; ensemble 0.64). On ED share, scored on the 48 states with an observation where the baseline forecast (FluSight-baseline has no Iowa ED forecast), 0.68 (rank 10 of 17; ensemble 0.59). Lower is better. Scored with a one-off script (WIS = twice the mean pinball loss over the 23 quantiles), not the research scorer.
- **File:** `production/submissions/2026-10-31/2026-10-31-ACCIDDA-Chromantis.csv`, SHA256 `7c838548d95bdf0bedd1336eceea4bcc4f13150d30ed6a37e82b14017f98eac8`, 12,532 rows: 9,568 weekly quantile rows (52 locations, no Puerto Rico; horizons 0-3; admissions and ED share) followed by 2,964 peak rows. US admissions medians: 8,183; 9,804; 12,196; 15,270 in horizon order, at the 76th, 76th, 65th and 65th percentile of the 17 Hub models available when it was run; the US ED-share medians were above all 4 available. Local checks passed: no quantile crossing, integer weekly counts, ED at most 0.160, correct target dates, peak-week probabilities summing to one. The export record (`.json`) describes the weekly part only.
- **Record:** interval PDFs, the peer comparison (Hub clone `9a18c654`, 37 same-week models) and the season-peak PDF with its manifest are in `production/submissions/2026-10-31/`.


### Reference date 24 October 2026

**B7 refit submitted instead of Bes**, on the user's decision on 21 October. [PR 3895](https://github.com/cdcepi/FluSight-forecast-hub/pull/3895) was opened at 21:11 EDT from branch `submit-2026-10-24` of the fork (commit `d7c27a5e`, "ACCIDDA-Chromantis 2026-10-24"), based on the Hub's `main` of that evening. Hub validation (`validate-submission`) passed; merged at 21:47 EDT the same evening.

- **Why the switch:** the Bes file submitted for 17 October forecast too high. For the week ending 17 October (first report), its US admissions median was 5,762 against 4,698 observed (FluSight-ensemble: 4,831). On the 51 state/DC tasks of horizon 0, its mean WIS divided by FluSight-baseline's was 0.76 on log admissions (rank 37 of 56 models), 0.78 on counts (rank 39) and 1.21 on ED share (rank 16 of 16; lower is better). The B7 refit below, run on the same 14 October panel but not submitted, would have scored 0.70 (rank 21), 0.66 (rank 11) and 0.86 (rank 11); the FluSight-ensemble scored 0.65, 0.65 and 0.76. The B7 file submitted for 10 October, scored on its horizons 0-1, ranked 6 of 48 on log admissions (0.59, ensemble 0.58). For 24 October, Bes's US median was 7,216, the highest of 50 Hub models (peer median 5,678); the B7 refit gave 6,200 (76th percentile). This is one scored week and is noisy: over the held-out seasons of the 10 October tree search, Bes scored better than B7 (0.2895 against 0.2976 state/DC log-admission WIS). The unsubmitted Bes file for 24 October is in `production/output/2026-10-21/bes-20261010/`.
- **Season-peak targets:** in the same file, see [Season peak](flusight-peak.md).
- **Weekly model:** release `production/releases/b7-20261009.json`, the B7 three recipes (`A_blocks3`, `B5_confirmed_candidate_1`, `B_width256`, see the 10 October entry) retrained on 9 October 2026 with the current code, seeds 42-51 each, 30 fits. Same recipes, seeds, training panel and treatments as the B7 checkpoints submitted for 10 October (`b7-20261007`), which no longer load. Trained on 2022-23 through 2025-26 with no held-out season; training admission and ED histories made preliminary with the prescribed 2025-26 reporting errors; labels are latest finalized future flu admissions and ED share (September 2026 panel). No refit this week: the saved fits were run on the 21 October reports, with the newest two admission and ED weeks corrected by each fit's saved trees (`corrected` view). Equal weight per recipe and per seed; predictive distributions mixed.
- **File:** `production/submissions/2026-10-24/2026-10-24-ACCIDDA-Chromantis.csv`, SHA256 `7666f2bd5f9f6e5be75bbfa02bc8b8182902990e8aaa9452ba4963872e2b230f`, 12,532 rows: 9,568 weekly quantile rows (52 locations, no Puerto Rico; horizons 0-3; admissions and ED share) followed by 2,964 peak rows. US admissions medians: 6,200; 7,383; 9,272; 11,831 in horizon order. Local checks passed: no quantile crossing, integer counts, ED at most 0.156, correct target dates. The export record (`.json`) describes the weekly part only, so the peer comparison does not repeat the model description.
- **Record:** interval PDFs, the peer comparison (Hub clone `3b4ceeb6`, 57 same-week models including open PRs) and the season-peak PDF with its manifest are in `production/submissions/2026-10-24/`. The scoring of the 17 October files and the comparison with selected Hub models are in `production/output/2026-10-21/check-2026-10-17/` and `production/output/2026-10-21/vs-hub-models/`.


### Reference date 17 October 2026

**Bes was submitted** in [PR 3804](https://github.com/cdcepi/FluSight-forecast-hub/pull/3804), opened 14 October 2026 at 17:09 EDT from the fork's `main` (commit `62a30211`). Hub validation passed and it was merged on 14 October, with weekly targets only. That file is kept in `production/submissions/2026-10-17/superseded/`.

Season-peak targets were added to the same file on 14 October, see [Season peak](flusight-peak.md#reference-date-17-october-2026).

- **Model:** release `production/releases/bes-20261010.json`. One recipe, B_width256: a width-256 MLP with neighbouring-state exchange and 23 direct quantiles, seeds 42-51. Each fit was trained on 2022-23 through 2025-26, with no held-out season. Training admission and ED histories were made preliminary with artificial errors from the prescribed 2025-26 reporting process at 1.5x strength, plus reconstruction labels for the last 4 history weeks. No covariates. Labels: latest finalized future flu admissions and ED share (September 2026 panel). Equal weight per seed; predictive distributions mixed.
- **Why Bes replaced B7:** in the 10 October tree search (`experiments/tree-20261010/protocol.json`), on states/DC log-admission WIS, Bes scored 0.2895 against 0.2976 for the submitted B7 mixture on the same held-out seasons. It was worse than B7 in 2023-24. In the forward-only check (2024-25 forecast by models trained on 2022-23 and 2023-24 only) it scored 0.336 against 0.368. Lower is better. These are retrospective comparisons, not prospective estimates.
- **Operational inputs:** issuance 14 October 2026. Panel `data/operational-20261014/processed/panel.npz`, SHA256 `b8de0b1fd792eeab48f681d661f9feaae944de87aedaf3c28e5cec9f71d4dab9`. It was built from snapshots pulled on 14 October 2026 around 20:34 UTC (Hub target history including the 14 October release, Delphi NHSN and NSSP, PopHIVE Kinsa). Admissions and ED through the week ending 10 October matched the Hub target data exactly for every location over the last 8 weeks. The newest two admission and ED weeks were corrected by each fit's saved trees (`corrected` view).
- **Data note:** Iowa flu ED share was missing in the Hub's 30 September and 7 October releases (weeks ending 4 July to 3 October) and was filled in on 14 October. The 10 October submission therefore had no Iowa ED history for its last 14 weeks; this one does.
- **File:** `production/submissions/2026-10-17/2026-10-17-ACCIDDA-Chromantis.csv`, SHA256 `a4764eb9ad29a816330136c79902f63e2138605a0d5a52e95ca10640ed20880a`. It contains 9,568 quantile rows: horizons 0-3, 52 locations (no Puerto Rico), admissions and ED share, and no peak targets. Local checks passed: ED at most 0.25, admissions below 30% of population, no quantile crossing, integer counts, and correct target dates. The Hub's `hubValidations` was not run locally; the PR's Hub CI validates.
- **Record:** the interval PDFs and the peer comparison drawn at submission time are in `production/submissions/2026-10-17/`. Peers came from the local Hub clone at `8e6ffa74`, with 13 same-week forecasts merged; Google, CMU, UGA, UMass-flusion and NAU-vulPES had not yet submitted.
- **Not used:** B7 run on the same panel (release `b7-20261009`, the 9 October retrain on the current code) forecast lower values: US admissions median 5,049 against Bes's 5,762 at horizon 0, and 9,249 against 11,694 at horizon 3. The exact submitted B7 checkpoints (`b7-20261007`) no longer load in the current code: their saved settings include a field, `forecast_targets`, that it no longer accepts.


### Reference date 10 October 2026

**B7 was submitted and merged.** The Hub's merged CSV is byte-for-byte identical to the saved three-recipe B7 export and the local submission record. Verified on 8 October 2026 by hashing the file at the merge commit of [PR 3764](https://github.com/cdcepi/FluSight-forecast-hub/pull/3764) and the renamed file on Hub `main` after [PR 3774](https://github.com/cdcepi/FluSight-forecast-hub/pull/3774).

#### Submission history

All times below are Eastern Daylight Time.

| Time | Event |
| --- | --- |
| 7 October, 10:47:26 pm | Commit `2346eadf83ab0fcd16e6d36d5c63d2cfd4069d35` contained the on-time eight-recipe, 80-fit mixture without FluSurv, called System2 during development. |
| 7 October, 11:00 pm | Weekly submission deadline. |
| 8 October, 12:23:20 am | Commit `b1d0076ba7fd08e71ed5be8ba705e4262dbe0393`, “update submission past deadline,” replaced that CSV with the three-recipe, 30-fit B7 mixture. The user explicitly requested the replacement and commit message. |
| 8 October, 12:25:40 am | The replacement's Hub validation check failed on one check only, `submission_time` (pushed at 04:25 UTC, outside the round's window). No format or value check failed. The earlier on-time head had passed. |
| 8 October, 7:06:03 am | PR 3764 merged as `1b168879a7cc46fbd62b716be4af242caec1061b`. Inclusion in the round's Hub ensemble is a separate fact and is not established by this log. |
| 8 October, 1:09 pm | The user renamed the model on the Hub: commit `6d20dff5`, “model-rename”, moved `ACCIDDA-EpiLoom` to `ACCIDDA-Chromantis` (metadata and `model-output/ACCIDDA-Chromantis/2026-10-10-ACCIDDA-Chromantis.csv`). Only `model_name`, `model_abbr` and the name in `methods_long` changed; the CSV is unchanged (same SHA256 as below). |
| 8 October, 1:36 pm | [PR 3774](https://github.com/cdcepi/FluSight-forecast-hub/pull/3774), “rename mode ACCIDDA_EpiLoom to ACCIDDA_Chromantis”, merged. |

#### What the merged forecast contains

- Public name: **ACCIDDA-Chromantis** since 8 October (submitted as ACCIDDA-EpiLoom). `EpiLoomB7` and `System2` are local export names, not submitted models.
- Issuance: **7 October 2026**, with input context through **3 October**. Reference date: **10 October**.
- Targets: weekly incident influenza hospital admissions in counts and influenza ED visits as proportions from 0 to 1.
- Geography: 50 states, DC and native US, 52 locations total; no Puerto Rico.
- Horizons: 0–3, for weeks ending 10, 17, 24 and 31 October. No sample, peak or rate-change targets were submitted.
- Format: 23 quantiles per task, **9,568 rows** = 52 locations × 2 targets × 4 horizons × 23 quantiles.
- National admission medians: **4,133; 4,698; 5,631; 7,063**, in horizon order. These are forecasts, not observed outcomes.

#### The model that produced it

All three neural-network recipes were **retrained on the four completed seasons 2022–23, 2023–24, 2024–25 and 2025–26**, with seeds **42–51** for each recipe. There are 30 fits. Production fitting did not hold out an epidemic season.

Admission and ED training histories were artificially made preliminary using the prescribed **2025–26 reporting-error process**. Future prediction labels remained the frozen research panel's latest flu admissions and ED values, described by the research protocol as the September 2026 reference values. Artificial revisions changed inputs, not future labels. Training and epoch selection used the existing normalized native loss plus **0.5 times the log-admission loss**; ED remained on its native scale.

| Recipe identifier | Model and training treatment |
| --- | --- |
| `A_blocks3` | Width-96 sampled MLP with a three-block decoder and Kinsa. Learns future labels from artificial admission/ED histories corrected by cross-fitted trees. |
| `B5_confirmed_candidate_1` | Width-96 sampled MLP with Kinsa and historical state ILI pretraining before August 2022. Uses the corrected-history training route, with its recipe-specific realizations and uncorrected share. ILI is a pretraining source, not a live input requirement. |
| `B_width256` | Width-256 direct-quantile MLP with neighboring-location exchange and no Kinsa. Learns from artificial preliminary histories, with recent-history reconstruction labels as an auxiliary objective and latest future labels. |

For the operational forecast, the **already fitted** models were replayed on real reported inputs from the pinned 7 October panel, with their saved two-week admission/ED correction trees. This replay did not retrain the neural networks. Kinsa was retained for the two sampled recipes, assumed available and non-revising. No FluSurv or other-pathogen histories were used. Calendar inputs remained enabled; the separate calendar-jitter and 2024 reporting-lapse masking proposal was **not this submitted model**.

The predictive distributions were mixed with equal recipe weights and equal seed weights within recipes: one third per recipe and one thirtieth per fit. This was **distribution mixing**, not averaging member quantiles. The Hub received marginal quantiles; this does not establish calibrated joint epidemic trajectories.

#### Selection evidence and its scope

The final matched comparison replayed saved fold models; it did not retrain them. For evaluation on **2024–25**, both systems trained on **2022–23, 2023–24 and 2025–26**. For evaluation on **2025–26**, both trained on **2022–23 through 2024–25**. Both learned latest future admission/ED labels. B7 used artificial admission and ED revisions in training as described above; the eight-recipe System2 retained its B6 recipe-specific treatments, with ED mostly at latest values and no FluSurv member.

Both received the same archived Wednesday reports, including the existing substitutions with later values, and their own saved corrections. Scoring used identical FluSight tasks: reference dates 23 November 2024–31 May 2025 and 22 November 2025–30 May 2026, horizons 0–3. Admissions average those seasons equally; ED covers 2025–26 only. The table is for states/DC, using two seeds per recipe on both sides, not the 10-seed production fits.

| Measure with lower values better | Three-recipe B7 | Eight-recipe System2 without FluSurv |
| --- | ---: | ---: |
| WIS on log of admissions plus one | 0.2642 | 0.2737 |
| Admission-count WIS | 62.14 | 59.59 |
| ED-proportion WIS | 0.005041 | 0.005090 |

B7 traded approximately **3.5% lower log-admission WIS for 4.3% higher admission-count WIS**, with similar ED accuracy. That supported choosing it when season-long state log-admission accuracy was the priority. It does not quantify the expected benefit of the October 10 forecast. The comparison omitted October and early November, reused seasons for selection, and used 2025–26 reporting errors to construct B7's correction even when evaluating that season. The 2024–25 epidemic fold also used later-season training. These are exploratory, exchangeable-season comparisons, not an untouched prospective accuracy estimate.

#### Exact artifacts and outstanding discrepancies

Both 10 October files have their interval PDFs (`*-flu-hospital-admissions-forecast-intervals-50-80-95.pdf`, `*-flu-ED-visit-share-forecast-intervals-50-80-95.pdf`) and peer comparison (`*-flu-forecast-medians-vs-hub-models.pdf`, peers merged by the Hub's 7 October 22:46 EDT commit `f66ce884`) in `production/submissions/2026-10-10/` and its `superseded/` folder. They were redrawn on 9 October 2026 from that same local Hub clone, which had not been updated since the submissions; the System2 file's interval PDFs had not been kept at the time.

Local copies were renamed from `ACCIDDA-EpiLoom` to `ACCIDDA-Chromantis` on 14 October 2026; the file contents did not change. The [merged Hub CSV](https://github.com/cdcepi/FluSight-forecast-hub/blob/1b168879a7cc46fbd62b716be4af242caec1061b/model-output/ACCIDDA-EpiLoom/2026-10-10-ACCIDDA-EpiLoom.csv), the renamed [`2026-10-10-ACCIDDA-Chromantis.csv`](https://github.com/cdcepi/FluSight-forecast-hub/blob/main/model-output/ACCIDDA-Chromantis/2026-10-10-ACCIDDA-Chromantis.csv) on Hub `main`, `production/submissions/2026-10-10/2026-10-10-ACCIDDA-Chromantis.csv`, and `output/b7/submission-20261007/2026-10-10-ACCIDDA-EpiLoomB7.csv` share SHA256:

```text
cdee271c326437b81049daed50c453d8b5210ebffa9690d8d593b39e06cf607a
```

The operational panel SHA256 is `68962ec56c8246469bb71c416f9e2abc593d7b68469dd5f4817caf71743029cc`. The export manifest records all 30 forecast sources and their hashes in `output/b7/submission-20261007/2026-10-10-ACCIDDA-EpiLoomB7.json`. Re-exporting those forecasts with the current code (`chromantis.production`, 8 October) reproduces the submitted CSV byte for byte. The production training design is `docs/experiments/b7-production-20261007/design.json`.

The superseded on-time CSV is `production/submissions/2026-10-10/superseded/2026-10-10-ACCIDDA-Chromantis.csv` (as submitted on time), SHA256 `b68b34228bbd4feee5d03fe7ac1e3703f379d4c0dd9cc636f8584b3c7e5f7a70`.

The Hub metadata (`ACCIDDA-Chromantis.yml`) still describes two recipes, five seeds per recipe and averaged quantiles, which matches neither submitted version (B7: three recipes, ten seeds, mixed distributions). Its `ensemble_of_models: false` was set at the user's request at 10:13 pm on 7 October (commit `e8d8ec1d`, “fix ensemble”), when the submission was thought to be a seed ensemble of one recipe; a multi-recipe mixture may need `true`. The B7 export manifest also still says `published: false`, reflecting its pre-publication export state. The B7 release is `production/releases/b7-20261007.json` (all 30 checkpoints with the SHA256 of each `model.pt`, matching the hashes recorded when the forecast was made); the on-time System2 file can be regenerated from `production/releases/system2-20261007.json` (the 80 submitted checkpoints). Decision on 8 October 2026: defer Hub metadata changes until the recipe is settled. The log preserves the methods actually used for each issuance even when later submissions use a different recipe. This log records the actual merged model without changing Hub metadata or launching another submission.

Scientific sources: [production fit](../experiments/b7-production-20261007/index.md), [matched comparison](../experiments/b7-folds-20261007/vs-system2/index.md), [submission decision review](../experiments/submission-choice-review-20261007.md).

The production-fit page reports a second, larger comparison (55 weeks, real reports): B7 state/DC log-admission WIS 4% lower than System2, counts even, ED 2% worse. The table above (two seeds per recipe, both systems) shows ED 1% better for B7. The two comparisons differ in seeds and support; neither is a prospective estimate. The earlier production-fit report uses “submitted” for the then-current System2 file; the chronology above resolves that ambiguity.
