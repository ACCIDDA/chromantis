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
| Submitted | 31 October, 7 November and 14 November 2026 |
| Current model | Negative-binomial nowcast, then three neural recipes × four seeds (12 fits) |
| Latest file | 14 November 2026, [PR 117](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/117), opened 10 November |
| What we submit | 75 locations (country, 8 provinces, the 66 health zones with at least one reported case), the five newest onset weeks (nowcast) and four weeks ahead, 100 trajectories, with `forecast_date` |

## Current model

**Nowcast.** For each health zone, the cases still to be added to the five newest onset
weeks are drawn release step by release step from a negative-binomial model, so zones
reporting zero can gain cases. The share added per release at each lag (weeks since the onset
week ended) is the geometric mean over every pair of consecutive Hub releases since 9 October;
the zone-level weights and dispersion are fitted to the latest release pair. It
runs on cases with an observed onset date; cases the Hub gave an imputed onset are added
unchanged, plus 14% of the cases still to come for those reported without onset date.
Provinces and the country are sums of their health zones. 100 seeded draws.

**Forecast.** Three recipes, four seeds each (42–45), selected by the five-window rescoring
below. All read the last six weeks of square-root case counts and sample joint four-week
trajectories:

- `top035_r020_child09`: pools locations, no outbreak-total input.
- `top004_r026_child20`: pools locations, with outbreak-total summaries.
- `top045_r017_child03`: no pooling across locations, outbreak-total growth input.

**Training.** Each fit was trained on weekly cases from the 2014–15 West Africa outbreak,
the 2018–20 Kivu outbreak and BDBV weeks up to five weeks before the last data week (through 3 October 2026 for the 14 November file), at their latest values,
with no held-out window. The prediction labels are the cases 1–4 weeks ahead.

**Trajectories.** Trajectory i is nowcast draw i followed by the forecast that fit
(i mod 12) sampled from that draw, so all fits contribute equally. Future weeks are
reconciled top-down in each trajectory: the national value is kept, provinces are scaled to
sum to it and health zones to their province. The code is `scripts/ebola_nowcast.py` and
`scripts/ebola_project.py`.

## Inputs and nowcast

| Input | `top035_r020_child09` | `top004_r026_child20` | `top045_r017_child03` |
|---|---|---|---|
| Histories read | 6 weeks of square-root case counts | 6 weeks of square-root case counts | 6 weeks of square-root case counts |
| Correction of the newest reported weeks | Reads each nowcast draw | Reads each nowcast draw | Reads each nowcast draw |
| Other pathogens | No | No | No |
| Additional data (covariates) | None | Outbreak-total cases, as summary features | Outbreak-total cases, as recent growth features |
| Extra training data | West Africa 2014–15 and Kivu 2018–20 outbreaks | The same | The same |
| Sharing across locations | Pooled across locations | Pooled across locations | None |
| Other features | No calendar or population | No calendar or population | No calendar or population, no recent-dynamics features |

**Nowcast.** This is the one challenge with a separate nowcast model, because recent onset
weeks are incomplete and the Hub asks for those weeks as well as future ones. The negative-binomial nowcast described above fills the five newest
onset weeks, and those filled weeks are both submitted as the nowcast and read by the neural
models. Training stops five weeks before the last data week because later weeks are still
growing; training uses the latest values with no artificial reporting errors.

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

## Submission log

Newest first.

### Reference date 14 November 2026

[PR 117](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/117) was opened on 10 November 2026 at
18:11 UTC from branch `ACCIDDA-Chromantis-2026-11-14` of `jcblemai/BDBV-Modeling-Hub`, based on the
Hub's `main` at `f8dcc3b`, with `forecast_date` 2026-11-10. Hub validation passed.

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
