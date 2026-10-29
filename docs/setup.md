# Setup

For local work, run `uv sync` in the checkout and use `.venv/bin/python` for
package commands. The sections below describe the Longleaf installation at
`/proj/jlessler/projects/tapestry-all/tapestry`, with uv-managed Python 3.11.
Substitute your checkout path if it differs. The [research workflow](workflow.md)
covers planning and launching jobs once the environment is ready.

## Clone and install uv

Clone the repository once. Skip the installer if uv is already available.

```bash
cd /proj/jlessler/projects/tapestry-all
git clone https://github.com/ACCIDDA/chromantis.git tapestry

curl -LsSf https://astral.sh/uv/install.sh -o /tmp/chromantis-uv-install.sh
env UV_INSTALL_DIR=/proj/jlessler/projects/tapestry-all/.local/bin \
    UV_NO_MODIFY_PATH=1 sh /tmp/chromantis-uv-install.sh
```

## Python environment

Set the workspace paths in each new shell:

```bash
export PATH=/proj/jlessler/projects/tapestry-all/.local/bin:$PATH
export UV_CACHE_DIR=/proj/jlessler/projects/tapestry-all/.cache/uv
export UV_PYTHON_INSTALL_DIR=/proj/jlessler/projects/tapestry-all/.local/share/uv/python
cd /proj/jlessler/projects/tapestry-all/tapestry
```

Install the research environment:

```bash
uv sync --python-preference only-managed
```

`uv sync` creates `.venv` and installs Chromantis in editable mode with training,
evaluation, explorer and test dependencies. The managed interpreter avoids the
login shell's Anaconda environment. Scoring uses Python and requires no R setup.

## Download the training sources

Initialize the raw-data store and acquire the sources used by the state panel:

```bash
uv run python -m chromantis.data --data-root data init
uv run python -m chromantis.data --data-root data pull \
    delphi_nhsn delphi_nssp delphi_claims_inpatient delphi_claims_outpatient \
    delphi_nwss delphi_nwss_aux hub_flusight_current hub_covid_current \
    hub_rsv_current pophive_kinsa_ili \
    delphi_fluview_ilinet delphi_fluview_clinical delphi_flusurv
```

The [source catalog](data/sources.md) describes targets, claims, wastewater,
Kinsa, ILINet, clinical labs and FluSurv-NET. CDC Socrata entries and legacy or
RSVNet Hub mirrors are available for comparison but are not required for this
panel. Acquisition saves source snapshots; building the panel is a separate step.
Use a Slurm allocation for training and substantial scoring work.

## Sync code and panel from the Mac

The saved `data/processed/panel.npz` is tracked despite the general `/data/`
ignore rule, so the panel can travel with the code. Push to a side branch on
the cluster, then fast-forward its checkout:

```bash
git remote add longleaf chadi@longleaf.unc.edu:/proj/jlessler/projects/tapestry-all/tapestry
git push longleaf HEAD:refs/heads/incoming
ssh chadi@longleaf.unc.edu 'cd /proj/jlessler/projects/tapestry-all/tapestry && git merge --ff-only incoming'
```

Sources are usually acquired and built on the Mac, so a synced panel needs no
cluster rebuild. A planned experiment pins its hash. Replacing it while the
experiment runs prevents remaining tasks from fitting against changed data.

The location/population file `data/metadata/locations.csv` and frozen Hub support
`data/evaluation/b0_hub_comparison_q23` are ignored by Git. Restore the location
file using the pinned commits below and copy the frozen support separately,
for example with `rsync`. The planner pins their hashes alongside the panel's.

## Build the training panel

Build on the machine holding the source snapshots, before planning an experiment:

```bash
.venv/bin/python -m chromantis.dataset.build build --data-root data
.venv/bin/python -m chromantis.dataset.build show
```

The panel contains reference outcomes and Wednesday report histories used to
construct examples. The [workflow](workflow.md#acquire-and-build) includes the
wastewater-index step and panel checks. If you already synced a built panel,
continue with the metadata and frozen support instead.

The commands below restore the pinned Hub commits and population table:

```bash
(
set -euo pipefail
mkdir -p data/mirrors data/metadata
while read -r hub repository revision; do
  mirror="data/mirrors/hub_${hub}_current.git"
  if [[ ! -d "$mirror" ]]; then
    git init --bare "$mirror"
  fi
  git --git-dir="$mirror" fetch --depth=1 \
    "https://github.com/${repository}.git" "$revision"
  git --git-dir="$mirror" update-ref --no-deref HEAD "$revision"
done <<'HUBS'
flusight cdcepi/FluSight-forecast-hub db3d8a9b8f022404affe56166c63a9d224a11861
covid CDCgov/covid19-forecast-hub df7965dd1d4832a96fe6712f9de9f000abc01f3e
rsv CDCgov/rsv-forecast-hub 53baf7db03a2429f5a3710d859319b9029df76cd
HUBS
git --git-dir=data/mirrors/hub_flusight_current.git \
  show HEAD:auxiliary-data/locations.csv > data/metadata/locations.csv
printf '%s  %s\n' \
  80aaa24750044a837e063812a1d0a22339c8b3a92513f71a23dac613eaaa29e0 \
  data/metadata/locations.csv | sha256sum --check
)
```

Keep these files fixed during an experiment. `plan` copies `src/` into
`data/experiments/<experiment>/code`, and the Slurm launcher runs that snapshot.
Replanning replaces it. Local `planner run` uses the working tree. Each attempt's
`run.json` records its Git commit and whether the checkout had uncommitted changes.

## The frozen evaluation denominator

Hub comparisons use the saved 23-quantile support at
`data/evaluation/b0_hub_comparison_q23`, named by `FROZEN` in `planner.py`.
Copy and preserve that directory across checkouts. The package has no supported
command to rebuild it from scratch; constructing replacement support requires
an explicit implementation and a new comparison definition.

## GPU execution

The shared launcher uses the hidden `jlessler` partition:

| Node | GPUs | Host memory | Physical CPU cores |
|---|---|---:|---:|
| `g1803jles01.ll.unc.edu` | 4 × L40, 48 GB each | 512 GB | 56 |
| `g1803jles02.ll.unc.edu` | 2 × H100, 96 GB each | 2 TB | 64 |

Use the [manager commands](workflow.md#plan-launch-and-resume) to plan, launch,
check and rank a study. `scripts/jlessler.sbatch` and the dispatcher control
concurrency; `LANES` sets processes per GPU. A run can use a regular GPU partition
when chosen for that study.

## Documentation hosting

The `ACCIDDA/chromantis` repository publishes the documentation at
[accidda.github.io/chromantis/](https://accidda.github.io/chromantis/). The
Documentation Action on `main` handles publication. The importable package is
`chromantis`; existing local and cluster directory names can remain unchanged.

Update an older checkout's remote with:

```bash
git remote set-url origin https://github.com/ACCIDDA/chromantis.git
```

The repository and documentation URLs changed to lowercase `chromantis` on
9 October 2026. Historical submitted metadata retains the names recorded at
the time.
