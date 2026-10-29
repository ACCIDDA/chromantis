# Data

Surveillance data have two clocks: the week a measurement describes and the
date its report becomes available. A report published in October can revise
September's admission count. The later value can serve as a training label;
a historical forecast needs the value available at its own deadline.

The state panel contains weekly admissions and emergency-department (ED)
shares for the 50 states, Washington, DC and the native US series, plus selected
covariates. Local Flu MetroCast forecasts use a separate panel. Admissions are
counts; ED shares are proportions of visits attributed to a pathogen. Healthcare
use, testing and reporting affect both outcomes.

Each input carries an availability indicator. Missing labels receive no training
weight. The [architecture guide](../architecture.md#missing-observations)
explains how missing observations and archive gaps enter the models.

## Assumed publication schedule

The schedule defines when the model may use a source. `T` is the latest
completed Saturday in the forecast history; `T-1` means the preceding week.

| Data source | Availability |
| --- | --- |
| Kinsa ILI | T-0 |
| FluSurv-NET | T-1 |
| All six targets (NHSN / NSSP) | T-0 |
| Clinical lab flu percent positive | T-1 |
| ILINet ILI | T-1 |
| Inpatient flu / COVID | T-0 |
| Outpatient flu / COVID | T-0 |
| NWSS | T-0 |

The [B2 training protocol](../experiments/b-2-t0/index.md#protocol) introduced
these assumptions, which also govern the
[reported-input evaluation](../workflow.md#standard-evaluation). ED is available
at T-0 in every modeled season under the chosen 2026–27 regime. The 2024–25
archive instead shows ED publication on the following Friday, one week later.
Retrospective newest-week ED inputs for that season therefore mostly use later
reference fills, recorded by stars in reports.

## Deadlines

Each pathogen uses its Hub's deadline. The panel reads archived reports at
Wednesday 23:00 America/New_York, except for the holiday extensions below.
Date-only releases count at the end of their UTC day; Git commits retain exact
timestamps. This policy replaced the 23:59 UTC cutoff on 5 October 2026.

| Hub reference date (Saturday) | Nominal Wednesday | FluSight | COVID Hub | RSV Hub |
|---|---|---|---|---|
| 2024-12-28 | 2024-12-25 | Thu 2024-12-26 | Thu 2024-12-26 | Wed 2024-12-25 (no RSV Hub before 2025-08) |
| 2025-01-04 | 2025-01-01 | Thu 2025-01-02 | Thu 2025-01-02 | Wed 2025-01-01 (no RSV Hub) |
| 2025-12-27 | 2025-12-24 | Tue 2025-12-30 | Mon 2025-12-29 | Mon 2025-12-29 |
| 2026-01-03 | 2025-12-31 | Mon 2026-01-05 | Sun 2026-01-04 | Sun 2026-01-04 |

Extensions change the information cutoff but retain the nominal Wednesday and
preceding Saturday. The panel's main report arrays use FluSight deadlines for
flu forecasts and training. Separate arrays serve COVID or RSV forecasts when
their deadlines differ. The archive contained no deadline extension for
22 January 2025; missing admission reports for the preceding Saturday use
reference fills and are marked accordingly.

## Explore the data

The [availability staircase](staircase.md) shows evidence for what had been
reported at each deadline. The [revision explorer](revision-staircase.md)
compares reported values with a fixed reference snapshot. The
[source explorer](../explorer/overview.md) lets you compare individual series
and versions. Reference-history coverage and evidence of historical availability
answer different questions.

## Current dataset

The reference panel documented here is `data/processed/panel.npz`, covering
14 May 2022–19 September 2026: 228 observation weeks, 52 locations, six targets
and 14 covariate series. It includes 12 context weeks before the 6 August 2022
season start. The 2022–23 season supplies training data; B2 evaluated 2024–25
and 2025–26, while later problems also use 2023–24.

The added 2022–23 season has revised flu and COVID admissions throughout its
52 weeks and locations. ED outcomes begin 1 October 2022; RSV admissions are
absent. Covariates retain their gaps. Finite CDC revised NHSN counts take
precedence in reference outcomes; dated input reports keep their own values.
B2 uses the assumed schedule above with native missing cells, rather than the
availability audit's historical release masks.

<!-- source-history:start -->
## First observation and first archived report dates

An observation date identifies the period measured. The report date below is
the earliest archived release containing a finite value. Neither is the download
date. A source can publish retrospective history, so its first archived report
does not establish when the source first became available.

This scan includes all downloaded native geographies. It applies no state,
Saturday, season, deadline, fill-method or age filter and no conflict rejection.
The linked CSV also records first reports containing null rows.

| Covariate | Earliest observation date | Earliest archived report date |
| --- | --- | --- |
| inpatient_flu | 2019-10-08 | 2020-05-29 |
| inpatient_covid | 2019-10-08 | 2020-05-29 |
| outpatient_flu | 2019-10-08 | 2020-05-29 |
| outpatient_covid | 2019-10-08 | 2020-05-29 |
| ilinet_ili | 1997-10-04 | 2003-11-28 |
| clinical_lab_flu_pct_positive | 2016-10-08 | 2018-10-05 |
| flusurv_flu_rate | 2003-10-04 | 2012-11-02 |
| kinsa_ili | 2019-01-01 | 2026-04-06 |
| NWSS raw covid_avg_conc_lin | 2020-01-14 | 2026-02-25 |
| NWSS raw rsv_avg_conc_lin | 2022-02-27 | 2026-02-25 |
| NWSS raw flu_avg_conc_lin | 2021-09-15 | 2026-02-25 |

Kinsa dates refer to the raw daily series, before the complete-seven-day rule.
NWSS dates refer to raw sewershed concentrations, before weekly indices and
site/history thresholds. The derived wastewater series have their own start
dates in the CSV.

Earliest dates cannot establish continuous coverage. FluSurv has a large gap
from November 2020 to November 2025 and another through February 2026. ILINet's
first archived series may be national rather than state-level.

[All signal dates and raw row counts](availability/raw-archive-starts.csv) ·
[Raw NWSS dates](availability/raw-nwss-starts.csv) ·
[Availability evidence](staircase.md).
<!-- source-history:end -->

## Sources and reporting frequency

| Source | Native frequency and model representation | Details |
| --- | --- | --- |
| NHSN admissions and NSSP ED | Weekly target histories; six pathogen/outcome combinations | [Sources](sources.md) |
| Inpatient/outpatient claims | Daily trailing-seven-day percentages, sampled on Saturday | [Claims](sources.md#claims), [same-date conflict audit](methods.md#same-date-conflicts) |
| Kinsa ILI | Daily national signal, averaged over complete seven-day weeks | [Kinsa](sources.md#kinsa) |
| ILINet ILI, clinical lab positivity, FluSurv | Weekly; geographic coverage differs by source | [FluView and FluSurv](sources.md#fluview-and-flusurv) |
| Wastewater | Irregular raw sampling, converted to weekly WVAL-like and percentile indices | [Wastewater](sources.md#wastewater) |

Claims rows with conflicting finite values on one report date are rejected by
the model pipeline. The availability view still counts evidence of those
reports; revision estimates use the unambiguous subset. The
[conflict audit](methods.md#same-date-conflicts) explains the implications.

## Acquisition, definitions and provenance

Use the [source catalog](sources.md) to identify measures and the
[selection and provenance guide](methods.md) to trace transformations, geography
and report versions. [Panel diagnostics](panel.md) describe a saved snapshot
with its date and hash. The
[deadline audit policy](availability/provenance/deadline-policy.json) and
[operational policy](availability/provenance/operational-policy.json) retain
machine-readable assumptions. Model comparisons are in the
[experiment reports](../experiments/index.md).
