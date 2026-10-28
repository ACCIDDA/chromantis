# Chromantis submission log

See [Description and hub rules](reference/hub-scoring-2026-2027.md) for the three hubs' targets, submission formats, and scoring rules for 2026–27.

Chromantis records submissions across all pathogens and model recipes. Each dated entry identifies the pathogen, Hub, public model name, exact fitted recipe, training and operational inputs, submitted file, and publication status. Future recipes receive new entries; a change of model does not rename or overwrite the submission history.

The Hub model is **ACCIDDA-Chromantis**. It was submitted as ACCIDDA-EpiLoom for the 10 October 2026 round and renamed on the Hub on 8 October 2026 (PR 3774); the file contents did not change. RSV has been submitted to the RSV Hub since 17 October 2026, under the same public name. For 24 October, the influenza weekly targets switched from Bes back to the B7 recipes. COVID-19 has not been submitted yet.

Each entry must state: the recipe and its exact fitted checkpoints, the training seasons and training-input treatments, the prediction labels, the operational input panel (with hash), the submitted file hash, and the Hub PR, validation and merge record. The local record of each issuance is `production/submissions/<reference date>/` (FluSight) or `<reference date>/<hub>/` (other Hubs): the submitted CSV under its Hub name, its export record (`.json`: release, sources, hashes), the interval PDFs and the peer-comparison PDF drawn at submission time (`python -m chromantis.production record`); replaced versions are in its `superseded/` subfolder.

On 14 October 2026 (evening) every recorded peer comparison was redrawn to show every same-week Hub model individually, plus open-PR submissions: FluSight Hub `50898478` (55 models for 10 October, 39 for 17 October) and RSV Hub `8dd45ebb` (12 models). The earlier versions showed six fixed peers and a band over the rest. The 17 October flu comparison does not repeat the model description because the submitted CSV now includes peak targets and no longer matches its weekly-only export record.

| Pathogen | Reference date | Public model | Recipe | Recorded status |
| --- | --- | --- | --- | --- |
| Influenza | 31 October 2026 | ACCIDDA-Chromantis | B7 refit `b7-20261009` weekly targets (30 fits) + Peak8 season-peak targets (6 fits) | PR 3943 open, Hub validation passed |
| Influenza | 24 October 2026 | ACCIDDA-Chromantis | B7 refit `b7-20261009` weekly targets (30 fits) + Peak8 season-peak targets (6 fits) | PR 3895 merged 21 October |
| Influenza | 17 October 2026 | ACCIDDA-Chromantis | Bes weekly targets (10 fits) + Peak8 season-peak targets (6 fits) | Weekly file merged (PR 3804); peak targets added in PR 3815, merged 14 October |
| Influenza | 10 October 2026 | ACCIDDA-Chromantis (submitted as ACCIDDA-EpiLoom) | Three-recipe B7 mixture, 30 fits | Merged after the deadline; replaced the on-time eight-recipe forecast |
| Influenza (MetroCast) | 31 October 2026 | ACCIDDA-Chromantis | Same two models as 24 October, same splice | PR 629 open, Hub validation passed |
| Influenza (MetroCast) | 24 October 2026 | ACCIDDA-Chromantis | Season-CV winner `r010_c08` (5 fits) for horizons 0-3, spliced with full-season `full_season_finalist_1` (5 fits) to 12 June | First MetroCast submission; metadata and forecast in PR 609, opened after the deadline, merged 22 October |
| COVID-19 | — | — | — | No submission entered in this log yet |
| RSV | 31 October 2026 | ACCIDDA-Chromantis | Four-recipe mixture rsv-four-20261014, 40 fits | PR 673 merged 28 October |
| RSV | 24 October 2026 | ACCIDDA-Chromantis | Four-recipe mixture rsv-four-20261014, 40 fits | PR 657 merged 21 October |
| RSV | 17 October 2026 | ACCIDDA-Chromantis | Four-recipe mixture rsv-four-20261014, 40 fits | First RSV submission; metadata and forecast in PR 641, merged 15 October |

Hub metadata changes are deferred until the recipe is settled, as decided on 8 October 2026.

From 31 October, `production/submissions/<reference date>/shared-pdfs/` collects every PDF of the submitted files (interval PDFs, peer comparisons, season peak, MetroCast forecasts) in one folder for sharing.

## MetroCast reference date 31 October 2026

**Same two models and splice as 24 October, run on the 28 October Hub data.** [PR 629](https://github.com/reichlab/flu-metrocast/pull/629) was opened on 28 October 2026 at 18:27 EDT, before the 8 PM ET deadline, from branch `submit-2026-10-31` of the fork `jcblemai/flu-metrocast` (commit `6293da51`, "ACCIDDA-Chromantis 2026-10-31"), based on the Hub's `main` of that evening. It adds the forecast file only (the metadata was merged with PR 609). Hub validation passed; merge is not yet recorded. The fork's local clone is `production/hubs/flu-metrocast-fork` (sparse: our model folders only).

- **Models:** the 4-week winner `r010_c08` (experiment `metrocast-submit-winner`) and `full_season_finalist_1` (experiment `metrocast-submit-fullseason`), five seeds (42-46) each, as described in the 24 October entry. No refit: the saved fits were run on Longleaf (one CPU job, partition `general`) with `scripts/metrocast_submit_export.py`, which gained a `--panel` option on 28 October so that weekly reruns read the new panel instead of the one recorded at fitting time. This change exists only in the Longleaf working copy (`/hickory/proj/jlessler/projects/tapestry-all/metrocast-20261019`).
- **Training and labels:** unchanged; 2022-23 through 2025-26, future local flu ED percentages, 2026-27 excluded.
- **Operational inputs:** Hub target data at commit `445d17d0` (28 October 2026, 18:21 UTC, "Weekly target-data update for 2026-10-28"), panel `data/metrocast-20261028/panel.npz` on Longleaf (SHA256 prefix `48afa2aa4e8358e4`), 103 locations. 90 locations run through 24 October, NYC through 17 October, and the 12 Georgia locations through 10 October (two weeks behind, one week on 21 October). Missing weeks stay missing; no nowcast or revision correction.
- **Splice:** same rule as 24 October (`splice.py`), with the join at the week ending 21 November. The full-season model ran closer to the 4-week model this week: median week-4/week-3 ratio 0.93 (0.73 on 24 October).
- **File:** `production/submissions/2026-10-31/metrocast/2026-10-31-ACCIDDA-Chromantis.parquet`, SHA256 `07fe90612c1aa39947416dacad3ae103f284e9e634e1e54bc1110d4c5f4c7279`. 339,900 sample rows: 100 trajectories shared across weeks and locations, 33 weeks (31 October 2026 to 12 June 2027), 103 locations. Median over locations of the median peak: 10.2% of ED visits (9.9% on 24 October), median peak week 26 December; median season total 87 (sum of weekly %).
- **Last week's file, checked:** for the week ending 24 October (90 locations observed), the 24 October file's median was 1.21 times the observed value (median across locations), while observed values grew 1.23 times per week over the previous two weeks. The observation fell inside the 80% interval in 76 locations and below it in 10. No WIS was computed.
- **Comparison:** against the seven other 31 October submissions available at about 18:45 EDT, all from open PRs (CU-NeuralWalkODE, DMAPRIME-ObsHYB, UMass-SAR, UT-GBQR, VTSanghani-PRIME, epiENGAGE-baseline, epiENGAGE-renewal_rt). Our week-0 median is 1.49 times the last observation (median across locations), the highest; the others give 1.03-1.31. At week 3, 2.57 times (DMAPRIME-ObsHYB 2.67, others 1.00-2.43). `model-comparison.csv` and page 2 of `2026-10-31-ACCIDDA-Chromantis-metrocast-flu-ed-forecasts.pdf` in the same folder; the downloaded peer files stay in `production/output/2026-10-28/metrocast/others/`.

## Operational inputs, issuance 28 October 2026 (reference date 31 October)

The flu and RSV forecasts for 31 October read one operational data root, `data/operational-20261028/`: a copy of the 21 October root with fresh pulls on 28 October 2026 between 20:28 and 20:39 UTC (16:28-16:39 EDT) of Delphi NHSN, Delphi NSSP, the FluSight, RSV and COVID Hub target histories, and PopHIVE Kinsa. Other sources are the 14 October snapshots. The Hubs had posted the week ending 24 October between 11:20 and 12:32 EDT that day; Delphi NHSN and NSSP both reached that week. Panels:

- Influenza: `data/operational-20261028/processed/panel.npz`, SHA256 `af38b52146df5d476ab2c2009267885e9d7c5b3b0dc3c320bf08128277073f71`.
- RSV: `panel-rsv.npz` in the same folder, NHSN RSV admissions before 2024-11-02 masked as in training, SHA256 `9506578ad5fdfadcb1dc312332d4949f763d882bade2be8f2f5e2b8ea3f32698`.

The FluSight Hub's target data has no ED share for Iowa, Georgia and Delaware for the week ending 24 October. Unlike 21 October, the panel was not checked cell by cell against the Hubs' latest target data.

## Influenza reference date 31 October 2026

**Same B7 + Peak8 model as 24 October**, chosen over Bes on the user's decision on 28 October. [PR 3943](https://github.com/cdcepi/FluSight-forecast-hub/pull/3943) was opened at 18:26 EDT from branch `submit-2026-10-31` of the fork (commit `519b0f38`, "ACCIDDA-Chromantis 2026-10-31", no PR description), based on the Hub's `main` of that evening. Hub validation (`validate-submission`) passed; merge is not yet recorded.

- **Why B7 rather than Bes:** both recipes raise the two newest admission and ED weeks with correction trees saved with each fit. Run on the four 2026-27 issuances (7-28 October), summed over states and DC, B7's trees raise the newest admission week 1.095-1.104 times and Bes's 1.131-1.141 times. Those weeks have since been revised 1.054-1.070 times after one to three weeks. In November-December 2025 (the archive holds no 2025-26 first reports before the 12 November issuance), national first reports were revised up 3-10% after one week and ended 8-16% above first report; 2026-27 first reports have been revised up 5.3-5.4% after one week. B7's correction matches that pattern; Bes's over-corrects admissions by about 4 points. B7's US week-0 median is about 1.24 times its corrected last week, close to recent observed growth (about 1.23 per week); Bes's is about 1.39 times. ED revisions (1-3% after one week) were similar in both seasons. These are four issuances with incomplete revisions, not a scored comparison. The unsubmitted Bes file is in `production/output/2026-10-28/bes-20261010/`, with `bes-vs-b7/`.
- **Weekly model:** release `production/releases/b7-20261009.json`, the B7 three recipes as in the 24 October entry (30 fits, trained on 2022-23 through 2025-26 with the prescribed 2025-26 reporting errors, labels latest finalized future flu admissions and ED share). No refit: the saved fits were run on the 28 October reports, newest two admission and ED weeks corrected by each fit's saved trees (`corrected` view). Equal weight per recipe and per seed; predictive distributions mixed.
- **Peak model:** the same Peak8 release and six fits (`production/releases/peak-20261014.json`), run on the same 28 October panel with 6,000 season paths. US peak size median 34,722 admissions (5-95%: 22,192-52,538); peak week median 19 December 2026 (10-90%: 28 November 2026 to 9 January 2027).
- **Last week's file, scored:** the 24 October file at horizon 0, against the first report for the week ending 24 October. US admissions median 6,200 against 6,006 observed. On the 51 state/DC tasks, its mean WIS divided by FluSight-baseline's was 0.66 on log admissions (rank 13 of 58 models; FluSight-ensemble 0.66) and 0.63 on counts (rank 4 of 58; ensemble 0.64). On ED share, scored on the 48 states with an observation where the baseline forecast (FluSight-baseline has no Iowa ED forecast), 0.68 (rank 10 of 17; ensemble 0.59). Lower is better. Scored with a one-off script (WIS = twice the mean pinball loss over the 23 quantiles), not the research scorer.
- **File:** `production/submissions/2026-10-31/2026-10-31-ACCIDDA-Chromantis.csv`, SHA256 `7c838548d95bdf0bedd1336eceea4bcc4f13150d30ed6a37e82b14017f98eac8`, 12,532 rows: 9,568 weekly quantile rows (52 locations, no Puerto Rico; horizons 0-3; admissions and ED share) followed by 2,964 peak rows. US admissions medians: 8,183; 9,804; 12,196; 15,270 in horizon order, at the 76th, 76th, 65th and 65th percentile of the 17 Hub models available when it was run; the US ED-share medians were above all 4 available. Local checks passed: no quantile crossing, integer weekly counts, ED at most 0.160, correct target dates, peak-week probabilities summing to one. The export record (`.json`) describes the weekly part only.
- **Record:** interval PDFs, the peer comparison (Hub clone `9a18c654`, 37 same-week models) and the season-peak PDF with its manifest are in `production/submissions/2026-10-31/`.

## RSV reference date 31 October 2026

**Same model as 24 October.** [PR 673](https://github.com/CDCgov/rsv-forecast-hub/pull/673) was opened at 18:27 EDT from branch `submit-2026-10-31` of the fork (commit `582d152a`, "ACCIDDA-Chromantis 2026-10-31", no PR description). Hub validation, the designated-user authorization check and the `approve-and-merge` job passed; it was merged at 18:34 EDT on 28 October.

- **Model:** release `production/releases/rsv-four-20261014.json`, the four-recipe mixture described in the 17 October entry (40 fits, trained on 2022-23 through 2025-26, no refit), run on the 28 October RSV panel with the `corrected` view.
- **Last week's file, scored:** the 24 October file at horizon 0, against the first report for the week ending 24 October. US admissions median 1,068 against 874 observed. On the 51 state/DC tasks, its mean WIS divided by RSVHub-baseline's was 0.94 on log admissions (rank 5 of 11; RSVHub-ensemble 0.87) and 1.24 on counts (rank 8; ensemble 1.07); on ED share 1.24 (rank 3 of 3; ensemble 1.00). Lower is better. Same one-off script as for flu.
- **File:** `production/submissions/2026-10-31/rsv/2026-10-31-ACCIDDA-Chromantis.parquet`, SHA256 `f86c4d062840b47f336ecedcb511aec8c3ddd422b36898f80602a3aed52b7409`; the CSV beside it has the same rows. Quantiles and 200 sample trajectories per location, horizons 0-3, 52 locations, admissions and ED share. US admissions medians: 1,221; 1,472; 1,769; 2,148, at the 67th percentile of the 6 Hub models available when it was run.
- **Record:** interval PDFs and the peer comparison (Hub clone `63bb1955`, 8 same-week models) in `production/submissions/2026-10-31/rsv/`.

## MetroCast reference date 24 October 2026

**First Flu MetroCast submission.** [PR 609](https://github.com/reichlab/flu-metrocast/pull/609) was opened on 21 October 2026 at about 20:15 EDT, after the 8 PM ET deadline, from the fork `jcblemai/flu-metrocast` `main` (commit `bc448be3`, "ACCIDDA-Chromantis 2026-10-24"). It adds `model-metadata/ACCIDDA-Chromantis.yml` and the forecast. The first push failed Hub validation only because the date columns were strings; commit `b939780` stores them as Parquet dates (the exporter now does this). Commit `ac334bd` replaced the 4-week file with the spliced full-season file and set `long_term_forecasts: true`; validation passed. Merged on 22 October 2026 at 09:11 EDT.

- **Model:** season-CV winner `r010_c08`: `ed_transform=logit,decoder=residual2,decoder_blocks=2,noise=local,latent=32,width=128,epochs=160,members=32,weight_decay=0.001,covariate_encoder=growth,covariate_set=state,input_normalization=b0,covariate_dropout=0.25`. Each location's history plus its own state's series through a shared encoder; latest history week visible in training. Five seeds (42-46), experiment `metrocast-submit-winner` on Longleaf (`/hickory/proj/jlessler/projects/tapestry-all/metrocast-20261019`).
- **Training:** 2022-23 through 2025-26 seasons, labels are future local flu ED percentages (2026-27 excluded). Revised histories.
- **Selection:** tree search of about 270 recipes (11 rounds, ~1,200 fits) scored by leave-one-season-out CV over 2022-23..2025-26. 2025-26 was replayed on the Hub archive version of each Wednesday deadline (which holds the Saturday four days earlier) against the actual MetroCast ensemble; other seasons used revised histories. CV WIS 0.77 x the direct-MLP reference; on 2025-26, 0.82 x the ensemble's WIS (location mean, 72 locations; lower is better). Selected as the best of many, so optimistic. The earlier confirmation that used archive versions strictly before Wednesday dropped the latest week for our models only, and is superseded.
- **Operational inputs:** Hub target data at commit `1ffeb2f8` (21 October 2026, through 17 October; NYC through 10 October), panel `data/metrocast-20261021/panel.npz` (SHA256 prefix `c63fc5834fe82cd5`), 103 locations including the 13 Utah districts and NYC. No nowcast or revision correction.
- **Full-season model (weeks 4-33):** `full_season_finalist_1`, a 52-week-history MLP with a whole-path loss (`lookback=52,geography=0,decoder=residual2,decoder_blocks=2,noise=local,epochs=320,batch_size=2,members=16,lr=0.002,covariate_encoder=growth,signal_features=smooth_multiscale,covariate_set=state,input_normalization=b0,path_loss_weight=1.0,covariate_dropout=0.1`), latest week visible. Five seeds, experiment `metrocast-submit-fullseason`, same training seasons, labels and panel. Lowest 2025-26 WIS of four full-season candidates at horizons 4-12 (2.13 percentage points) and 13-25 (0.83), revised inputs; no ensemble or baseline exists for these horizons.
- **Splice:** at each location the 4-week trajectory with the k-th largest 14 November value continues with the full-season path that is k-th largest at its own 14 November; both models unmodified (`splice.py`). The full-season model runs about 40% below the 4-week model, so trajectories drop at the join (median week-4/week-3 ratio 0.73).
- **File:** `production/submissions/2026-10-24/metrocast/2026-10-24-ACCIDDA-Chromantis-submitted.parquet` (Hub name `2026-10-24-ACCIDDA-Chromantis.parquet`), SHA256 `65b23872c898acc74f5c6115998f615f7fe0a0668d7c97a55771c2a34c50a66d`. 350,200 sample rows: 100 trajectories shared across weeks and locations, 34 weeks (24 October 2026 to 12 June 2027), 103 locations. The 4-week-only version is in `superseded/`. Median peak 9.9% of ED visits around 2 January, season total 86 (sum of weekly %), within the range of past seasons and the other three full-season submissions this round (`model-comparison.csv`, PDF page 2).

## Operational inputs, issuance 21 October 2026 (reference date 24 October)

Both 24 October forecasts read one operational data root, `data/operational-20261021/`: a copy of the 14 October root with fresh pulls on 22 October 2026 between 00:13 and 00:29 UTC (20:13-20:29 EDT on 21 October) of Delphi NHSN, Delphi NSSP, the FluSight, RSV and COVID Hub target histories, and PopHIVE Kinsa. Other sources are the 14 October snapshots. Panels:

- Influenza: `data/operational-20261021/processed/panel.npz`, SHA256 `05f983687c7da5a2e5db6832f96a37614762eab4602bb3b3f6fa72f02dc2a547`.
- RSV: `panel-rsv.npz` in the same folder, the same panel with NHSN RSV admissions before 2024-11-02 masked as in training, SHA256 `a29b957449d8228291ed7c429d79f0e4e04056392daf7aae83c9e4ab05c67639`.

For every location and the 8 weeks through 17 October, the admissions and ED values seen at the 21 October issuance equal each Hub's latest target data. The only empty cells are empty on the Hub too: the FluSight Hub's 21 October "Remove suppressed data" commit (16:21 EDT) removed Iowa ED share again for the weeks ending 29 August to 10 October, and Delaware ED share for the week ending 17 October is missing. The same Iowa and Delaware gaps are in the RSV ED share.

## Influenza reference date 24 October 2026

**B7 refit submitted instead of Bes**, on the user's decision on 21 October. [PR 3895](https://github.com/cdcepi/FluSight-forecast-hub/pull/3895) was opened at 21:11 EDT from branch `submit-2026-10-24` of the fork (commit `d7c27a5e`, "ACCIDDA-Chromantis 2026-10-24"), based on the Hub's `main` of that evening. Hub validation (`validate-submission`) passed; merged at 21:47 EDT the same evening.

- **Why the switch:** the Bes file submitted for 17 October forecast too high. For the week ending 17 October (first report), its US admissions median was 5,762 against 4,698 observed (FluSight-ensemble: 4,831). On the 51 state/DC tasks of horizon 0, its mean WIS divided by FluSight-baseline's was 0.76 on log admissions (rank 37 of 56 models), 0.78 on counts (rank 39) and 1.21 on ED share (rank 16 of 16; lower is better). The B7 refit below, run on the same 14 October panel but not submitted, would have scored 0.70 (rank 21), 0.66 (rank 11) and 0.86 (rank 11); the FluSight-ensemble scored 0.65, 0.65 and 0.76. The B7 file submitted for 10 October, scored on its horizons 0-1, ranked 6 of 48 on log admissions (0.59, ensemble 0.58). For 24 October, Bes's US median was 7,216, the highest of 50 Hub models (peer median 5,678); the B7 refit gave 6,200 (76th percentile). This is one scored week and is noisy: over the held-out seasons of the 10 October tree search, Bes scored better than B7 (0.2895 against 0.2976 state/DC log-admission WIS). The unsubmitted Bes file for 24 October is in `production/output/2026-10-21/bes-20261010/`.
- **Weekly model:** release `production/releases/b7-20261009.json`, the B7 three recipes (`A_blocks3`, `B5_confirmed_candidate_1`, `B_width256`, see the 10 October entry) retrained on 9 October 2026 with the current code, seeds 42-51 each, 30 fits. Same recipes, seeds, training panel and treatments as the B7 checkpoints submitted for 10 October (`b7-20261007`), which no longer load. Trained on 2022-23 through 2025-26 with no held-out season; training admission and ED histories made preliminary with the prescribed 2025-26 reporting errors; labels are latest finalized future flu admissions and ED share (September 2026 panel). No refit this week: the saved fits were run on the 21 October reports, with the newest two admission and ED weeks corrected by each fit's saved trees (`corrected` view). Equal weight per recipe and per seed; predictive distributions mixed.
- **Peak model:** the same Peak8 release and six fits as on 17 October (`production/releases/peak-20261014.json`), run on the same 21 October panel with 6,000 season paths. US peak size median 34,041 admissions (5-95%: 21,179-52,974); peak week median 19 December 2026 (10-90%: 28 November 2026 to 9 January 2027).
- **File:** `production/submissions/2026-10-24/2026-10-24-ACCIDDA-Chromantis.csv`, SHA256 `7666f2bd5f9f6e5be75bbfa02bc8b8182902990e8aaa9452ba4963872e2b230f`, 12,532 rows: 9,568 weekly quantile rows (52 locations, no Puerto Rico; horizons 0-3; admissions and ED share) followed by 2,964 peak rows. US admissions medians: 6,200; 7,383; 9,272; 11,831 in horizon order. Local checks passed: no quantile crossing, integer counts, ED at most 0.156, correct target dates. The export record (`.json`) describes the weekly part only, so the peer comparison does not repeat the model description.
- **Record:** interval PDFs, the peer comparison (Hub clone `3b4ceeb6`, 57 same-week models including open PRs) and the season-peak PDF with its manifest are in `production/submissions/2026-10-24/`. The scoring of the 17 October files and the comparison with selected Hub models are in `production/output/2026-10-21/check-2026-10-17/` and `production/output/2026-10-21/vs-hub-models/`.

## RSV reference date 24 October 2026

**Same model as 17 October.** [PR 657](https://github.com/CDCgov/rsv-forecast-hub/pull/657) was opened at 21:11 EDT from branch `submit-2026-10-24` of the fork (commit `9eda861`, "ACCIDDA-Chromantis 2026-10-24"). Hub validation, the designated-user authorization check and the `approve-and-merge` job passed; merged at 21:20 EDT the same evening.

- **Model:** release `production/releases/rsv-four-20261014.json`, the four-recipe mixture described in the 17 October entry (40 fits, trained on 2022-23 through 2025-26, no refit), run on the 21 October RSV panel with the `corrected` view.
- **Last week's file, scored:** for the week ending 17 October (first report), US admissions median 774 against 788 observed. On the 51 state/DC tasks, its mean WIS divided by RSVHub-baseline's was 0.75 on log admissions (rank 1 of 10; RSVHub-ensemble 0.81) and 0.55 on counts (rank 2); on ED share 0.82 (rank 3 of 6; ensemble 0.71). Lower is better.
- **File:** `production/submissions/2026-10-24/rsv/2026-10-24-ACCIDDA-Chromantis.parquet`, SHA256 `b08d1cfa2f7ab5f92b68b3caacfa785c829bcf86562b64b8d4481cd31c8849a8`; the CSV beside it has the same rows. Quantiles and 200 sample trajectories per location, horizons 0-3, 52 locations, admissions and ED share. US admissions medians: 1,068; 1,282; 1,537; 1,863, at the 83rd to 92nd percentile of the 10-12 Hub models available.
- **Record:** interval PDFs and the peer comparison (Hub clone `b145a6a`, 14 same-week models including open PRs) in `production/submissions/2026-10-24/rsv/`.

## RSV reference date 17 October 2026

**First RSV submission.** [PR 641](https://github.com/CDCgov/rsv-forecast-hub/pull/641) was opened on 14 October 2026 at 19:10 EDT from the fork's `main` (commit `0e8c4c2b`, "ACCIDDA-Chromantis 2026-10-17"). It adds the model metadata `model-metadata/ACCIDDA-Chromantis.yml` and the forecast. The RSV Hub asks for new-model metadata by 4 PM ET on the first Wednesday, so this PR missed that time. It was merged on 15 October 2026 at 12:39 UTC.

- **Model:** release `production/releases/rsv-four-20261014.json`, a mixture of four recipes with seeds 42-51 each. Equal weight per recipe and per seed; predictive distributions are mixed.
  - Ball_c0w512: width-512 direct-quantile MLP with neighbouring-state exchange, trained on the actual archived reports.
  - Bw: width-256 direct-quantile MLP.
  - A4c0: width-192 sampled MLP with corrected histories and Kinsa.
  - A4i: A4 with all six admission and ED histories.
- **Training and labels:** every fit was trained on 2022-23 through 2025-26, with no held-out season, on `panel-rsv.npz`. In that panel, NHSN RSV admissions before 2024-11-02 are treated as unobserved because reporting was voluntary. Training admission and ED histories were made preliminary with artificial errors from the prescribed 2025-26 RSV reporting process. Labels: latest finalized future RSV admissions and ED share (September 2026 panel). The recipes were selected by tree search `rsv-tree-20261013`. Held-out states/DC log-admission WIS was 0.3105 on artificial preliminary inputs and 0.3114 replayed on archived 2024-25 and 2025-26 reports (lower is better). These are retrospective comparisons, not prospective estimates.
- **Operational inputs:** issuance 14 October 2026. Panel `data/operational-20261014/processed/panel-rsv.npz`, SHA256 `cdf70c024b395ed73504428e5aa43a316d312b3bce74f7cb4cefe25e93dc5b6a`. It is the 14 October operational panel (the same pulls as the influenza entry below) with the same pre-2024-11-02 RSV admission mask as in training. Inputs are the reports visible at the RSV Hub deadline; the RSV Hub's target data `as_of` 2026-10-14 covers weeks through 10 October. View: `corrected`.
- **File:** `production/submissions/2026-10-17/rsv/2026-10-17-ACCIDDA-Chromantis.parquet`, SHA256 `ac28391d2608b9b99600b5020cb5fc9e3f34946198add643ef21c96e8a98ddd3`. It is the Hub's first Parquet from us; the CSV beside it has the same rows.
  - 9,568 quantile rows and 83,200 sample rows: horizons 0-3, 52 locations (no Puerto Rico), `wk inc rsv hosp` and `wk inc rsv prop ed visits`.
  - Samples are 200 trajectories per location, with id `<state>_<k>` shared by both targets and all horizons.
  - The two sampled recipes give whole network draws, picked at evenly spaced ranks at each location. The two direct-quantile recipes give values at evenly spaced levels (0.01-0.99) of their seed-mixture quantiles. These values are ordered by the sampled recipes' trajectories (Schaake shuffle).
  - Sample medians and 10%/90% matched the exported quantiles. Sample 2.5%/97.5% were about 10% narrower.
  - `hubValidations` was not run locally; the PR's Hub CI validates.
- **Record:** the interval PDFs and the peer comparison are in `production/submissions/2026-10-17/rsv/`. The comparison was redrawn on 14 October after 19:30 EDT from Hub clone `8dd45ebb`, with 12 merged same-week models.
- **Metadata update:** on a Hub maintainer's request, `designated_github_users: [jcblemai, emprzy, jlessler]` was added (commit `87cd3c8` on the fork's `main`, same PR) so future submissions by them can auto-merge.

## Influenza reference date 17 October 2026

**Bes was submitted** in [PR 3804](https://github.com/cdcepi/FluSight-forecast-hub/pull/3804), opened 14 October 2026 at 17:09 EDT from the fork's `main` (commit `62a30211`). Hub validation passed and it was merged on 14 October, with weekly targets only. That file is kept in `production/submissions/2026-10-17/superseded/`.

**Season-peak targets were added** in [PR 3815](https://github.com/cdcepi/FluSight-forecast-hub/pull/3815), opened 14 October 2026 at about 18:20 EDT from the fork's `main` (commit `a1885800`). It replaces the same file with the weekly rows unchanged plus `peak inc flu hosp` and `peak week inc flu hosp`. The new file has 12,532 rows, SHA256 `c32fcaf51cc74ce873ed3ce2e7f50679b7dc74fe4c93f8f159393c2ede59f791`; it was merged on 14 October 2026 at 23:45 UTC.

- **Peak model:** release `production/releases/peak-20261014.json`, recipe `artificial_lookback8` from the season-peak search (`experiments/season-peak-ensemble-tree/protocol.json`). It is a season-long sampled MLP with square-root admission counts, logit ED share, local noise, neighbouring-state exchange, multiscale shape features and an 8-week history, trained with weekly, path and peak losses. Training admission and ED histories were perturbed with synchronous_phase_log reporting errors.
- **Training and labels:** 36 future finalized weekly flu admissions and ED share (September 2026 panel), trained on 2022-23 through 2025-26 with no held-out season, seeds 42-47 (training design `experiments/peak-production-20261014.json`, Slurm jobs 4914512 and 4915589). Seeds 48-49 ran out of GPU memory and are not in the submission.
- **Operational inputs:** the same 14 October panel as the weekly forecast, raw Wednesday reports with no finalized fallback. Reported in-window weeks were kept as reported, and 6,000 joint season paths were pooled equally over the six seeds. Each path's maximum and its week give one peak draw (`chromantis.production.season_peak`). It covers 52 locations; Puerto Rico is not included.
- **Development evidence:** these are retrospective, not prospective. Each season was held out in turn and replayed on archived Wednesday reports, on 862 matched state/DC tasks in 2024-25 and 2025-26 (lower is better). Peak-week negative log score was 2.81 against 2.58 for FluSight-ensemble, so the ensemble is better on timing, mainly in the last 7 weeks before the peak. Peak-size WIS on log admissions was 0.306 against 0.523, so this model is better on size.
- **This forecast (US):** peak size median 34,177 admissions (5-95%: 20,905-54,007); peak week median 19 December 2026 (10-90%: 28 November 2026 to 2 January 2027). Plot: `production/submissions/2026-10-17/2026-10-17-ACCIDDA-Chromantis-flu-season-peak-size-and-week.pdf`.

- **Model:** release `production/releases/bes-20261010.json`. One recipe, B_width256: a width-256 MLP with neighbouring-state exchange and 23 direct quantiles, seeds 42-51. Each fit was trained on 2022-23 through 2025-26, with no held-out season. Training admission and ED histories were made preliminary with artificial errors from the prescribed 2025-26 reporting process at 1.5x strength, plus reconstruction labels for the last 4 history weeks. No covariates. Labels: latest finalized future flu admissions and ED share (September 2026 panel). Equal weight per seed; predictive distributions mixed.
- **Why Bes replaced B7:** in the 10 October tree search (`experiments/tree-20261010/protocol.json`), on states/DC log-admission WIS, Bes scored 0.2895 against 0.2976 for the submitted B7 mixture on the same held-out seasons. It was worse than B7 in 2023-24. In the forward-only check (2024-25 forecast by models trained on 2022-23 and 2023-24 only) it scored 0.336 against 0.368. Lower is better. These are retrospective comparisons, not prospective estimates.
- **Operational inputs:** issuance 14 October 2026. Panel `data/operational-20261014/processed/panel.npz`, SHA256 `b8de0b1fd792eeab48f681d661f9feaae944de87aedaf3c28e5cec9f71d4dab9`. It was built from snapshots pulled on 14 October 2026 around 20:34 UTC (Hub target history including the 14 October release, Delphi NHSN and NSSP, PopHIVE Kinsa). Admissions and ED through the week ending 10 October matched the Hub target data exactly for every location over the last 8 weeks. The newest two admission and ED weeks were corrected by each fit's saved trees (`corrected` view).
- **Data note:** Iowa flu ED share was missing in the Hub's 30 September and 7 October releases (weeks ending 4 July to 3 October) and was filled in on 14 October. The 10 October submission therefore had no Iowa ED history for its last 14 weeks; this one does.
- **File:** `production/submissions/2026-10-17/2026-10-17-ACCIDDA-Chromantis.csv`, SHA256 `a4764eb9ad29a816330136c79902f63e2138605a0d5a52e95ca10640ed20880a`. It contains 9,568 quantile rows: horizons 0-3, 52 locations (no Puerto Rico), admissions and ED share, and no peak targets. Local checks passed: ED at most 0.25, admissions below 30% of population, no quantile crossing, integer counts, and correct target dates. The Hub's `hubValidations` was not run locally; the PR's Hub CI validates.
- **Record:** the interval PDFs and the peer comparison drawn at submission time are in `production/submissions/2026-10-17/`. Peers came from the local Hub clone at `8e6ffa74`, with 13 same-week forecasts merged; Google, CMU, UGA, UMass-flusion and NAU-vulPES had not yet submitted.
- **Not used:** B7 run on the same panel (release `b7-20261009`, the 9 October retrain on the current code) forecast lower values: US admissions median 5,049 against Bes's 5,762 at horizon 0, and 9,249 against 11,694 at horizon 3. The exact submitted B7 checkpoints (`b7-20261007`) no longer load in the current code: their saved settings include a field, `forecast_targets`, that it no longer accepts.

## Influenza reference date 10 October 2026

**B7 was submitted and merged.** The Hub's merged CSV is byte-for-byte identical to the saved three-recipe B7 export and the local submission record. Verified on 8 October 2026 by hashing the file at the merge commit of [PR 3764](https://github.com/cdcepi/FluSight-forecast-hub/pull/3764) and the renamed file on Hub `main` after [PR 3774](https://github.com/cdcepi/FluSight-forecast-hub/pull/3774).

### Submission history

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

### What the merged forecast contains

- Public name: **ACCIDDA-Chromantis** since 8 October (submitted as ACCIDDA-EpiLoom). `EpiLoomB7` and `System2` are local export names, not submitted models.
- Issuance: **7 October 2026**, with input context through **3 October**. Reference date: **10 October**.
- Targets: weekly incident influenza hospital admissions in counts and influenza ED visits as proportions from 0 to 1.
- Geography: 50 states, DC and native US, 52 locations total; no Puerto Rico.
- Horizons: 0–3, for weeks ending 10, 17, 24 and 31 October. No sample, peak or rate-change targets were submitted.
- Format: 23 quantiles per task, **9,568 rows** = 52 locations × 2 targets × 4 horizons × 23 quantiles.
- National admission medians: **4,133; 4,698; 5,631; 7,063**, in horizon order. These are forecasts, not observed outcomes.

### The model that produced it

All three neural-network recipes were **retrained on the four completed seasons 2022–23, 2023–24, 2024–25 and 2025–26**, with seeds **42–51** for each recipe. There are 30 fits. Production fitting did not hold out an epidemic season.

Admission and ED training histories were artificially made preliminary using the prescribed **2025–26 reporting-error process**. Future prediction labels remained the frozen research panel's latest flu admissions and ED values, described by the research protocol as the September 2026 reference values. Artificial revisions changed inputs, not future labels. Training and epoch selection used the existing normalized native loss plus **0.5 times the log-admission loss**; ED remained on its native scale.

| Recipe identifier | Model and training treatment |
| --- | --- |
| `A_blocks3` | Width-96 sampled MLP with a three-block decoder and Kinsa. Learns future labels from artificial admission/ED histories corrected by cross-fitted trees. |
| `B5_confirmed_candidate_1` | Width-96 sampled MLP with Kinsa and historical state ILI pretraining before August 2022. Uses the corrected-history training route, with its recipe-specific realizations and uncorrected share. ILI is a pretraining source, not a live input requirement. |
| `B_width256` | Width-256 direct-quantile MLP with neighboring-location exchange and no Kinsa. Learns from artificial preliminary histories, with recent-history reconstruction labels as an auxiliary objective and latest future labels. |

For the operational forecast, the **already fitted** models were replayed on real reported inputs from the pinned 7 October panel, with their saved two-week admission/ED correction trees. This replay did not retrain the neural networks. Kinsa was retained for the two sampled recipes, assumed available and non-revising. No FluSurv or other-pathogen histories were used. Calendar inputs remained enabled; the separate calendar-jitter and 2024 reporting-lapse masking proposal was **not this submitted model**.

The predictive distributions were mixed with equal recipe weights and equal seed weights within recipes: one third per recipe and one thirtieth per fit. This was **distribution mixing**, not averaging member quantiles. The Hub received marginal quantiles; this does not establish calibrated joint epidemic trajectories.

### Selection evidence and its scope

The final matched comparison replayed saved fold models; it did not retrain them. For evaluation on **2024–25**, both systems trained on **2022–23, 2023–24 and 2025–26**. For evaluation on **2025–26**, both trained on **2022–23 through 2024–25**. Both learned latest future admission/ED labels. B7 used artificial admission and ED revisions in training as described above; the eight-recipe System2 retained its B6 recipe-specific treatments, with ED mostly at latest values and no FluSurv member.

Both received the same archived Wednesday reports, including the existing substitutions with later values, and their own saved corrections. Scoring used identical FluSight tasks: reference dates 23 November 2024–31 May 2025 and 22 November 2025–30 May 2026, horizons 0–3. Admissions average those seasons equally; ED covers 2025–26 only. The table is for states/DC, using two seeds per recipe on both sides, not the 10-seed production fits.

| Measure with lower values better | Three-recipe B7 | Eight-recipe System2 without FluSurv |
| --- | ---: | ---: |
| WIS on log of admissions plus one | 0.2642 | 0.2737 |
| Admission-count WIS | 62.14 | 59.59 |
| ED-proportion WIS | 0.005041 | 0.005090 |

B7 traded approximately **3.5% lower log-admission WIS for 4.3% higher admission-count WIS**, with similar ED accuracy. That supported choosing it when season-long state log-admission accuracy was the priority. It does not quantify the expected benefit of the October 10 forecast. The comparison omitted October and early November, reused seasons for selection, and used 2025–26 reporting errors to construct B7's correction even when evaluating that season. The 2024–25 epidemic fold also used later-season training. These are exploratory, exchangeable-season comparisons, not an untouched prospective accuracy estimate.

### Exact artifacts and outstanding discrepancies

Both 10 October files have their interval PDFs (`*-flu-hospital-admissions-forecast-intervals-50-80-95.pdf`, `*-flu-ED-visit-share-forecast-intervals-50-80-95.pdf`) and peer comparison (`*-flu-forecast-medians-vs-hub-models.pdf`, peers merged by the Hub's 7 October 22:46 EDT commit `f66ce884`) in `production/submissions/2026-10-10/` and its `superseded/` folder. They were redrawn on 9 October 2026 from that same local Hub clone, which had not been updated since the submissions; the System2 file's interval PDFs had not been kept at the time.

Local copies were renamed from `ACCIDDA-EpiLoom` to `ACCIDDA-Chromantis` on 14 October 2026; the file contents did not change. The [merged Hub CSV](https://github.com/cdcepi/FluSight-forecast-hub/blob/1b168879a7cc46fbd62b716be4af242caec1061b/model-output/ACCIDDA-EpiLoom/2026-10-10-ACCIDDA-EpiLoom.csv), the renamed [`2026-10-10-ACCIDDA-Chromantis.csv`](https://github.com/cdcepi/FluSight-forecast-hub/blob/main/model-output/ACCIDDA-Chromantis/2026-10-10-ACCIDDA-Chromantis.csv) on Hub `main`, `production/submissions/2026-10-10/2026-10-10-ACCIDDA-Chromantis.csv`, and `output/b7/submission-20261007/2026-10-10-ACCIDDA-EpiLoomB7.csv` share SHA256:

```text
cdee271c326437b81049daed50c453d8b5210ebffa9690d8d593b39e06cf607a
```

The operational panel SHA256 is `68962ec56c8246469bb71c416f9e2abc593d7b68469dd5f4817caf71743029cc`. The export manifest records all 30 forecast sources and their hashes in `output/b7/submission-20261007/2026-10-10-ACCIDDA-EpiLoomB7.json`. Re-exporting those forecasts with the current code (`chromantis.production`, 8 October) reproduces the submitted CSV byte for byte. The production training design is `docs/experiments/b7-production-20261007/design.json`.

The superseded on-time CSV is `production/submissions/2026-10-10/superseded/2026-10-10-ACCIDDA-Chromantis.csv` (as submitted on time), SHA256 `b68b34228bbd4feee5d03fe7ac1e3703f379d4c0dd9cc636f8584b3c7e5f7a70`.

The Hub metadata (`ACCIDDA-Chromantis.yml`) still describes two recipes, five seeds per recipe and averaged quantiles, which matches neither submitted version (B7: three recipes, ten seeds, mixed distributions). Its `ensemble_of_models: false` was set at the user's request at 10:13 pm on 7 October (commit `e8d8ec1d`, “fix ensemble”), when the submission was thought to be a seed ensemble of one recipe; a multi-recipe mixture may need `true`. The B7 export manifest also still says `published: false`, reflecting its pre-publication export state. The B7 release is `production/releases/b7-20261007.json` (all 30 checkpoints with the SHA256 of each `model.pt`, matching the hashes recorded when the forecast was made); the on-time System2 file can be regenerated from `production/releases/system2-20261007.json` (the 80 submitted checkpoints). Decision on 8 October 2026: defer Hub metadata changes until the recipe is settled. The log preserves the methods actually used for each issuance even when later submissions use a different recipe. This log records the actual merged model without changing Hub metadata or launching another submission.

Scientific sources: [production fit](experiments/b7-production-20261007/index.md), [matched comparison](experiments/b7-folds-20261007/vs-system2/index.md), [submission decision review](experiments/submission-choice-review-20261007.md).

The production-fit page reports a second, larger comparison (55 weeks, real reports): B7 state/DC log-admission WIS 4% lower than System2, counts even, ED 2% worse. The table above (two seeds per recipe, both systems) shows ED 1% better for B7. The two comparisons differ in seeds and support; neither is a prospective estimate. The earlier production-fit report uses “submitted” for the then-current System2 file; the chronology above resolves that ambiguity.
