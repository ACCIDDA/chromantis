# Chromantis

Chromantis forecasts hospital admissions and the share of emergency-department
visits attributed to influenza, COVID-19 and respiratory syncytial virus (RSV).
The package brings together surveillance data, models of reporting revisions,
neural forecasting models and the tools needed to compare and submit forecasts.
Researchers can use it to study current-week burden, the next four weeks, or
longer outcomes such as the size and timing of an influenza season's peak.

The data pose a problem before forecasting begins. Hospitals and surveillance
systems publish reports at different times, leave gaps and revise past values.
A low count in the latest report may reflect a decline in illness, unfinished
reporting, or both. A forecasting model has to learn from that imperfect history.
A researcher evaluating the model has to reconstruct what it could have known.

## Reading a forecast

[![North Carolina influenza forecasts: reported history, median, and central 50% and 95% prediction intervals](figures/chromantis/forecast.svg)](figures/chromantis/forecast.svg)

The black points show North Carolina's influenza reports available on
21 October 2026. The blue line and bands show the median and central 50% and
95% prediction intervals for the four weeks beginning 24 October. The first
week is a *nowcast*: its outcome was still unreported when the forecast was
issued. The widening bands express the model's uncertainty about later weeks.

Admissions are weekly counts. The ED series measures the proportion of all
emergency-department visits attributed to influenza; the figure displays it as
a percentage. Both outcomes measure healthcare use, which also depends on care
seeking, testing and reporting practices.

The forecast combines three neural model configurations, with ten fits per
configuration. Each fit used a different random seed and trained on 2022–23
through 2025–26 flu admissions and ED histories. Reporting errors measured in
2025–26 made those training inputs resemble preliminary reports. The models
learned to predict future reference admissions and ED shares from the September
2026 snapshot. For this 2026–27 forecast, saved correction trees adjusted the
two newest observed weeks before the saved neural models read the 21 October
reports. The models kept their trained weights. The figure shows the issued
forecast; its future outcomes are not scored here.

## Understanding the method

Five challenges shape the approach. Recent reports need revision estimates.
Missing observations need a representation that distinguishes them from zero.
The short epidemic record calls for learning across locations and signals.
Forecasts need probabilities as well as central estimates. Model comparisons
need a clear account of training data and information available at prediction
time. The [architecture guide](architecture.md) follows these challenges from
the incoming reports to the evaluated forecast.

Chromantis uses a state panel covering the 50 states, Washington, DC and a
separate United States series. Local influenza forecasts use a Flu MetroCast
panel. Flu, RSV, local ED and season-peak applications share the package's data
and modeling tools, with their own fitted models and output rules.

## Using the package

| Your next step | Guide |
|---|---|
| Understand the models | [Challenges and architecture](architecture.md) |
| Install the package and run a study | [Setup](setup.md) and [research workflow](workflow.md) |
| Examine the source data and reporting history | [Data](data/index.md) and [availability staircase](data/staircase.md) |
| Find equations, network layers or release settings | [Model details](reference/model-details.md) |
| Assess the experimental evidence | [Experiment reports](experiments/index.md) |
| Trace an issued forecast to its inputs and fitted models | [Submission log](submissions.md) |
| Configure or extend the code | [Model choices](reference/model-choices.md), [scenario fields](reference/scenario.md) and [Python API](reference/python-api.md) |

The [repository](https://github.com/ACCIDDA/chromantis) contains the source code,
problem definitions and release manifests. Each experiment report records the
training and evaluation setup behind its results.
