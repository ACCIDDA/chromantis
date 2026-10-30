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
| Submitted | 24 and 31 October 2026 |
| Current model | 4-week model `r010_c08` (5 fits) spliced with full-season model `full_season_finalist_1` (5 fits) |
| Latest file | 31 October 2026, [PR 629](https://github.com/reichlab/flu-metrocast/pull/629), merged 29 October |
| What we submit | 103 locations, 100 trajectories from the reference date to 12 June 2027 |

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
not reported stay missing (on 28 October, New York City was one week and the 12 Georgia
locations two weeks behind the others), and the first forecast week is predicted directly.

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
