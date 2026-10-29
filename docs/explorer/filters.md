# Filters and interpretation

The signal browser groups observations by pathogen, source and measure. Each
checkbox selects a variant: a provider, release product, geography, unit or
other dimension of that measure. You can compare several variants of the same
signal, including CDC and Delphi versions. Search covers display names,
providers, dataset titles, source paths, API fields and full series labels.

COVID-19, influenza and RSV appear first, followed by combined respiratory
illness, other viruses and all-cause capacity. Sources and signals are
alphabetical within each pathogen. NHSN and NSSP combine related source
products under their origins; the [selection policy](../data/methods.md)
lists the retained measures and files.

## Signal filters

| Filter | What you select |
|---|---|
| Cadence | Daily, weekly, monthly or sample-based observations |
| Revision history | Sources with or without archived versions |
| Spatial support | Native state observations or national context |
| Data currency | Series whose latest observation falls within a cadence-specific window |

The currency windows are 14 days for daily data, 35 for weekly, 75 for monthly
and 45 for sample-based sources. A “current” label describes the indexed dates;
it says nothing about future maintenance by the publisher.

The default spatial filter is native state, and **Reset** restores it. Choose
**Any support** or **National broadcast** to see national-only demographic or
RSV-NET products. The API applies filters before pagination. It reports matching
variants, while the interface also counts distinct signals.

## Series interpretation

Pathogen, subtype, model, target, unit and quantile can define separate variants.
Publisher season fields remain metadata, allowing a covariate to continue
across seasons. The selection policy excludes county, HSA, HHS, catchment and
wastewater-site rows before indexing.

The plot displays repeated rows for one state, series, observation date and
release as an unweighted mean. Hover to see the contributing row count.

## Scaling

**Divide by mean** divides each series by its mean over the dates common to all
selected series. Every series then averages 1 in that window. Historical
versions use the latest version's divisor so revisions remain comparable.
The axis title names the window. Values from a longer history outside that
window can exceed the displayed y-axis range.

This scaling changes the chart display. Raw observations, saved index values
and model-training normalization keep their own definitions.
