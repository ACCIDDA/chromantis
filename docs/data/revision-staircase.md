# Wednesday revision explorer

The revision explorer compares each nominal Wednesday's report with a frozen
reference snapshot from **22 September 2026**. Choose a signal, location and
2–12 trailing weeks, or isolate one forecast round.

[Open availability and revisions side by side](revisions/comparison.html) ·
[Open revisions and fitting periods](revisions/index.html).

<iframe class="availability-frame" src="../revisions/index.html" title="Wednesday revisions and actual fitting periods" loading="lazy"></iframe>

## Read a revision

The default percentage is `100 × (reference − report) / report`. Positive
values show upward revisions, negative values downward revisions and zero an
unchanged value. You can use the reference value as the denominator instead.
The frozen reference serves as the comparison value; publishers may revise it
again.

Each colored line follows one Wednesday round across observation weeks. The
black dashed history uses the right axis in the signal's original units. The
axes scale independently; the revision axis includes zero. T−0 is the preceding
Saturday, followed by T−1 through T−(N−1). A dotted tail from a finite T−0 point
to Wednesday marks the date connection without adding an observation.

A zero denominator gives an undefined percentage unless both values are zero,
which is treated as no change. Missing reports, missing reference values and
undefined percentages break the lines and retain separate CSV statuses. When
both values are missing, the point is classified as a missing report. Weeks
before the panel begins are blank.

## Information available at the cutoff

Snapshots use the processed panel's saved cutoff policy. The exporter adds no
publication times and makes no inference that an absent archived report was
published late. The [availability view](staircase.md) classifies that evidence.
Kinsa remains national; other signals retain native gaps and geographic support.

The revision plot uses the same trailing-week window for all signals. The
fitting plot applies source lags: one week for ILINet, clinical-laboratory flu
positivity and FluSurv, and zero for the other signals.

## Fitting-period backgrounds

The backgrounds describe the dated `reporting-triangle-v11-20261001` experiment.
The exporter checks its panel hash and verifies mask counts against run
manifests. That model reconstructs eight weeks; you can select the reconstruction
age to inspect its labels. A role belongs to the observation week at that age,
rather than every historical input used to predict it. Skipped signal/fold fits
are unused, and held-out cells follow the experiment's location eligibility.

Orange marks chronological missing-cell validation within outer training; those
weeks also enter the final gap-model refit. Red marks held-out evaluation.
Reported-cell correction strength uses up to 52 training weeks. A four-week
maturity/gap rule and purging of scored observation dates across ages separate
calibration and evaluation labels. Those labels come from the later reference
snapshot, so the comparison remains retrospective.

## Forecast-style split figures

These figures show US targets at reconstruction length 8 and the newest
reconstructed week. The interactive view includes other locations, signals
and ages.

![Rolling training and held-out periods](revisions/cv-layout-rolling-us.png)

![Forward-season training and held-out periods](revisions/cv-layout-season-us.png)

Regenerate the views from saved records with:

```bash
.venv/bin/python -m chromantis.explorer.revisions --experiment data/experiments/reporting-triangle-v11-20261001
```

The command draws the explorer without fitting or scoring. For the
reporting-triangle model, the colors describe reference-label calibration and
evaluation. Development factors update each Wednesday using available report
pairs, including earlier evaluation-period reports. The colors therefore do
not describe every input entering the triangle.
