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

**Research only: nothing has been submitted.** Two searches ran on 14–15 October 2026 and
left six provisional release files, none published:
`production/releases/covid-*-candidate-20261015.json`. The search record says the export was
checked, but scientific acceptance is incomplete: ED and national intervals were too narrow,
archive gaps were filled with finalized values, and the evaluation design was disputed.

## Candidates

The leading candidate is `covid-half-perturbation-candidate-20261015`: an equal mixture of a
width-256 direct-quantile MLP (neighbouring-state exchange, recent-history reconstruction
labels) and a width-192 sampled MLP (corrected artificial histories), with artificial
reporting errors on half of the training episodes and no covariates. The target-routed
candidate `covid-target-routed-candidate-20261015` keeps that pair for admissions and uses
fourth-root ED versions of the same architectures for ED. Both were trained on 2022–23
through 2025–26 with labels the finalized future COVID admissions and ED shares; training
reporting errors follow the COVID 2025–26 reporting process.

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

No submission.
