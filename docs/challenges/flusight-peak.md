# FluSight: influenza season peak

FluSight also accepts two season-peak targets in the weekly file: the highest weekly
influenza admission count of the 2026–27 season (`peak inc flu hosp`, quantiles,
nonnegative integers) and the week in which it occurs (`peak week inc flu hosp`, a
probability for each candidate Saturday, summing to one). Both leave `horizon` and
`target_end_date` empty. FluSight does not score tied peak weeks for a location. No complete
2026–27 scoring specification for the peak targets was found
([Respiratory hub rules](../reference/hub-scoring-2026-2027.md)). The weekly targets of the
same file are on [FluSight weekly](flusight-weekly.md).

## Status

| Item | Value |
|---|---|
| Public model | ACCIDDA-Chromantis, in the same file as the weekly targets |
| Submitted | 17, 24 and 31 October 2026 |
| Current model | Peak8, release `production/releases/peak-20261014.json` (6 fits) |
| What we submit | 52 locations (no Puerto Rico), both peak targets |

## Current model

One recipe, `artificial_lookback8`, six seeds (42–47): a season-long sampled MLP that reads
an 8-week history of square-root admission counts and logit ED share, with local noise,
neighbouring-state exchange and multiscale shape features. It was trained with weekly,
whole-path and peak losses.

**Training.** Trained on 2022–23 through 2025–26 with no season held out. The admission and
ED training histories were perturbed with artificial reporting errors
(`synchronous_phase_log`). The prediction labels are the 36 future finalized weekly flu
admissions and ED shares (September 2026 panel).

**Each week.** The saved fits read that Wednesday's reports, with no finalized fallback, and
draw 6,000 joint season paths pooled equally over the six seeds. Each path's maximum and its
week give one peak draw (`chromantis.production.season_peak`). Reported weeks of the season
are kept as reported.

## How it was chosen

- 7 October (stopped): [whole-season paths versus peak loss](../experiments/peak-study-20261007/index.md)
  and [autoregressive rollout](../experiments/peak-rollout-20261007/index.md).
- 12–13 October: tree searches `season-peak-tree` and `season-peak-ensemble-tree`
  (`experiments/season-peak-tree/protocol.json`,
  `experiments/season-peak-ensemble-tree/protocol.json`). Each season was held out in turn
  and replayed on archived Wednesday reports; the score is peak-week negative log score plus
  peak-size WIS on log admissions (lower is better). There is no report page for these
  searches yet; the development evidence is in the 17 October entry below.
- 24–26 October: a conditional-VAE latent improved the peak-week log score in retrospective
  folds ([autoencoders and conditional VAEs](../experiments/autoenc-20261024/index.md)); it
  is not in the submitted model.

## Submission log

Newest first. The file, PR and operational inputs are shared with the weekly targets and are
recorded in the [FluSight weekly log](flusight-weekly.md#submission-log).

### Reference date 31 October 2026

Same file and PR as the [weekly entry](flusight-weekly.md#reference-date-31-october-2026).

- **Peak model:** the same Peak8 release and six fits (`production/releases/peak-20261014.json`), run on the same 28 October panel with 6,000 season paths. US peak size median 34,722 admissions (5-95%: 22,192-52,538); peak week median 19 December 2026 (10-90%: 28 November 2026 to 9 January 2027).


### Reference date 24 October 2026

Same file and PR as the [weekly entry](flusight-weekly.md#reference-date-24-october-2026).

- **Peak model:** the same Peak8 release and six fits as on 17 October (`production/releases/peak-20261014.json`), run on the same 21 October panel with 6,000 season paths. US peak size median 34,041 admissions (5-95%: 21,179-52,974); peak week median 19 December 2026 (10-90%: 28 November 2026 to 9 January 2027).


### Reference date 17 October 2026

First season-peak submission, in the FluSight weekly file.

**Season-peak targets were added** in [PR 3815](https://github.com/cdcepi/FluSight-forecast-hub/pull/3815), opened 14 October 2026 at about 18:20 EDT from the fork's `main` (commit `a1885800`). It replaces the same file with the weekly rows unchanged plus `peak inc flu hosp` and `peak week inc flu hosp`. The new file has 12,532 rows, SHA256 `c32fcaf51cc74ce873ed3ce2e7f50679b7dc74fe4c93f8f159393c2ede59f791`; it was merged on 14 October 2026 at 23:45 UTC.

- **Peak model:** release `production/releases/peak-20261014.json`, recipe `artificial_lookback8` from the season-peak search (`experiments/season-peak-ensemble-tree/protocol.json`). It is a season-long sampled MLP with square-root admission counts, logit ED share, local noise, neighbouring-state exchange, multiscale shape features and an 8-week history, trained with weekly, path and peak losses. Training admission and ED histories were perturbed with synchronous_phase_log reporting errors.
- **Training and labels:** 36 future finalized weekly flu admissions and ED share (September 2026 panel), trained on 2022-23 through 2025-26 with no held-out season, seeds 42-47 (training design `experiments/peak-production-20261014.json`, Slurm jobs 4914512 and 4915589). Seeds 48-49 ran out of GPU memory and are not in the submission.
- **Operational inputs:** the same 14 October panel as the weekly forecast, raw Wednesday reports with no finalized fallback. Reported in-window weeks were kept as reported, and 6,000 joint season paths were pooled equally over the six seeds. Each path's maximum and its week give one peak draw (`chromantis.production.season_peak`). It covers 52 locations; Puerto Rico is not included.
- **Development evidence:** these are retrospective, not prospective. Each season was held out in turn and replayed on archived Wednesday reports, on 862 matched state/DC tasks in 2024-25 and 2025-26 (lower is better). Peak-week negative log score was 2.81 against 2.58 for FluSight-ensemble, so the ensemble is better on timing, mainly in the last 7 weeks before the peak. Peak-size WIS on log admissions was 0.306 against 0.523, so this model is better on size.
- **This forecast (US):** peak size median 34,177 admissions (5-95%: 20,905-54,007); peak week median 19 December 2026 (10-90%: 28 November 2026 to 2 January 2027). Plot: `production/submissions/2026-10-17/2026-10-17-ACCIDDA-Chromantis-flu-season-peak-size-and-week.pdf`.
