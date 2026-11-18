# Flu MetroCast

The [Flu MetroCast Hub](https://github.com/reichlab/flu-metrocast) collects local forecasts
of the percentage of emergency-department visits due to influenza. Most locations are Health
Service Areas from CDC's NSSP (single- or multi-county clusters that often match metropolitan
areas); New York City uses the city's EpiQuery syndromic data and North Carolina the state's
NC DPH system. Teams submit 100 sample trajectories per location, joint across horizons 0 to
3 weeks, and may add full-season trajectories to the end of the season. Forecasts are due
Wednesdays at 8 PM Eastern, from 21 October 2026 to 19 May 2027. Forecasts are evaluated in
real time with WIS, and a [pre-registered evaluation](https://osf.io/rc9dt/overview) is run at
the end of the season.

## Status

| Item | Value |
|---|---|
| Public model | ACCIDDA-Chromantis |
| Submitted | 24 and 31 October, 7, 14 and 21 November 2026 |
| Current model | 4-week model `r010_c08` (5 fits) spliced with full-season model `full_season_finalist_1` (5 fits) |
| Latest file | 21 November 2026, [PR 683](https://github.com/reichlab/flu-metrocast/pull/683), opened 18 November |
| What we submit | Flu ED %: 103 locations; California flu admissions: 7 locations (from 14 November). 100 trajectories to 12 June 2027 |

## Current model

Two models, five seeds (42–46) each, both trained on 2022–23 through 2025–26 (2026–27
excluded) on revised local ED histories, with labels the future local flu ED percentages:

- **Weeks 0–3:** `r010_c08`, an MLP that reads each location's history plus its own state's
  series through a shared encoder (logit ED, residual decoder, local noise, growth covariate
  encoder).
- **Weeks 4 to the end of the season:** `full_season_finalist_1`, an MLP with a 52-week
  history trained with a whole-path loss.

At each location the 4-week trajectory with the k-th largest week-3 value continues with the
full-season path that is k-th largest at the same week (`splice.py`). Neither model is
modified. No nowcast or revision correction is applied; missing weeks stay missing. The
fits run on Longleaf (`/hickory/proj/jlessler/projects/tapestry-all/metrocast-20261019`) with
`scripts/metrocast_submit_export.py`.

## Inputs and nowcast

| Input | `r010_c08` (weeks 0–3) | `full_season_finalist_1` (weeks 4 to end of season) |
|---|---|---|
| Histories read | 12 weeks of the location's flu ED percentage | 52 weeks of the location's flu ED percentage |
| Correction of the newest reported weeks | No | No |
| Other pathogens | No | No |
| Additional data (covariates) | Own state's flu ED percentage from the Hub's target data, as recent growth features; hidden in 25% of training episodes | The same, hidden in 10% of training episodes |
| Extra training data | None | None |
| Sharing across locations | None | None |
| Other features | Calendar, population | Calendar, smoothed multiscale features; no population |

**Nowcast.** None. Both models trained on revised histories and read the Hub's published
values as they are, without any artificial reporting errors or correction. Weeks a location has
not reported stay missing (on 4 November, New York City was one week and the 12 Georgia
locations three weeks behind the others), and the first forecast week is predicted directly.

**Not used.** No flu admissions, Kinsa or other outside source: MetroCast models read Hub data
only.

## How it was chosen

Tree search `metrocast-20261019` of about 270 recipes (11 rounds, about 1,200 fits), scored
by leave-one-season-out cross-validation over 2022–23 to 2025–26. 2025–26 was replayed on
the Hub archive version of each Wednesday deadline and compared with the actual MetroCast
ensemble. The 4-week winner's cross-validated WIS was 0.77 times that of the direct-MLP
reference; on 2025–26 it was 0.82 times the ensemble's WIS (location mean, 72 locations;
lower is better). It was selected as the best of many, so these numbers are optimistic.
There is no report page for this search yet; details are in the 24 October entry below.

## Submission log

Newest first.

### Reference date 21 November 2026

**ED unchanged; California anchored on the last observed week times NHSN growth.** [PR 683](https://github.com/reichlab/flu-metrocast/pull/683) was opened on 18 November 2026 at 16:11 EST from branch `submit-2026-11-21` of the fork `jcblemai/flu-metrocast` (commit `d45a940`, "ACCIDDA-Chromantis 2026-11-21", no PR description), based on the Hub's `main` of that afternoon (`f81fdcc`, after the "Weekly target-data update for 2026-11-18"). It adds the forecast file only.

- **ED models ("Flu ED visits pct"):** unchanged: `r010_c08` for weeks 0-3 and `full_season_finalist_1` after, five seeds each, trained on 2022-23 through 2025-26 local flu ED percentages, no refit, spliced at the week ending 12 December (`splice.py`). Panel `data/metrocast-20261118/panel.npz` on Longleaf (`--truth-day 2026-11-18`, SHA256 `42690402c9f21da1895bbb7b1c4320e27f19af091c321ac3538f55205d9223e5`): 102 of 103 locations through 14 November, one through 7 November. Week-0 median 1.24 times the last observation (observed growth into the week ending 14 November: 1.14, median over locations); median week-4/week-3 ratio at the join 1.97.
- **California models ("Flu hosp admits"):** the same 9 recipes x 5 seeds as 14 November (`metrocast-ca-prod`, trained on all weeks before 1 August 2026), reading the rebuilt panel through 7 November (Hub target data of 18 November and the CDPH dashboard of 18 November; SHA256 `383d09754279941943af06f0e401fa8abdb5e0961de6e8ca82cd30dbdb5c0a16`). Two changes in `scripts/export_metrocast_california.py`, both applied to the model output, not to training:
  - **Anchor (`--anchor 1 --growth 1.248`):** each fit's whole trajectories are multiplied, per location, so that the fit's week -1 median equals the last observed week times NHSN California growth into week -1 (NHSN, FluSight target data of 18 November: 1,407 for 7 November, 1,756 for 14 November). Reason: the 14 November file's week -1 scored 3.05 times the baseline (rank 6 of 7), all 7 observations above our median. Backtest on the four held-out seasons of `metrocast-ca-r03` (scores of the saved held-out quantiles, rescaled; mean WIS over weeks -1..3, 9 submitted recipes, lower is better): as is 56.5, half anchor on the last observed week 50.3, full anchor times NHSN growth 38.0; the NHSN version was the best of the rules tried in every season. The backtest used revised NHSN, so it is optimistic. The user approved the half anchor first, then the NHSN version when choosing between both files.
  - **Draws:** all 128 draws of every fit are pooled and 100 taken at random. Before, each fit gave 3 draws at indices seeded by its seed only, so the 45 fits used 5 index sets; this skewed the 14 November mixture (65% of draws below a level that each fit had at its median).
- **California forecast:** statewide median 1,486 at -1 (10-90%: 990-2,364), 1,523 at week 0, 1,574 at +3; Bay Area 420 and Los Angeles 362 at -1 (observed 7 November: 339 and 307). Full season to 12 June 2027 as committed on 14 November.
- **File:** `production/submissions/2026-11-21/metrocast/2026-11-21-ACCIDDA-Chromantis.parquet`, SHA256 `d69022b026c416f1487be97910ddddd7c0f4f3cc13a9402ec5bac4bf2a4e7699`. 330,700 sample rows: ED, 103 locations, 30 weeks (21 November 2026 to 12 June 2027), IDs S1-S100; California, 7 locations, 31 weeks (14 November 2026 to 12 June 2027), IDs S101-S200. The half-anchor alternative (not submitted) is in `california-half-anchor/`.
- **Past files, scored** (`score_metrocast.py`, against the 18 November data; pairwise relative WIS, 1 = epiENGAGE-baseline, lower is better). ED, all four files, weeks 0-3 observed: 0.691, rank 8 of 16 (DMAPRIME-ObsHYB 0.627, epiENGAGE-ensemble_short 0.676). By file: 24 October 0.605 (5 of 13), 31 October 0.586 (3 of 13), 7 November 0.720 (9 of 15), 14 November 1.130 (9 of 15, week 0 only). By week: 0.831 (10 of 16), 0.663 (6 of 15), 0.589 (4 of 13), 0.526 (3 of 13). Our week-0 medians were the highest of the models compared (median of forecast/observed 1.11, 0.92, 0.99, 1.14 by file); at weeks 1-3 all models were too low and we least. First reports of ED weeks are later revised by about +1% (median over locations). A whole-path anchor on the ED model was neutral in its held-out seasons (`scripts/anchor_ed_backtest.py` in `metrocast-20261019`), so ED was not changed.
- **Record:** `2026-11-21-ACCIDDA-Chromantis-metrocast-forecasts.pdf`, `perf.txt`, `perf-*.csv`, `merge.py`, `splice.py`, `california-nhsn/` and `california-half-anchor/` (export provenance), in the same folder. The Hub's 18 November `latest-data.csv` is not sorted by date; the PDF script now sorts it.

### Reference date 14 November 2026

**First California admissions forecast; ED forecast from the same two models as 7 November.** This week the NSSP data and the Hub's target-data update came a day late (Veterans Day); the Hub merged them on Thursday 12 November (`b5338e5`) and teams submitted that day. [PR 668](https://github.com/reichlab/flu-metrocast/pull/668) was opened on 12 November 2026 at 17:41 EST from branch `submit-2026-11-14` of the fork `jcblemai/flu-metrocast` (commit `c05d478`, "ACCIDDA-Chromantis 2026-11-14", no PR description), based on `b5338e5`. It adds the forecast file only. The first push failed Hub validation (`spl_mt_unique`): the ED and California rows both used sample IDs S1-S100, and the Hub requires each sample ID to belong to one target. Commit `4cf2c5b` renumbered the California trajectories S101-S200 (same paths); `write_samples` now does this.

- **ED models ("Flu ED visits pct"):** unchanged. The 4-week winner `r010_c08` and `full_season_finalist_1`, five seeds each, trained on 2022-23 through 2025-26 local flu ED percentages, no refit. Run on Longleaf on panel `data/metrocast-20261112/panel.npz` (`scripts/build_metrocast.py --truth-day 2026-11-12`, SHA256 `c169d1f7370f304081dd029764c02553a41a21ec3368dda68522b0076f8bcbc5`): 102 of 103 locations through 7 November, one through 31 October. Spliced at the week ending 5 December with the same rule (`splice.py`). The full-season model is steeper than the 4-week model at the join: median week-3 / last observation 2.93 against 1.97, so the median week-4/week-3 ratio is 1.9 (1.5 on 7 November).
- **California models ("Flu hosp admits", 6 CDPH regions and the state):** an equal mixture of 9 recipes, 5 seeds each (45 fits, 3 draws per fit, 100 of the 135 kept). Each fit was trained on the rebuilt California labels (private CDPH history October 2022 to September 2026 plus Hub target data from July 2026, statewide = Hub value or else the sum of regions) for all weeks before 1 August 2026 (experiment `metrocast-ca-prod`, Longleaf `/hickory/proj/jlessler/projects/tapestry-all/metrocast-ca-20261109`), and reads data through 31 October. Labels are future weekly admissions. The recipes are the 9 best of 18 in the four-season calibration `metrocast-ca-r03`: each of 2022-23 to 2025-26 held out in turn, mean WIS over the 7 locations at Hub weeks -1..3 (lower is better): `wide_cov_tp_state_ed_raw` 51.6, `ref_wide` 53.2, `wide_path` 53.9, `ref_log1p` 56.6, `ref_path` 56.9, `ref_ili` 57.8, `log1p_cov_tp_state` 57.9, `cov_tp_growth_drop0.25` 58.1, `wide_log1p` 58.4. The mixture itself was not scored. Exported with `scripts/export_metrocast_california.py`.
- **Why a 9-recipe mixture:** the recipes disagree widely one week out. Statewide medians for the week ending 7 November (Hub horizon -1) range from 573 to 2,181 across the 18 recipes, against 1,170 observed on 31 October. The top two alone gave 1,755 and 2,181, while NHSN California flu admissions (a different series that matched the Hub closely: 1,181 and 1,223 against 1,166 and 1,170 on 24 and 31 October) were flat at 1,225 on 7 November. The mixture was chosen by calibration rank, not by agreement with NHSN. The three-recipe mixture prepared on 11 November (`cov_tp_state_ed_raw`, `log1p_cov_tp_state`, `ref_wide`, chosen on the old dashboard labels and one held-out season) was not submitted.
- **California forecast:** statewide median 931 at -1 (10-90%: 497-2,348), 1,243 at +3; Bay Area 221 at -1 against 287 observed on 31 October. Over the full season, statewide median peak 1,774 (10-90%: 1,170-5,293; past four peaks 1,800-4,599), median peak week 5 December, median season total 25,449 (past 15,883-47,761). Medians of the peak in Los Angeles (428) and Southern California (530) are below every past season. All 32 weeks were submitted at the user's request, so California full-season trajectories are now due every week.
- **File:** `production/submissions/2026-11-14/metrocast/2026-11-14-ACCIDDA-Chromantis.parquet`, SHA256 `a17f9d74b4d15d602e4b48aafc0ae6ce32ad4c84aeb495a9581e82f61378f8c1`. 341,700 sample rows: ED, 103 locations, 31 weeks (14 November 2026 to 12 June 2027); California admissions, 7 locations, 32 weeks (7 November 2026 to 12 June 2027). 100 trajectories per target and location (sample IDs S1-S100 for ED, S101-S200 for California); same Parquet schema as 7 November.
- **Past files, scored:** all three ED files (24 October, 31 October, 7 November), every week 0-3 observed by 12 November. WIS from 100 samples turned into the 23 Hub quantiles; pairwise relative WIS, 1 = epiENGAGE-baseline, lower is better. All three together: 0.660, rank 7 of 15 (DMAPRIME-QR_E 0.607, epiENGAGE-ensemble_short 0.641). By file: 24 October 0.656 (rank 6 of 13), 31 October 0.595 (3 of 13), 7 November 0.749 (11 of 15, week 0 only so far). By week: week 0 0.720 (9 of 15), week 1 0.619 (4 of 13), week 2 0.609 (5 of 13). Script `score_past.py`.
- **Record:** `2026-11-14-ACCIDDA-Chromantis-metrocast-forecasts.pdf` (scores, California, ED pages), `past-scores*.csv`, `california/` (export provenance), in the same folder.

### Reference date 7 November 2026

**Same two models and splice rule as 31 October, run on the 4 November Hub data.** [PR 645](https://github.com/reichlab/flu-metrocast/pull/645) was opened on 4 November 2026 at 16:59 EST, before the 8 PM ET deadline, from branch `submit-2026-11-07` of the fork `jcblemai/flu-metrocast` (commit `217cb7b3`, "ACCIDDA-Chromantis 2026-11-07", no PR description), based on the Hub's `main` of that afternoon (`c35e4f89`). It adds the forecast file only. Hub validation passed.

- **Models:** the 4-week winner `r010_c08` (experiment `metrocast-submit-winner`) and `full_season_finalist_1` (experiment `metrocast-submit-fullseason`), five seeds (42-46) each, as described in the 24 October entry. No refit: the saved fits were run on Longleaf (`srun`, partition `general`) with `scripts/metrocast_submit_export.py --panel`. The job needs `PYTHONPATH=src:scripts`; the first attempt without it failed on import.
- **Training and labels:** unchanged; 2022-23 through 2025-26, future local flu ED percentages, 2026-27 excluded.
- **Operational inputs:** Hub target data at commit `c35e4f89` (4 November 2026, after the 17:44 UTC "Weekly target-data update for 2026-11-04"), panel `data/metrocast-20261104/panel.npz` on Longleaf (`scripts/build_metrocast.py --truth-day 2026-11-04`, SHA256 `f66b67993c277f2defd6c9e0361bf0011672c4a9c2f875e585c8d4e2fcfeb62a`), 103 locations. 90 locations run through 31 October, NYC through 24 October and the 12 Georgia locations through 10 October (three weeks behind). Missing weeks stay missing; no nowcast or revision correction.
- **Splice:** same rule as 31 October (`splice.py`), with the join at the week ending 28 November. The full-season run gives 33 weeks (to 19 June 2027); the splice cuts it at the Hub's last target week, 12 June 2027, so this file has 32 weeks. Median week-4/week-3 ratio 1.5 (0.93 on 31 October, 0.73 on 24 October): at the join both models are about 2.4 times the last observation (4-week 2.47, full-season 2.37, medians across locations), and the full-season model keeps growing, to 3.3 times at week 4 and 4.9 times by mid-December.
- **File:** `production/submissions/2026-11-07/metrocast/2026-11-07-ACCIDDA-Chromantis.parquet`, SHA256 `64b1a49cb117b69b468c3f352d74090fff70183bea84c51bc4eeac0440b042ef`. 329,600 sample rows: 100 trajectories shared across weeks and locations, 32 weeks (7 November 2026 to 12 June 2027), 103 locations; same columns and types as the merged 31 October file. Median over locations of the median peak: 10.2% of ED visits (10.2% on 31 October), median peak week 19 December; median season total 84 (sum of weekly %). Week-0 median 1.47 times the last observation, week 3 2.46 times.
- **Last week's file, scored:** WIS from 100 samples turned into the 23 Hub quantiles, against the 4 November target data, divided by epiENGAGE-baseline's on the same tasks (lower is better). The 31 October file at horizon 0: 0.56. The 24 October file: 0.92 at horizon 0, 0.62 at horizon 1. Pairwise relative WIS over both files: 0.655 (rank 2 of 13; epiENGAGE-ensemble_short 0.676, DMAPRIME-ObsHYB 0.638); on the week ending 31 October alone, 0.592 (rank 1 of 13). Same one-off script as for flu.
- **Comparison:** against the one other 7 November submission available at about 16:00 EST, UMass-SAR (open PR 639, 70 locations): its week-0 median is 1.24 times the last observation and week 3 2.19 times (ours 1.47 and 2.46); median peak 7.8% in the week of 16 January (ours 10.2%, 19 December). `model-comparison.csv` and page 2 of `2026-11-07-ACCIDDA-Chromantis-metrocast-flu-ed-forecasts.pdf` in the same folder; the peer file stays in `production/output/2026-11-04/metrocast/others/`.

### Reference date 31 October 2026

**Same two models and splice as 24 October, run on the 28 October Hub data.** [PR 629](https://github.com/reichlab/flu-metrocast/pull/629) was opened on 28 October 2026 at 18:27 EDT, before the 8 PM ET deadline, from branch `submit-2026-10-31` of the fork `jcblemai/flu-metrocast` (commit `6293da51`, "ACCIDDA-Chromantis 2026-10-31"), based on the Hub's `main` of that evening. It adds the forecast file only (the metadata was merged with PR 609). Hub validation passed; merged on 29 October 2026 at 11:09 EDT. The fork's local clone is `production/hubs/flu-metrocast-fork` (sparse: our model folders only).

- **Models:** the 4-week winner `r010_c08` (experiment `metrocast-submit-winner`) and `full_season_finalist_1` (experiment `metrocast-submit-fullseason`), five seeds (42-46) each, as described in the 24 October entry. No refit: the saved fits were run on Longleaf (one CPU job, partition `general`) with `scripts/metrocast_submit_export.py`, which gained a `--panel` option on 28 October so that weekly reruns read the new panel instead of the one recorded at fitting time. This change exists only in the Longleaf working copy (`/hickory/proj/jlessler/projects/tapestry-all/metrocast-20261019`).
- **Training and labels:** unchanged; 2022-23 through 2025-26, future local flu ED percentages, 2026-27 excluded.
- **Operational inputs:** Hub target data at commit `445d17d0` (28 October 2026, 18:21 UTC, "Weekly target-data update for 2026-10-28"), panel `data/metrocast-20261028/panel.npz` on Longleaf (SHA256 prefix `48afa2aa4e8358e4`), 103 locations. 90 locations run through 24 October, NYC through 17 October, and the 12 Georgia locations through 10 October (two weeks behind, one week on 21 October). Missing weeks stay missing; no nowcast or revision correction.
- **Splice:** same rule as 24 October (`splice.py`), with the join at the week ending 21 November. The full-season model ran closer to the 4-week model this week: median week-4/week-3 ratio 0.93 (0.73 on 24 October).
- **File:** `production/submissions/2026-10-31/metrocast/2026-10-31-ACCIDDA-Chromantis.parquet`, SHA256 `07fe90612c1aa39947416dacad3ae103f284e9e634e1e54bc1110d4c5f4c7279`. 339,900 sample rows: 100 trajectories shared across weeks and locations, 33 weeks (31 October 2026 to 12 June 2027), 103 locations. Median over locations of the median peak: 10.2% of ED visits (9.9% on 24 October), median peak week 26 December; median season total 87 (sum of weekly %).
- **Last week's file, checked:** for the week ending 24 October (90 locations observed), the 24 October file's median was 1.21 times the observed value (median across locations), while observed values grew 1.23 times per week over the previous two weeks. The observation fell inside the 80% interval in 76 locations and below it in 10. No WIS was computed.
- **Comparison:** against the seven other 31 October submissions available at about 18:45 EDT, all from open PRs (CU-NeuralWalkODE, DMAPRIME-ObsHYB, UMass-SAR, UT-GBQR, VTSanghani-PRIME, epiENGAGE-baseline, epiENGAGE-renewal_rt). Our week-0 median is 1.49 times the last observation (median across locations), the highest; the others give 1.03-1.31. At week 3, 2.57 times (DMAPRIME-ObsHYB 2.67, others 1.00-2.43). `model-comparison.csv` and page 2 of `2026-10-31-ACCIDDA-Chromantis-metrocast-flu-ed-forecasts.pdf` in the same folder; the downloaded peer files stay in `production/output/2026-10-28/metrocast/others/`.


### Reference date 24 October 2026

**First Flu MetroCast submission.** [PR 609](https://github.com/reichlab/flu-metrocast/pull/609) was opened on 21 October 2026 at about 20:15 EDT, after the 8 PM ET deadline, from the fork `jcblemai/flu-metrocast` `main` (commit `bc448be3`, "ACCIDDA-Chromantis 2026-10-24"). It adds `model-metadata/ACCIDDA-Chromantis.yml` and the forecast. The first push failed Hub validation only because the date columns were strings; commit `b939780` stores them as Parquet dates (the exporter now does this). Commit `ac334bd` replaced the 4-week file with the spliced full-season file and set `long_term_forecasts: true`; validation passed. Merged on 22 October 2026 at 09:11 EDT.

- **Model:** season-CV winner `r010_c08`: `ed_transform=logit,decoder=residual2,decoder_blocks=2,noise=local,latent=32,width=128,epochs=160,members=32,weight_decay=0.001,covariate_encoder=growth,covariate_set=state,input_normalization=b0,covariate_dropout=0.25`. Each location's history plus its own state's series through a shared encoder; latest history week visible in training. Five seeds (42-46), experiment `metrocast-submit-winner` on Longleaf (`/hickory/proj/jlessler/projects/tapestry-all/metrocast-20261019`).
- **Training:** 2022-23 through 2025-26 seasons, labels are future local flu ED percentages (2026-27 excluded). Revised histories.
- **Selection:** tree search of about 270 recipes (11 rounds, ~1,200 fits) scored by leave-one-season-out CV over 2022-23..2025-26. 2025-26 was replayed on the Hub archive version of each Wednesday deadline (which holds the Saturday four days earlier) against the actual MetroCast ensemble; other seasons used revised histories. CV WIS 0.77 x the direct-MLP reference; on 2025-26, 0.82 x the ensemble's WIS (location mean, 72 locations; lower is better). Selected as the best of many, so optimistic. The earlier confirmation that used archive versions strictly before Wednesday dropped the latest week for our models only, and is superseded.
- **Operational inputs:** Hub target data at commit `1ffeb2f8` (21 October 2026, through 17 October; NYC through 10 October), panel `data/metrocast-20261021/panel.npz` (SHA256 prefix `c63fc5834fe82cd5`), 103 locations including the 13 Utah districts and NYC. No nowcast or revision correction.
- **Full-season model (weeks 4-33):** `full_season_finalist_1`, a 52-week-history MLP with a whole-path loss (`lookback=52,geography=0,decoder=residual2,decoder_blocks=2,noise=local,epochs=320,batch_size=2,members=16,lr=0.002,covariate_encoder=growth,signal_features=smooth_multiscale,covariate_set=state,input_normalization=b0,path_loss_weight=1.0,covariate_dropout=0.1`), latest week visible. Five seeds, experiment `metrocast-submit-fullseason`, same training seasons, labels and panel. Lowest 2025-26 WIS of four full-season candidates at horizons 4-12 (2.13 percentage points) and 13-25 (0.83), revised inputs; no ensemble or baseline exists for these horizons.
- **Splice:** at each location the 4-week trajectory with the k-th largest 14 November value continues with the full-season path that is k-th largest at its own 14 November; both models unmodified (`splice.py`). The full-season model runs about 40% below the 4-week model, so trajectories drop at the join (median week-4/week-3 ratio 0.73).
- **File:** `production/submissions/2026-10-24/metrocast/2026-10-24-ACCIDDA-Chromantis-submitted.parquet` (Hub name `2026-10-24-ACCIDDA-Chromantis.parquet`), SHA256 `65b23872c898acc74f5c6115998f615f7fe0a0668d7c97a55771c2a34c50a66d`. 350,200 sample rows: 100 trajectories shared across weeks and locations, 34 weeks (24 October 2026 to 12 June 2027), 103 locations. The 4-week-only version is in `superseded/`. Median peak 9.9% of ED visits around 2 January, season total 86 (sum of weekly %), within the range of past seasons and the other three full-season submissions this round (`model-comparison.csv`, PDF page 2).
