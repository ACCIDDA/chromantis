# COVID-19 Forecast Hub

CDC's [COVID-19 Forecast Hub](https://github.com/CDCgov/covid19-forecast-hub) collects
weekly forecasts of laboratory-confirmed COVID-19 hospital admissions
(`wk inc covid hosp`, NHSN counts) and the proportion of emergency-department visits
attributed to COVID-19 (`wk inc covid prop ed visits`, NSSP, between 0 and 1). Each
forecast gives 23 quantiles and, optionally, 200 sample trajectories. Forecasts are due
Wednesdays at 11 PM Eastern, on a rolling schedule. Admission quantiles are required; ED and
samples are optional. The Hub dashboard scores both natural and `log(value + 1)` scales
([Respiratory hub rules](../reference/hub-scoring-2026-2027.md)).

## Status

**Submitting from 7 November 2026.** First-time teams register metadata, reviewed by hand:
[PR 2017](https://github.com/CDCgov/covid19-forecast-hub/pull/2017), opened at about 17:00 EST
on 4 November (after the Hub's suggested 4 PM deadline) and merged at 17:05 EST. The first
forecast is [PR 2018](https://github.com/CDCgov/covid19-forecast-hub/pull/2018), merged at
17:19 EST.

## Current model

From 28 November the same 40 fits are issued with the tree correction at half strength
(`production/releases/covid-gru-four-cs050.json`); before, at full strength.

Release `production/releases/covid-gru-four-candidate-20261103.json`: an equal mixture of
four recipes, each refit on all of 2022–23 through 2025–26 with labels the finalized future
COVID admissions and ED shares, ten seeds (42–51) per recipe, equal weight per seed:

- `Ah.neighbors`: width-192 sampled MLP, neighbouring-state exchange, artificial reporting
  errors on half of the training episodes. Its draws order the other recipes' samples.
- `pN.enc_gru`: GRU encoder, states share a US-only summary, artificial reporting errors on
  25% of the training episodes.
- `N.multiscale`: finalized training histories, US-only summary, multiscale history features.
- `Bh.wd`: neighbouring-state exchange, artificial reporting errors on half of the training
  episodes, weight decay.

It was chosen in the `covid-tree-20261030` search (`experiments/covid-tree-20261030/protocol.json`,
decision of 3 November). Lower is better for every score:

- Held-out seasons (the same four recipes trained on the other seasons, seeds 208–215):
  states/DC WIS of log(1 + admissions) 0.2197, against 0.2371 for the earlier two-recipe
  fallback. Trained on 2022–23 to 2024–25 and scored on archived 2025–26 reports, its WIS
  divided by CovidHub-ensemble's was 0.92 (states/DC) and 0.84 (US) on log admissions, and
  1.06 and 1.41 on ED share.
- Live check: the all-season fits run on the 14 and 21 October reports, horizons 0–1, truth as
  of 28 October. Log-admission WIS 0.172 (states/DC) and 0.039 (US), against 0.170 and 0.048
  for CovidHub-ensemble.

The recipes and the mixture were selected on the same seasons, seeds and live weeks that
score them, so these numbers are optimistic. The October 2026 candidates
(`covid-*-candidate-20261015.json`) were never submitted.

## Inputs and nowcast

The table below describes the 15 October candidate, not the submitted model; it has not been
updated.

For the leading candidate, `covid-half-perturbation-candidate-20261015`; nothing here has been
submitted.

| Input | Direct-quantile MLP (`B_width256.errors_half_time`) | Sampled MLP (`A4.errors_half_time`) |
|---|---|---|
| Histories read | 12 weeks of COVID admissions and ED share | 12 weeks of COVID admissions and ED share |
| Correction of the newest reported weeks | Yes at issuance: saved trees. Trained on uncorrected histories, and also learns the final values of the last four history weeks | Yes: saved trees, also used on its training histories |
| Other pathogens | No | No |
| Additional data (covariates) | None | None |
| Extra training data | None | None |
| Sharing across locations | Four neighbouring states | None |
| Other features | Calendar, population | Calendar, population |

**Nowcast.** No separate nowcast model, as on [FluSight weekly](flusight-weekly.md#inputs-and-nowcast):
trees estimate the revisions to the two newest reported weeks, and the neural network predicts
the unreported week. Artificial reporting errors are applied to only half of the training
episodes.

**Not used.** No covariate is read by this candidate. The `covid-ed-20261015` search also tried
the claims inpatient share and wastewater among its ED changes; neither is in the leading
candidate.

## How they were found

- `covid-tree-20261014` (`experiments/covid-tree-20261014/protocol.json`): current recipe
  families fitted to COVID admissions and ED share, horizons 1–4. Each of 2023–24, 2024–25 and
  2025–26 was held out in turn, training on the other seasons from 2022–23 to 2025–26; a
  forward-only check trains on earlier seasons only.
- `covid-ed-20261015` (`experiments/covid-ed-20261015/protocol.json`): aimed at ED
  natural-scale WIS against CovidHub-ensemble and interval coverage, without hurting
  admissions. Trained on 2022–23 to 2024–25 and evaluated on archived 2025–26 reports; 2025–26
  had already been used for choices, so it is not an untouched test.

There is no report page for these searches yet.

## Submission log

Newest first. The shared data pulls of each Wednesday are on
[Weekly data pulls](weekly-inputs.md).

### Reference date 28 November 2026

**Same 40 fits, tree correction at half strength.** [PR 2105](https://github.com/CDCgov/covid19-forecast-hub/pull/2105) was opened at 22:19 EST on Thursday 26 November from branch `submit-2026-11-28` of the fork (commit `1a00391`, "ACCIDDA-Chromantis 2026-11-28", no PR description). The Hub gave this Thanksgiving week its own round in `tasks.json` (Hub change of 24 November), with the window closing Thursday 26 November instead of Wednesday.

- **Choice of model.** The user kept the submitted fits rather than the drafts of `covid-rsv-search-20261124` (their coverage panel has never been built for a live week) or the earlier `covid-rsv-coverage-20261118` recipes (selected with leaky reporting errors and on live 2026-27 weeks). The full-strength file was made first (US medians 7,158; 8,236; 9,309; 10,090, above all 16 Hub models merged then); the user then chose half strength.
- **Model:** release `production/releases/covid-gru-four-cs050.json` (the 40 fits of `covid-gru-four-candidate-20261103`, trees at half strength, no retraining), issuance 25 November, view `corrected`.
- **Operational inputs:** [25 November root](weekly-inputs.md#operational-inputs-issuance-25-november-2026-reference-date-28-november), panel `panel.npz`, SHA256 `71ae17186fb43829cdd0de6c6193f9dec2a6080051f7255930ebe80406624b4d`.
- **File:** `production/submissions/2026-11-28/covid/2026-11-28-ACCIDDA-Chromantis.parquet`, SHA256 `c4579218052539783e333d5eb21f60c40cc534c0ed11c24a7b0efbb9f760ca62`; the CSV beside it has the same rows. 9,568 quantile and 83,200 sample rows: 52 locations, horizons 0-3, admissions and ED share. US admissions medians 6,970; 8,025; 9,081; 9,858 after 5,335 reported for the week ending 21 November (4,690 and 5,119 the two weeks before). The 16 Hub models merged when it was run (baseline included) had horizon-0 US medians of 5,102-6,619, so this file is again the highest; most of the rise comes from the networks.
- **Export fix:** `production/export.py` read only the first round of the Hub's `tasks.json`, which no longer lists 28 November; it now uses the round that lists the reference date. The first run also lacked `--samples` and was rerun.
- **Record:** interval PDFs and the peer comparison (Hub clone `ac5bae1`) in `production/submissions/2026-11-28/covid/`.

### Reference date 21 November 2026

**Same model as 7 and 14 November, full-strength tree correction.** [PR 2068](https://github.com/CDCgov/covid19-forecast-hub/pull/2068) was opened at 16:10 EST on 18 November from branch `submit-2026-11-21` of the fork (commit `2f82da6`, "ACCIDDA-Chromantis 2026-11-21", no PR description). Every check passed, including validation, and the Hub bot merged it at 16:14 EST.

- **Model:** release `production/releases/covid-gru-four-candidate-20261103.json`, issuance 18 November, view `corrected`.
- **Operational inputs:** [18 November pulls](weekly-inputs.md#operational-inputs-issuance-18-november-2026-reference-date-21-november), panel `panel.npz`, SHA256 `d4cccc684df500c0a8c00657b1cd3c7816a2fb63d3e795b6044934547f40ed2a`.
- **Earlier files, scored** with every Hub model against the Hub's target data of 18 November (weeks through 14 November), states and DC, horizons 0-3, pairwise relative WIS (baseline = 1, lower is better):
  - The 14 November file at horizon 0: 0.576 on log admissions (rank 13 of 20; CovidHub-ensemble 0.479), 0.762 on counts (rank 14), 0.830 on ED share (rank 4 of 9). The same fits at half strength would have scored 0.545, 0.695 and 0.801. US median 5,530 against 4,900 first reported.
  - Both files (7 and 14 November): 0.467 on log admissions (rank 8 of 22; ensemble 0.431), 0.634 on counts (rank 13; 0.515), 0.761 on ED share (rank 5 of 10; 0.698). Medians 12% above the data.
- **Why full strength was kept.** The same 40 fits were scored over five issuances (14 October-11 November, each on its own operational panel, no retraining; 22 models, 10 for ED):

  | Version | Log admissions | Counts | ED share | Medians / observed |
  |---|---|---|---|---|
  | Full strength (submitted) | 0.410 (rank 5) | 0.518 | 0.891 | 0.892 |
  | Half strength (`covid-gru-four-cs050`) | 0.422 | 0.528 | 0.912 | 0.866 |
  | Matched (`covid-gru-four-matched`) | 0.421 | 0.523 | 0.908 | 0.878 |
  | No trees (`covid-gru-four-cs000`) | 0.459 | 0.545 | 0.942 | 0.840 |
  | CovidHub-ensemble | 0.409 | 0.515 | 0.804 | |

  Over these five weeks the model was too low for the three October reference dates and too high for 7 and 14 November, with no consistent excess; full strength is best on every score. The trees do not over-correct COVID either: they add x1.054 to the newest admission week (x1.027 to US ED share), and that week has since grown x1.084 (x1.046-1.102) in 2026-27 and ended x1.111 in 2025-26 (ED x1.045-1.048); details in the [RSV entry](rsv.md#reference-date-21-november-2026). The matched release gives the trees at full strength to `Ah.neighbors` (trained on corrected histories) and `N.multiscale` (finalized histories) and reports as published to `pN.enc_gru` and `Bh.wd` (uncorrected histories with reconstruction labels); it gains nothing.
- **File:** `production/submissions/2026-11-21/covid/2026-11-21-ACCIDDA-Chromantis.parquet`, SHA256 `2b19ef98c0ad2ca6cdea1dfe8a3845f6abdda1391137e52b8540fa4524debaa2`; the CSV beside it has the same rows. 9,568 quantile and 83,200 sample rows: 52 locations, horizons 0-3, admissions and ED share. US admissions medians 6,144; 7,014; 7,940; 8,764 (half strength: 5,963; 6,811; 7,719; 8,519) after 4,900 reported for the week ending 14 November (4,225; 4,747; 4,659 the three weeks before). This is above all 4 Hub models merged when it was run (baseline included; horizon-0 US medians 4,900-5,655, horizon 3 up to 6,819). The user chose full strength.
- **Record:** interval PDFs and the peer comparison (Hub clone `72d118e`) in `production/submissions/2026-11-21/covid/`.

### Reference date 14 November 2026

**Same model as 7 November.** [PR 2049](https://github.com/CDCgov/covid19-forecast-hub/pull/2049) was opened at about 17:15 EST on Thursday 12 November from branch `submit-2026-11-14` of the fork (commit `e670ff5`, "ACCIDDA-Chromantis 2026-11-14", no PR description). The Hubs released the data for the week ending 7 November on Thursday 12 November, a day late after Veterans Day, and took forecasts that day, but the configured window still closed on Wednesday 11 November at 23:59 EST. So `validate-submission` failed on `submission_time` only (every check on the file passed), as it did on every other team's Thursday PR, which the Hub maintainers merged by hand. Authorization passed; `approve-and-merge` failed on a GitHub GraphQL error, and the job could not be rerun from the fork. A Hub maintainer (O957) merged it by hand at 17:23 EST on 12 November.

- **Model:** release `production/releases/covid-gru-four-candidate-20261103.json` (40 fits, described under Current model, no refit), full-strength tree correction, view `corrected`, issuance 11 November.
- **Operational inputs:** root `data/operational-20261111/` (pulled by the flu session on 12 November, 16:51-17:02 EST), panel `processed/panel.npz`, SHA256 `f478b2da51e97e1403ac557b4dbbb2dd46a9bf4cf38c9151a198c56b39cdb90d` (the flu panel).
- **Why the correction was not weakened.** The 40 fits were rerun with the trees' log-correction multiplied by 0.5 and 0 (releases `covid-gru-four-cs050` and `covid-gru-four-cs000`, no retraining) on the 14, 21, 28 October and 4 November issuances, each on that week's operational panel, and every version was scored with the Hub's models against the Hub's target data of 12 November (weeks through 7 November), states and DC, horizons 0-3. Pairwise relative WIS, baseline = 1, lower is better, each version ranked alone among 21 models (9 for ED):

  | Correction strength | Log admissions | Admissions | ED share | US admissions mean WIS | States/DC medians ÷ observed |
  |---|---|---|---|---|---|
  | 1 (submitted) | 0.409 (rank 2) | 0.493 (3) | 0.909 | 363 | 0.885 |
  | 0.5 | 0.425 (3) | 0.512 (3) | 0.939 | 406 | 0.859 |
  | 0 | 0.462 (12) | 0.539 (6) | 0.981 | 454 | 0.833 |
  | CovidHub-ensemble | 0.425 | 0.526 | 0.810 | 362 | 0.852 |

  Over these four issuances the model was not too high (medians below the data, which will still be revised up); the submitted 7 November file was: US median 5,217 at horizon 0 against 4,412 first reported. Scored at horizon 0 against the 12 November data, that file had pairwise relative WIS 0.535 on log admissions (rank 9 of 20; CovidHub-ensemble 0.472), 0.778 on counts (rank 14) and 0.805 on ED share (rank 5 of 9).
- **Hospitals reporting:** slightly fewer than usual for the week ending 7 November after the holiday (0.871 of the hospitals reporting 3-5 weeks earlier, against 0.882-0.887 in the four previous Wednesday releases; details in the [RSV entry](rsv.md#reference-date-14-november-2026)). Inputs were not adjusted.
- **File:** `production/submissions/2026-11-14/covid/2026-11-14-ACCIDDA-Chromantis.parquet`, SHA256 `1b369930d73e07fffc6ecf3b872642e71ece16a0a6451f24808d11106495222e`; the CSV beside it has the same rows. 9,568 quantile and 83,200 sample rows: 52 locations, horizons 0-3, admissions and ED share. US admissions medians 5,530; 6,259; 7,055; 7,784, after 4,412 reported for the week ending 7 November (4,709 for the week before). This is above all 11 other Hub models available when it was run (horizon-0 US medians 4,322-5,279). Most of the rise comes from the network: with no tree correction the horizon-0 median is 5,213. The user chose to submit it.
- **Record:** interval PDFs and the peer comparison (Hub clone `57fefdf`) in `production/submissions/2026-11-14/covid/`. Making that comparison exposed a merged file (UGA_flucast-INFLAenza) whose rows carry another reference date. `production/peers.py` now skips such a file with a message instead of stopping.

### Reference date 7 November 2026

**First COVID submission.** [PR 2018](https://github.com/CDCgov/covid19-forecast-hub/pull/2018)
was opened at about 17:05 EST on 4 November from branch `submit-2026-11-07` of the fork
`jcblemai/covid19-forecast-hub` (commit `2197126`, "ACCIDDA-Chromantis 2026-11-07", no PR
description). Its first checks started about a minute before the metadata
([PR 2017](https://github.com/CDCgov/covid19-forecast-hub/pull/2017), branch
`metadata-chromantis`, deliberately short methods text) was merged at 17:05 EST, so
`metadata_exists` and the authorization check failed; every check on the file itself passed
(quantiles, samples coarser than the configured compound task set, submission window). Merging
the Hub's main into the branch (commit `c8dde3f`) re-ran the checks: Hub validation, the
designated-user authorization check and `approve-and-merge` passed, and it was merged at
17:19 EST on 4 November.

- **Not submitted:** horizon -1 (nowcast of the week ending 31 October) and Puerto Rico; both
  are optional, and the CovidHub-ensemble covers them.
- **Model:** release `production/releases/covid-gru-four-candidate-20261103.json` (40 fits,
  described under Current model, no refit), run with the `corrected` view on the 4 November
  operational panel `data/operational-20261104/processed/panel.npz`, SHA256
  `6486441cdc6ef06dbc6a5a9724a8841b196ca6b4ba0bf55cf5f64fcf2b162d7c` (the flu and RSV panel).
- **File:** `production/submissions/2026-11-07/covid/2026-11-07-ACCIDDA-Chromantis.parquet`,
  SHA256 `632ea80f92beb76ce33372e7d9235bd6a4968a01bd8c71331a4d23cd76047585`; the CSV beside it
  has the same rows. 23 quantiles and 200 sample trajectories per location and target,
  horizons 0–3, 52 locations, admissions and ED share.
- **Level:** US admissions medians 5,217; 5,562; 5,942; 6,333, after 4,540 reported for the
  week ending 31 October (4,122 the week before). When it was run, Emory-EpiRSI's US medians
  rose to 5,261 and UMass-ar6_pooled's to 5,489 at horizon 3.
- **Record:** interval PDFs and the peer comparison (Hub clone `46efdbf3`) in
  `production/submissions/2026-11-07/covid/`.
