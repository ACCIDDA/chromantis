# Submission comparison

Reference date: 2026-11-28. Hub commit: `e69d757977396603bdfb89f09b86c51d5ccd504f`.

Full-season and zoom panels use independent linear scales. Peer percentiles describe forecast magnitude, not accuracy.

Files: 2026-11-28-ACCIDDA-Chromantis-flu-forecast-medians-vs-hub-models.pdf, comparison-<FIPS>.png, forecast-medians.csv, history.csv, positions.csv, manifest.json.

## Model descriptions

- Amended (state by state): Training seasons, input treatments and prediction labels are not specified in the export note; consult the model record.
- Not amended (masked A, in PR 4244): Training seasons, input treatments and prediction labels are not specified in the export note; consult the model record.
- Median of the 71 other models (FluSight-ensemble stand-in): Training seasons, input treatments and prediction labels are not specified in the export note; consult the model record.

## Assumptions

- Descriptive forecast comparison, not accuracy scoring.
- Latest target values at the pinned Hub commit, not reconstructed issuance-time truth.
- No history dated after reference minus seven days is shown as current observations.
- Prior season aligned by CDC week; unmatched week 53 omitted, no value rescaling.
- Peer bands weight each available model median equally; local candidates are excluded.
- Partial peer coverage is retained; no missing forecasts or history are imputed.
- Training details are copied only from matching local export metadata; peer training is not inferred.

## Availability

- Not amended (masked A, in PR 4244): companion JSON hash does not match; model description not reused.
