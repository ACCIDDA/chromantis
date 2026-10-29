# Interactive availability staircase

Choose a signal and location to see what the archive contains at each forecast
deadline. The availability panel classifies the reporting evidence. The revision
panel shows how reported values differ from a fixed reference snapshot. Select
the same signal and location in both panels to compare them.

<div class="staircase-comparison">
<div><h2>Availability</h2><iframe class="availability-frame" src="../availability/timeline/evidence.html" title="Interactive availability staircase" loading="lazy"></iframe></div>
<div><h2>Revisions</h2><iframe class="availability-frame" src="../revisions/index.html?view=revisions" title="Separate signed revision explorer" loading="lazy"></iframe></div>
</div>

[Open both panels full-size](revisions/comparison.html) or
[open availability alone](availability/timeline/evidence.html). The revision
panel displays one line per Wednesday over 2–12 trailing weeks, with the
reference history on the right axis. Positive percentages indicate upward
revisions. The [revision guide](revision-staircase.md) defines the calculation.

## Read the staircase

The horizontal axis shows Saturday observation weeks. The vertical axis shows
nominal Wednesday forecast rounds, with later rounds higher. The diagonal
boundary is T−0, the Saturday four days before Wednesday. Moving one cell left
reaches T−1; following a column upward traces the reporting evidence for one
observation week.

For Wednesday 14 January 2026, T−0 is 10 January and T−1 is 3 January. Holiday
extensions change the actual cutoff while keeping the Wednesday row and its
Saturday. Hover to see that cutoff. Aggregate cells can combine several states'
statuses; their tooltips list the states in each category.

| Mark | Evidence in the inspected archive | Interpretation |
|---|---|---|
| Green | A finite value was reported by the deadline | Observed availability |
| Gray | No eligible report, but a value exists elsewhere in the history or reference panel | Publication timing unknown |
| Blue | An explicit missing statement followed by a later finite report | Evidence of a missing-to-present transition |
| Red × | Explicit missing statement, with no later finite report observed | Missing or withdrawn at that deadline |
| Beige × | No finite value anywhere in the inspected archive or reference panel | Unobserved in this dataset; support or archive coverage may be incomplete |
| Yellow | Locations have different statuses | Hover or select one location |
| White | The observation week is in the future | No report is expected yet |

A later archive can contain values published before collection began. The view
therefore requires a preceding explicit missing statement before assigning blue.
An explicit null can also mean suppression or withdrawal. Red and beige do not
prove permanent absence. Unsupported states remain selectable individually but
are excluded from aggregates.

## Evidence and assumptions

The classifications use the frozen panel's known-report masks and raw claims,
ILI, laboratory and FluSurv statement histories before conflict rejection.
Conflicting finite claims values count as evidence of a report. For those raw
sources, the scan looks for later reports through the pinned snapshot. Other
sources are checked through the panel's last available issuance. A reference-only
value supplies no publication date.

Use stable periods of observed releases when choosing a publication lag for a
new season. Extending that lag across gray periods is an inference and should
be labeled as such. The staircase leaves unknown timing visible rather than
filling it with an assumed delay.

[Evidence data](availability/timeline/evidence.json) ·
[Evidence counts](availability/timeline/evidence-counts.csv).
