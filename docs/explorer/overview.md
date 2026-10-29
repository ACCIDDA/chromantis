# Data explorer

Use the explorer to compare surveillance series and see how their reported
values changed. Choose a location and signals, then select an *As of* date to
overlay the history available at that cutoff. The solid line shows the latest
available values; the dashed line shows the selected historical version.

The [published explorer](https://accidda.github.io/chromantis/explorer/) contains
a saved export. Its banner gives the export date. A local explorer reads the
sources downloaded to your checkout and can be refreshed as new reports arrive.
The [availability staircase](../data/staircase.md) provides a different view:
it classifies evidence for whether a report existed at each deadline.

## Using the data

Start with a state or the United States. Search the signal list, then select
the provider and release variants you want to plot. Native-state observations
are the default. National context remains labeled as national when displayed
beside state series. A state label attached to a county, catchment or wastewater
site does not make that observation statewide; those rows are excluded from the
selected explorer data.

Each selection opens a card with its date range, point count and provenance.
Publisher descriptions appear on hover, while API field names and source
identifiers remain available for tracing the data. Delphi variants are orange
in the selector and Hub variants blue. Within the chart, each series keeps one
color across its latest and historical versions. Line widths and marker shapes
help distinguish overlapping series. Hub targets use black for admissions
(light gray in dark mode) and red for ED visits.

Selections persist when you change locations. The explorer looks for the
corresponding variant with the same source, measure and other dimensions; a
selected series with no observations remains visible as an empty selection.
The US view uses published national observations. It never constructs a total
from states. National-only products remain national context.

Hub presets select four series: the Hub's admission and ED targets, and their
Delphi counterparts. They turn on **Divide by mean** so counts, percentages and
proportions can share a plot. The divisor is each series' latest mean over the
dates common to all selected series; historical versions use that same divisor.
The [filter guide](filters.md) explains the units and display scaling.

### Choose a date window

Use the overview and date controls to select the observation period. Drag the
selected window to pan or select a new range outside it. **All dates** restores
the full history. Endpoints are included, with a minimum window of one day.
The main y-axis adjusts to the window; the overview scales signals separately.
Changing the observation window leaves the historical report cutoff unchanged.

### Compare report versions

The **As of** control selects information from the saved raw snapshots. Typed
dates and chart clicks round back to the preceding Wednesday or Saturday.
The version arrows move between those cutoffs; **← Wed** and **Wed →** move
between Wednesdays. Forward movement stops at today. Observation dates keep
their original cadence, so a daily series still has daily points.

**Finalized (latest)** means the latest values in the selected source snapshot.
Publishers may revise them again. Reports persist until a later eligible report
changes them. Complete Hub releases preserve omissions and retractions, and a
null latest revision does not restore an earlier value. Unversioned sources
use an observation-date cutoff; sources without row publication dates use their
saved snapshot or commit timestamp.

The chart resolves Git history saved during intake without fetching Git at
query time. `hub-history` can backfill a pinned acquisition, while `--hub-as-of`
can acquire another historical tip. The [vintage policy](../data/methods.md#vintages-and-geography)
describes these information cutoffs.

Repeated rows for one state, measure, observation date and release are displayed
as an unweighted mean, with the contributing count in the tooltip. **Index
details** lists missing, excluded and malformed sources. The banner credits
CMU Delphi, CDC and the respiratory Hubs and links to
[EpiVis](https://delphi.cmu.edu/epivis/) and [RespiLens](https://respilens.org),
which informed the interface. Its dismissal lasts for the current page load.

## Commands

Install the Parquet dependency and start the explorer from the repository root:

```bash
python -m pip install -e '.[explorer]'
python -m chromantis.explorer --data-root data serve --no-browser
```

The server defaults to `http://127.0.0.1:8765/`. Omit `--no-browser` to open it
automatically, or pass `--port 8877` for another port.

```bash
# Build without starting the server; reuse a current index.
python -m chromantis.explorer --data-root data index

# Force a rebuild, optionally adjusting buffer and SQLite cache sizes.
python -m chromantis.explorer --data-root data index --force \
  --batch-rows 100000 --cache-mb 256

# Read saved metadata, source errors, and freshness without rebuilding.
python -m chromantis.explorer --data-root data status

# Check SQLite integrity and the Parquet footer.
python -m chromantis.explorer --data-root data validate

# Refuse builds or reuse with source errors.
python -m chromantis.explorer --data-root data index --strict

# Serve an existing index without checking the raw inventory.
python -m chromantis.explorer --data-root data serve --no-index --no-browser
```

The reproducible B2 wastewater path is three explicit steps: acquire the
versioned NWSS signals and auxiliary join table, build and register the derived
state-index snapshot, then rebuild the explorer. The auxiliary endpoint is
roughly 10 GB; `--import-file` can register a previously downloaded complete
CSV or CSV.gz while retaining its path and checksum in the immutable manifest.

```bash
.venv/bin/python -m chromantis.data --data-root data pull delphi_nwss --mode archive --fill-method source --geo-type sewershed --signal flu_avg_conc_lin --signal covid_avg_conc_lin --signal rsv_avg_conc_lin --workers 3
.venv/bin/python -m chromantis.data --data-root data pull delphi_nwss_aux
.venv/bin/python -m chromantis.explorer.cli --data-root data index
```

Then rebuild the derived indices with `.venv/bin/python -m chromantis.dataset.build nwss-indices --data-root data` (`src/chromantis/dataset/nwss.py`)). It registers a new `derived_nwss_state_indices` snapshot, which `chromantis.dataset.build build` and the explorer index read.

`--batch-rows` bounds the revision buffer; `--cache-mb` sets the SQLite page-cache
budget. These are not a total process-memory limit. Every format uses the same
streaming path; there is no optional Polars indexer. For an isolated experiment,
put `--index-path` in a separate directory before the command, or specify both
`--index-path` and `--ledger-path`.

Builds report time and revision rows per artifact. Failed partial Parquet writes
abort the build and preserve the previous pair. Local file locks reject competing
builders. Stop the server before rebuilding: replacing the two files is not
atomic as a pair. Matching build IDs detect interrupted publication; rebuild to
recover. Indexes built with a different schema or selection policy are rebuilt.

`status` and `validate` emit JSON. Storage errors cause a nonzero exit; stale
indexes and source errors are reported separately. Validation checks SQLite
`quick_check`/`foreign_key_check`, Parquet schema and row count, and matching build
IDs. It does not compare every value to raw data. Strict mode rejects source
errors; intentional exclusions and quarantined conflicts remain audit entries.

## Source representation

The explorer uses the shared [selection policy](../data/methods.md). Its selected
stream contains native state and national observations. NHSN and NSSP group
related CDC, Delphi and current Hub measures while keeping provider, release,
unit and smoothing variants separate. Historical Hub products retain their own
target definitions.

Claims remain versioned raw sources. Wastewater comes from the registered
`derived_nwss_state_indices` snapshot, with `wval_like` and `pct_rank` displayed
and `n_sites` retained for audit. The snapshot records source IDs, hashes and
transformations. Its first usable week depends on the 26-week history and
three-site state thresholds.

Kinsa (`pophive_kinsa_ili`) is a national series with PopHIVE Git commit times
as report timestamps. FluView groups outpatient ILI and clinical laboratory
signals; FluSurv-NET supplies hospitalization rates for catchment states.
Age and fill-method variants remain labeled. The public-health laboratory
source is excluded. The [source catalog](../data/sources.md) gives the measures
and coverage.

## Published explorer

GitHub Pages serves a thinned export committed under `docs/explorer/data/`.
It uses the local interface and one Parquet file per selected series. The
browser downloads that file when plotting the series and resolves catalog,
series, version and data requests locally. GitHub Pages' compressed byte-range
behavior prevents using one large Parquet file for ranged reads.

The export retains Wednesday/Saturday histories and latest values, carrying
unchanged values forward. Later claims revisions remain available; there is no
eight-week revision limit. Hub change logs retain removals. Rebuilding the local
index leaves the published copy at its recorded export date until a new export
is committed and deployed.

Refresh the published data after pulling sources with:

```bash
scripts/update_published_explorer.sh
git add docs/explorer/data
git commit -m "Update published explorer data"
git push
```

The script indexes changed raw data and runs `chromantis.explorer export`.
Publication on `main` copies the committed export and the interface from
`src/chromantis/explorer/static/` into the built site.

## History selection

The local index stores metadata and latest points in SQLite and a compact
revision ledger in Parquet. The indexer scans all raw releases, retaining the
changes needed for Wednesday/Saturday cutoffs and the latest view. It preserves
publisher timestamps, float64 values, repeated-row counts and complete-release
omissions. National observations are stored once under `US`.

Compaction changes the disposable explorer index. Raw snapshots under
`data/raw/` retain every acquired release, and the model dataset builder reads
those snapshots. Indexes are rebuilt when missing, stale or incompatible with
the schema or selection policy. The [local API](api.md) documents the data
returned to the interface.
