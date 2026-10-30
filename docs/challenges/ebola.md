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
| Submitted | 31 October 2026 |
| Current model | Negative-binomial nowcast, then three neural recipes × four seeds (12 fits) |
| Latest file | 31 October 2026, [PR 71](https://github.com/InsightNet-US/BDBV-Modeling-Hub/pull/71), merged 27 October |
| What we submit | 75 locations (country, 8 provinces, the 66 health zones with at least one reported case), weeks ending 26 September to 21 November, 100 trajectories |

## Current model

**Nowcast.** For each health zone, the cases still to be added to the five newest onset
weeks are drawn release step by release step from a negative-binomial model fitted to the
cases added between the 17 and 24 October Hub releases, so zones reporting zero can gain
cases. Provinces and the country are sums of their health zones. 100 seeded draws.

**Forecast.** Three recipes, four seeds each (42–45), selected by the five-window rescoring
below. All read the last six weeks of square-root case counts and sample joint four-week
trajectories:

- `top035_r020_child09`: pools locations, no outbreak-total input.
- `top004_r026_child20`: pools locations, with outbreak-total summaries.
- `top045_r017_child03`: no pooling across locations, outbreak-total growth input.

**Training.** Each fit was trained on weekly cases from the 2014–15 West Africa outbreak,
the 2018–20 Kivu outbreak and BDBV weeks through 19 September 2026, at their latest values,
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
models. Training stops at BDBV weeks through 19 September because later weeks are still
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
