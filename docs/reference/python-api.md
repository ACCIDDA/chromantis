# Python API

Use these interfaces when building an analysis or extending the package. The
acquisition types are re-exported by `chromantis.data`. The
[command-line reference](cli.md) covers acquisition and explorer tasks that do
not require Python integration.

## Data package

::: chromantis.data
    options:
      members_order: source
      show_root_full_path: false

## Repository

::: chromantis.data.repository.RawDataRepository
    options:
      members: true
      show_root_full_path: false

## Data models

::: chromantis.data.models
    options:
      members_order: source
      show_root_full_path: false

## Geography

::: chromantis.data.geography
    options:
      members_order: source
      show_root_full_path: false

## Shared post-intake selection

::: chromantis.data.selection.SelectedData
    options:
      members: true
      show_root_full_path: false

## Explorer index

::: chromantis.explorer.ExplorerIndex
    options:
      members: true
      show_root_full_path: false
