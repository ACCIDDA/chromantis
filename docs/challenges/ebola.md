# BDBV Modeling Hub (Ebola)

The [BDBV Modeling Hub](https://github.com/InsightNet-US/BDBV-Modeling-Hub) collects nowcasts
and short-term forecasts of the 2026 Bundibugyo virus (Ebola) outbreak in the Democratic
Republic of the Congo. It is run by Insight Net centres (ACCIDDA and epiEngage), the School
of Public Health of the University of Kinshasa and the INSP. The current round's target is
`wk inc confirmed cases`: confirmed cases by week of symptom onset (Sunday to Saturday), for
the country, its 26 provinces and 519 health zones. Recent weeks are incomplete when the data
are released, so each file covers already elapsed weeks (nowcasts) and future weeks. A file
may cover any week from the start of the outbreak to three weeks after the reference date,
with 100 sample trajectories per location. The reference date is the Saturday ending the week
of submission; files are accepted Sunday to Tuesday of that week. The Hub's first round,
on total outbreak size, is closed; no Chromantis pull request was found for it. The Hub README does not state
a scoring rule.

## Status

| Item | Value |
|---|---|
| Public model | ACCIDDA-Chromantis |
| Submitted | 31 October, 7, 14 (and a resubmission), 21 and 28 November 2026 |
| Current model | Nowcast mixing a daily-delay model and a release-pair model, then three neural recipes × four seeds (12 fits) trained with artificial nowcast noise |
| Latest file | 28 November 2026, [PR 150](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/150), opened 24 November, validation passed |
| What we submit | 76 locations (country, 8 provinces, the 67 health zones with at least one reported case), the five newest onset weeks (nowcast) and four weeks ahead, 100 trajectories, with `forecast_date` |

## Current model

**Nowcast.** The five newest onset weeks are still filling in. Half of the 100 seeded draws come
from each of two models; both run on cases with an observed onset date, add the cases the Hub gave
an imputed onset unchanged, plus 14% of the cases still to come for those reported without onset
date, and make provinces and the country the sums of their health zones.

- *Release-pair model* (`scripts/ebola_nowcast.py`). For each health zone, the cases still to be
  added are drawn release step by release step from a negative-binomial model, so zones reporting
  zero can gain cases. The share added per release at each lag (weeks since the onset week ended)
  is the geometric mean over the two latest pairs of consecutive Hub releases (every pair since
  9 October until 17 November); the zone weights and dispersion are fitted to the latest pair.
- *Daily-delay model* (`scripts/ebola_daily_nowcast.py`, from 24 November). The onset-to-report
  delay in days is estimated from the Hub's case-level delay file (`auxiliary-data/weekly-reporting-delays-by-province*.csv`,
  as it stood at the release), corrected for recent onset days only showing their short delays,
  over the onset weeks of the last 8 weeks. A case reported on the cutoff day is often not yet in
  the release, so completeness is shifted by an entry lag of about one day, fitted on earlier
  release pairs. Each day's final count is drawn from its posterior under a log-linear trend of
  the last 35 days of daily counts, so the newest days, with few cases and low completeness, are
  pulled toward the trend. The national cases still to come are shared over health zones with the
  release-pair model's zone weights.

**Forecast.** Three recipes, four seeds each (42–45), selected by the five-window rescoring
below. All read the last six weeks of square-root case counts and sample joint four-week
trajectories:

- `top035_r020_child09`: pools locations, no outbreak-total input.
- `top004_r026_child20`: pools locations, with outbreak-total summaries.
- `top045_r017_child03`: no pooling across locations, outbreak-total growth input.

**Training.** Each fit is trained on weekly cases from the 2014–15 West Africa outbreak, the
2018–20 Kivu outbreak and BDBV weeks up to five weeks before the last data week (through
17 October 2026 for the 28 November file), at their latest values, with no held-out window. The
prediction labels are the cases 1–4 weeks ahead. From the 14 November resubmission, the last five
history weeks of every training episode are perturbed the way a nowcast error would
(`scripts/ebola_noise.py`, strength 0.5); labels are never changed.

**Trajectories.** Trajectory i is nowcast draw i followed by the forecast that fit
(i mod 12) sampled from that draw, so all fits contribute equally. Future weeks are
reconciled top-down in each trajectory: the national value is kept, provinces are scaled to
sum to it and health zones to their province. The code is `scripts/ebola_project.py`.

## Inputs and nowcast

| Input | `top035_r020_child09` | `top004_r026_child20` | `top045_r017_child03` |
|---|---|---|---|
| Histories read | 6 weeks of square-root case counts | 6 weeks of square-root case counts | 6 weeks of square-root case counts |
| Correction of the newest reported weeks | Reads each nowcast draw | Reads each nowcast draw | Reads each nowcast draw |
| Other pathogens | No | No | No |
| Additional data (covariates) | None | Outbreak-total cases, as summary features | Outbreak-total cases, as recent growth features |
| Extra training data | West Africa 2014–15 and Kivu 2018–20 outbreaks | The same | The same |
| Training-input treatment | Artificial nowcast noise on the last five weeks, strength 0.5 | The same | The same |
| Sharing across locations | Pooled across locations | Pooled across locations | None |
| Other features | No calendar or population | No calendar or population | No calendar or population, no recent-dynamics features |

**Nowcast.** This is the one challenge with a separate nowcast model, because recent onset
weeks are incomplete and the Hub asks for those weeks as well as future ones. The nowcast
described above fills the five newest onset weeks, and those filled weeks are both submitted as
the nowcast and read by the neural models. Training stops five weeks before the last data week
because later weeks are still growing.

**Not used.** The panel also holds each location's parent-area (province or country) cases;
no submitted recipe reads them.

## How it was chosen

Tree search `ebola-20261026` (`experiments/ebola-20261026/`, problems
`ebola-bdbv-screen` and `ebola-bdbv-confirm`): recipes trained on the West Africa, Kivu and
BDBV weeks before each scoring window and scored on BDBV 6 June–18 July and 25 July–29 August
2026, horizons 1–4, mean WIS over BDBV locations on the natural scale (lower is better).
The leaders were then rescored on five windows (problem `ebola-multi-outbreak`): West Africa
January–June 2015, Kivu March–August 2019 and BDBV June, August and September 2026. The
rescoring rank is `experiments/ebola-20261026/rescore-multi-rank.csv` on Longleaf. Until 27
October a single recipe (`r027_child12`) was used; the rescoring favoured the three-recipe
ensemble. There is no report page for this search yet.

## Running a round

**Hub clone.** The Ebola scripts read the Hub from `../hubs/BDBV-Modeling-Hub`, a sibling of
this repository, not from `production/hubs/` like the other Hubs. It is one full clone with two
remotes: `origin` = `InsightNet-US/BDBV-Modeling-Hub` (target data, other teams' files) and `fork`
= `jcblemai/BDBV-Modeling-Hub` (our submission branches `ACCIDDA-Chromantis-<reference date>`).
On a new machine:

```bash
git clone https://github.com/InsightNet-US/BDBV-Modeling-Hub.git ../hubs/BDBV-Modeling-Hub
git -C ../hubs/BDBV-Modeling-Hub remote add fork https://github.com/jcblemai/BDBV-Modeling-Hub.git
```

Longleaf has no clone: each round's folder there (`tapestry-all/ebola-<date>/hub/`) holds a copy of
the Hub's `target-data/` and `auxiliary-data/`, passed with `--hub hub`.

**Steps.** The Hub posts a release on Sunday or Monday; files are accepted Sunday to Tuesday.

1. `git -C ../hubs/BDBV-Modeling-Hub pull` on `main`.
2. In `scripts/ebola_project.py` set `REFERENCE_DATE` (the coming Saturday), `FORECAST_DATE` (the
   day the PR will be opened, checked by the Hub), `RELEASE` (the release's `as_of`), `LAST` (its
   last onset week) and `TRAIN_UNTIL` (five weeks before `LAST`); in `scripts/build_ebola.py` set
   `BDBV_INCOMPLETE_FROM` to two weeks before `LAST`. Default output folder in `scripts/ebola_fit.sbatch`.
3. `PYTHONPATH=src .venv/bin/python scripts/build_ebola.py` rebuilds `data/ebola/panel.npz`.
4. Copy `src scripts problems datasets`, `data/ebola/{panel.npz,locations.csv,manifest.json}` and the
   Hub's `target-data auxiliary-data` (into `hub/`) to a new Longleaf folder `tapestry-all/ebola-<date>`,
   with `.venv` linked to `covid-20261030/.venv`.
5. One array per recipe, four seeds each (a seed takes 0.5-3 minutes):
   `RECIPE=<recipe> sbatch --export=ALL --array=0-3 scripts/ebola_fit.sbatch` for the three recipes.
6. Merge on Longleaf, not on the laptop: the nowcast is recomputed at merge and must give the same
   draws the fits sampled from (the laptop's came out one case different on 23 November).
   `PYTHONPATH=src .venv/bin/python scripts/ebola_project.py merge --out data/ebola/ensemble-<date> --hub hub`,
   then copy the folder back to `data/ebola/`.
7. `scripts/plot_ebola_projection.py data/ebola/ensemble-<date>` draws the national figure and
   every location, with other teams' medians on the Hub's `main` for the same round.
8. Branch `ACCIDDA-Chromantis-<reference date>` from the Hub's `main`, add the file under
   `model-output/ACCIDDA-Chromantis/`, commit "ACCIDDA-Chromantis forecast for <reference date>",
   push to `fork`, open the PR with that title and no body. Then commit here and run
   `scripts/sync_longleaf.sh`.

Past rounds are scored with `scripts/score_ebola_hub.py` (every Hub file against the latest
release) and `scripts/plot_ebola_performance.py data/ebola/hub-scores-<release>.csv`.

## Submission log

Newest first.

### Reference date 28 November 2026

[PR 150](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/150) was opened on 24 November 2026 at
16:25 UTC from branch `ACCIDDA-Chromantis-2026-11-28` of `jcblemai/BDBV-Modeling-Hub` (commit `dbc7a0c`),
based on the Hub's `main` at `4eace09`, with `forecast_date` 2026-11-24. Hub validation passed.

- **Model:** new nowcast, half daily-delay and half release-pair draws (see Current model). The
  same three recipes × four seeds (42–45), retrained with nowcast noise 0.5 on West Africa
  2014–15, Kivu 2018–20 and BDBV weeks through 17 October 2026, latest values, labels 1–4 weeks
  ahead. Fitted on the jlessler GPUs (jobs 10519859–61) from
  `/hickory/proj/jlessler/projects/tapestry-all/ebola-20261128`. Code: commit `4145705`.
- **Operational inputs:** Hub release of 22 November (Hub commit `b0722b6`), panel with BDBV weeks
  ending 14 February to 21 November (10,909 cases; 67 health zones, Watsa CD-HU-13 in Haut Uele
  reporting for the first time, 8 provinces), `BDBV_INCOMPLETE_FROM` 7 November, panel SHA256
  `2d596013dccecc2978f648ce8ec9552e3a1ed8154d4326eb8b32c1ddb236e881`. Nowcast for the weeks ending
  24 October to 21 November.
- **Why the nowcast changed:** nowcasts of the five newest onset weeks were rerun from the 24
  October, 1, 8 and 15 November releases (each with only the data and delay file of that release)
  and scored on the 22 November counts, 20 weeks, mean WIS over 23 sample quantiles, natural scale
  (lower is better). Release-pair model alone (as submitted on 21 November): national 25.3, health
  zones 0.836, 90% intervals covering 70% of weeks, median 13 cases too high on average. Daily-delay
  model with cases spread evenly over the week: 24.3, 0.844, 70%, 28 too low; without the entry lag
  41.4; with its lag fitted on the latest release pair only 32.2; with a delay per province 25.3 and
  0.901; with the trend (as now) 24.4, 0.857, 55%. Half trend daily-delay and half release-pair
  draws: **19.9, 0.800, 80%**, 19 too low; half even-spread and half release-pair: 20.7, 0.813. The
  two models err in opposite directions (the daily one misses backlog releases such as 17 → 24
  October). Dividing each onset day by its own completeness, the direct use of daily counts, was
  worse (newest days carry a handful of cases and near-zero completeness). Four origins only, and
  the mix was picked after seeing them. Script `scripts/ebola_daily_nowcast.py`; results and figure
  in `data/ebola/daily-nowcast-backtest/`.
- **Comparison run:** the same 12 fits sampled from the release-pair nowcast alone
  (`data/ebola/ensemble-2026-11-28-pairs`, jobs 10519862–64): national nowcast 450 and 478 for the
  weeks ending 7 and 14 November, forecast 421 to 392; within 5% of the submitted file.
- **File:** `data/ebola/ensemble-2026-11-28/hub/model-output/ACCIDDA-Chromantis/2026-11-28-ACCIDDA-Chromantis.csv`,
  SHA256 `2401a7e739c60cdba79a28eb06951bd5071c39407563f1c9e6354a039fd42868`, 68,400 sample rows
  (100 × 76 locations × 9 weeks); country = sum of provinces = sum of health zones in every
  trajectory. Merged on Longleaf (the laptop's nowcast differed by one case). Every-location
  figures, with the release-pair comparison: `projection-all-locations-2026-11-23.pdf` and
  `compare-nowcast-2026-11-24.pdf` in that folder.
- **This forecast (country):** reported 528, 468, 418, 361 and 127 for the weeks ending 24 October
  to 21 November; nowcast medians 530, 481, 456, 471 and 457 (5–95% for 21 November 369–697).
  Forecast medians for 28 November to 19 December 439, 433, 424 and 413; 5–95% for 28 November
  284–660. On the submission day OHTJHU-BM was close (nowcast 426, 456, 471; forecast 452–468),
  the baseline flat at 418 and pedro-zonemix higher (551–644). Our forecast drifts down about 2%
  a week; the drift comes from the trained models, not the nowcast.
- **Last round's check:** see the 21 November entry, scored on the 22 November release.

### Reference date 21 November 2026

[PR 134](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/134) was opened on 17 November 2026 at
20:55 UTC from branch `ACCIDDA-Chromantis-2026-11-21` of `jcblemai/BDBV-Modeling-Hub` (commit `7f6c1ef`),
based on the Hub's `main` at `8586760`, with `forecast_date` 2026-11-17. Hub validation passed;
merged on 17 November 2026 at 21:21 UTC (commit `f340b1d`).

- **Model:** the same three recipes × four seeds (42–45), retrained with nowcast noise 0.5 (as in
  the 14 November resubmission) on West Africa 2014–15, Kivu 2018–20 and BDBV weeks through
  10 October 2026, latest values, labels 1–4 weeks ahead. Fitted on the jlessler GPUs from
  `/hickory/proj/jlessler/projects/tapestry-all/ebola-20261121`.
- **Nowcast change:** the release-pair growth per lag became the geometric mean of the two latest
  release pairs instead of every pair since 9 October. The 8 and 15 November pairs agreed on much
  slower late growth (share added at lag 2: 0.018 and 0.025, against 0.09–0.20 before), and the
  all-pair average had overshot the national count of weeks 1–2 weeks old by 10–22% in the 7 and
  14 November rounds. Rerun on the 24 October, 1 and 8 November releases against the 15 November
  counts, the two latest pairs gave mean national WIS 35.1 against 36.1. The all-pair version was
  run alongside (`data/ebola/ensemble-2026-11-21-allpairs`: nowcast 399 and 382 for the weeks
  ending 7 and 14 November, forecast 389 to 347).
- **Operational inputs:** Hub release of 15 November (Hub commit `8586760`), panel with BDBV weeks
  ending 14 February to 14 November (66 health zones, 8 provinces), `BDBV_INCOMPLETE_FROM`
  31 October, panel SHA256 `a0487879e2f973fcde87b1d734306b1b094732f58a6e8d6b9ae15f24edfd99ba`.
  Nowcast for the weeks ending 17 October to 14 November.
- **File:** `data/ebola/ensemble-2026-11-21/hub/model-output/ACCIDDA-Chromantis/2026-11-21-ACCIDDA-Chromantis.csv`,
  SHA256 `4d68b6ccda01d612b1f594acc73a8200d87c0192e36b8471c0b4dbd0a2124d82`, 67,500 sample rows
  (100 × 75 locations × 9 weeks); country = sum of provinces = sum of health zones in every trajectory.
- **This forecast (country):** reported 427, 496, 411, 279 and 90 for the weeks ending 17 October
  to 14 November; nowcast medians 431, 508, 428, 347 and 328. Forecast medians for 21 November to
  12 December 328, 306, 290 and 282; 5–95% for 21 November 238–486. On the submission day
  OHTJHU-BM was nearly identical (346, 330, 344, then 331 to 300); ACCIDDA-insightcast, MOBS-GLEAM,
  NTUCPH-LLM and both UQPSU models were flat at 430–490, pedro-zonemix 376–429, the baseline 411.
- **Last round's check:** the 14 November file scored against the 15 November release on its
  nowcast weeks ending 10 October to 7 November (mean WIS, 23 sample quantiles, natural scale):
  national 33.2 against 12.4 for OHTJHU-BM, 40.2 for ACCIDDA-insightcast and 54–88 for UQPSU-SEIHRD_CTMC,
  pedro-zonemix and both seabbs models; health zones 0.53 against 0.75 for ACCIDDA-insightcast and
  0.95–1.11 for the seabbs models (330 zone-weeks). The two 14 November files share the nowcast
  and score the same on these weeks.
- **Checked on 22 November:** this file was too low. The 15 November release added 287 cases
  (461–696 in earlier release pairs) and the 22 November one 650: the slowdown was reporting, not
  fewer cases. The weeks ending 7 and 14 November now stand at 418 and 361 (nowcast 347 and 328;
  the 14 November week is still growing). On the weeks ending 17 October to 14 November, national
  WIS 20.0, sixth of nine (seabbs-renewal 13.5, seabbs-rwnowcast 14.8, NAU-EpiPathsty 16.0,
  ACCIDDA-insightcast 17.6, pedro-zonemix 19.0, OHTJHU-BM 22.0, UQPSU 34.9 and 43.2); health zones
  0.73, best of the teams with zones (ACCIDDA-insightcast 0.82, seabbs 0.88 and 0.91, NAU 0.89).
  Reacting to the latest release pair made this round worse; the 28 November nowcast keeps half
  its draws from a model that does not.

### Reference date 14 November 2026, resubmission

[PR 122](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/122) was opened on 11 November 2026 at
02:30 UTC from branch `ACCIDDA-Chromantis-2026-11-14-resub` (commit `5554927`), with `forecast_date`
2026-11-11. Hub validation failed only because the submission window had closed (the bot reported
the content valid); the Hub merged it on 11 November at 14:09 UTC (commit `242ebc6`). The Hub file
holds both forecasts, `forecast_date` 2026-11-10 (PR 117) and 2026-11-11: 135,000 rows, SHA256
`b0da37b14ea72e51fb4947f17e1599e6612e28d88aa6895b5f57fb4fbed039a6`
(`data/ebola/resubmit-2026-11-14/`).

- **Change:** the 12 fits were retrained with artificial nowcast noise (`scripts/ebola_noise.py`,
  strength 0.5) on the training inputs only: the last five history weeks of each training episode
  get a log-scale factor shared by all locations (standard deviation 0.35, 0.2, 0.12, 0.06 and 0.03
  times the strength for weeks 0–4 old, set from the 31 October and 7 November nowcast errors) and
  a smaller independent term per location; labels are unchanged. Trained on final counts only, the
  models had trusted the newest week fully: across one file's trajectories, a newest week 10% higher
  gave a national forecast about 17% higher four weeks ahead. Same nowcast, release (8 November),
  training data (through 3 October) and recipes. Folders `data/ebola/ensemble-2026-11-14-noise05`
  (submitted) and `-noise1` (strength 1), comparison `data/ebola/compare-2026-11-14-noise.pdf`.
- **This forecast (country):** nowcast unchanged (392 for the week ending 7 November). Forecast
  medians for 14 November to 5 December 427, 398, 382 and 372 (the first file: 372, 336, 318 and
  308); 5–95% for 14 November 256–717.
- **Checked on 22 November:** national WIS 17.3 on the weeks ending 10 October to 14 November,
  third of eight files on those weeks, after the first 14 November file (15.9) and OHTJHU-BM (16.4).

### Reference date 14 November 2026

[PR 117](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/117) was opened on 10 November 2026 at
18:11 UTC from branch `ACCIDDA-Chromantis-2026-11-14` of `jcblemai/BDBV-Modeling-Hub`, based on the
Hub's `main` at `f8dcc3b`, with `forecast_date` 2026-11-10. Hub validation passed; merged on
10 November 2026 at 18:34 UTC (commit `c9fe11e`).

- **Model:** no code change to the nowcast or the recipes. The same three recipes × four seeds
  (42–45), retrained on West Africa 2014–15, Kivu 2018–20 and BDBV weeks through 3 October 2026
  (five-week rule), latest values, labels 1–4 weeks ahead. Fitted on the jlessler GPUs from
  `/hickory/proj/jlessler/projects/tapestry-all/ebola-20261114`.
- **Operational inputs:** Hub release of 8 November (Hub commit `f8dcc3b`), panel rebuilt with BDBV
  weeks ending 14 February to 7 November (9,979 cases; still 66 health zones and 8 provinces).
  `BDBV_INCOMPLETE_FROM` moved to 24 October. Nowcast for the weeks ending 10 October to 7 November.
  Its growth per lag now averages four release pairs, including the slow 1 → 8 November pair (see the
  7 November check below), so it is lower than last week's: lag 1 0.30 (was 0.34), lag 2 0.08 (was
  0.12), and the lag-2 spread is 1.0 on the log scale (was 0.42).
- **Hub change:** the Hub moved health zone CD-HK-19 (Manika) from Haut Katanga to Lualaba while
  keeping its code. Our code takes the parent from the location code, which would put it under CD-HK.
  It has no cases and is not in our file, so nothing changed this round; this must be handled if it
  ever reports a case.
- **File:** `data/ebola/ensemble-2026-11-14/hub/model-output/ACCIDDA-Chromantis/2026-11-14-ACCIDDA-Chromantis.csv`,
  SHA256 `7abdbd7a3684e76828965c7be85e495806e07f96f48bb69c00baec3ce7c93bd5`, 67,500 sample rows
  (100 × 75 locations × 9 weeks); country = sum of provinces = sum of health zones in every trajectory.
- **This forecast (country):** reported 473, 420, 482, 349 and 68 for the weeks ending 10 October to
  7 November; nowcast medians 478, 442, 534, 500 and 392 (5–95% for 7 November 266–622). Forecast
  medians for 14 November to 5 December 372, 336, 318 and 308; 5–95% for 14 November 200–713. On the
  submission day, between OHTJHU-BM (nowcast 340 for 7 November, forecast about 330) and
  ACCIDDA-insightcast (404, about 415); MOBS-GLEAM, NTUCPH-LLM, pedro-zonemix and the baseline were
  higher (420–500).
- **Last round's check:** the 7 November file scored against the 8 November release on the weeks
  ending 3–24 October (mean WIS over 23 sample quantiles, natural scale, lower is better; the week
  ending 24 October will still grow a few percent). Health zones about level with the other teams:
  0.65 vs 0.71 for ACCIDDA-insightcast and 0.60 for both seabbs models on 66 zones, 0.79 vs 0.77 for
  OHTJHU-BM and pedro-zonemix on 54; 90% intervals covered 90% of zone-weeks. Country and provinces
  too high: national WIS 41 vs 41 for ACCIDDA-insightcast, 4 for OHTJHU-BM, 14 for UQPSU-national_level,
  21–23 for the seabbs models and 33 for pedro-zonemix (all on the same four weeks),
  with the weeks ending 17 and 24 October outside the 90% interval (nowcast 492 and 618; now 420 and
  482). The 31 October file, scored the same way on the weeks ending 26 September to 24 October, was
  close: national medians 430, 509, 489, 426 and 429 against 433, 503, 473, 420 and 482, all inside
  the 90% interval.
- **Why the 7 November nowcast was high:** the 1 → 8 November release added far fewer cases to
  recent weeks than any earlier release pair (461 cases in 7 days against 507–696; share added at
  lag 1 0.18 against 0.29–0.40, at lag 2 0.02 against 0.10–0.20). The 7 November nowcast had averaged
  the earlier, faster pairs, one of them spanning 8 days (24 October → 1 November) and one looking like
  a backlog (17 → 24 October, large additions even at lags 3–4). Rerunning it from the 1 November
  release with all cases (imputed onsets included, as before 3 November) gave the same 614 for the
  week ending 24 October, so the 7 November nowcast changes were not the cause. Using only the latest
  pair's growth gave 584; dropping the pull toward the previous three weeks' level gave 638. The
  spread at lag 1 (0.2, the floor) was too narrow. Whether the slowdown is fewer infections or slower
  reporting cannot be told yet.

### Reference date 7 November 2026

[PR 96](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/96) was opened on 3 November 2026 at
14:58 EST from branch `ACCIDDA-Chromantis-2026-11-07` of `jcblemai/BDBV-Modeling-Hub`, based on the
Hub's `main` at `b66c182`. From this round every row carries `forecast_date` (here 2026-11-03), checked
against the date of the PR in Africa/Kinshasa. Hub validation passed; merged on 4 November 2026 at
09:07 UTC (commit `fb5c2de6`). Checked against the 8 November release in the 14 November entry.

- **Model:** the same three recipes × four seeds (42–45), retrained on West Africa 2014–15, Kivu
  2018–20 and BDBV weeks through 26 September 2026 (one week later than the 31 October file, keeping
  the five-week rule), latest values, labels 1–4 weeks ahead. Fitted on the jlessler GPUs (L40 and H100)
  from `/hickory/proj/jlessler/projects/tapestry-all/ebola-20261107`.
- **Nowcast changes:** a spread per lag instead of one pooled spread (the 31 October file put the
  newest week's 95th percentile at 1,130 national cases from 91 reported), and the model now runs on
  cases with an observed onset date only. Cases the Hub gave an imputed onset are added unchanged, and
  the cases still to come get 14% on top for those without onset date. The report week ending
  31 October carried 141 cases without onset date (40–90 before), 59 of the newest week's 150 cases.
  Scaling them as early reports had put the newest week at 652; with the change it is 626.
- **Operational inputs:** Hub release of 1 November (Hub commit `b66c182`), panel rebuilt with BDBV
  weeks ending 14 February to 31 October (9,477 cases). Nowcast for the weeks ending 3 to 31 October,
  fitted on the 24 October → 1 November release pair.
- **File:** `data/ebola/ensemble-2026-11-07/hub/model-output/ACCIDDA-Chromantis/2026-11-07-ACCIDDA-Chromantis.csv`,
  SHA256 `daf23a9246200827b6e724defa47514384c46de7ad8eab1f40531c7a2c0a887e`, 67,500 sample rows
  (100 × 75 locations × 9 weeks); country = sum of provinces = sum of health zones in every trajectory.
- **This forecast (country):** reported 492, 465, 409, 381 and 150 for the weeks ending 3 to 31
  October; nowcast medians 496, 490, 492, 618 and 626. Forecast medians for 7 to 28 November 647, 686,
  697 and 700; 5–95% for 7 November 442–959. Higher than OHTJHU-BM, UQPSU-oldSchool and both seabbs
  models this round, close to NTUCPH-LLM and pedro-zonemix. Run from the 24 October release, the same
  nowcast was 4–10% above the now nearly final values of the weeks ending 3–17 October.
- **Last round's check:** the 31 October file scored against the 1 November release on weeks at least
  two weeks old (mean WIS over 23 sample quantiles, lower is better): health zones 0.80 vs 1.04 for
  ACCIDDA-insightcast on their 45 shared locations, 0.58 vs 0.77 for OHTJHU-BM on 62.
- **Record:** plots and summary in `data/ebola/ensemble-2026-11-07/`.

### Reference date 31 October 2026

**First BDBV Modeling Hub submission.** [PR 71](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/71)
was opened on 27 October 2026 at 18:49 EDT from branch `ACCIDDA-Chromantis-2026-10-31` of the
fork `jcblemai/BDBV-Modeling-Hub`, based on the Hub's `main` at `07b9844d`. It adds the model
metadata (commit `db483a2`) and the forecast (commit `84c4705`). Merged at 19:43 EDT the same
evening. The local Hub clone is `../hubs/BDBV-Modeling-Hub`.

- **Model:** as described above, 12 fits, trained through 19 September 2026.
- **Operational inputs:** Hub target data release of 24 October (Hub commit `07b9844d`),
  built into `data/ebola/panel.npz` (168 locations over the three outbreaks; BDBV weeks
  ending 14 February to 24 October 2026, 8,955 cases). The nowcast covers the weeks ending
  26 September to 24 October.
- **File:** `data/ebola/ensemble-2026-10-31/hub/model-output/ACCIDDA-Chromantis/2026-10-31-ACCIDDA-Chromantis.csv`,
  SHA256 `6ddf74aae31244a7a750b079c4581a1132fe65a2a867ca2a626c3a14cc7c33a2`, identical to the
  merged Hub file. 67,500 sample rows: 100 trajectories × 75 locations × 9 weeks. In every
  trajectory the country equals the sum of provinces and of health zones.
- **This forecast (country):** reported cases in the 24 October release for the weeks ending
  26 September to 24 October were 420, 478, 413, 262 and 91; the nowcast medians are 430,
  509, 489, 426 and 429. Forecast medians for the weeks ending 31 October to 21 November are
  392, 374, 363 and 357; the 5–95% range for 31 October is 179–1,030.
- **Record:** settings, summary and plots (`projection.png`, `projection-all-locations.pdf`)
  are in `data/ebola/ensemble-2026-10-31/`. They have not been copied to
  `production/submissions/2026-10-31/`.
