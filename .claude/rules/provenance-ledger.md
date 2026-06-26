---
paths:
  - "data/**/*"
  - "results/**/*"
  - "docs/data/provenance-ledger/**/*"
  - "code/00_fetch/**/*"
  - "code/01_build/**/*"
  - "code/02_analyze/**/*"
---

# Provenance Ledger

The Provenance Ledger is the authoritative record for how project data assets
and their queryable units were generated. It lives in:

```text
docs/data/provenance-ledger/
├── index.toml
└── assets/
    ├── <asset_id>.toml
    └── <asset_id>.md
```

## Required Behavior

- Update the Provenance Ledger whenever fetching, creating, transforming, or exporting any data-bearing asset under `data/raw/`, `data/tmp/`, `data/clean/`, or `results/`.
- Claude/Codex may add new files to `data/raw/`, but must not overwrite, edit, delete, rename over, or chmod existing raw files.
- Document every asset and every queryable unit nested inside it: columns, variables, fields, raster bands, layers, class codes, model-output fields, and figure-data fields.
- Ground provenance in actual sources: code, downloaded documentation, codebooks, replication packages, papers, source websites, metadata files, or direct inspection. Do not fill gaps from memory.
- Use repo-relative paths for local evidence and URLs for external evidence; local paths referenced in the Ledger must exist.
- If exact provenance cannot be found, record the gap with `status = "partial-flagged"` or `status = "missing-blocker"` and warn the user.
- Run `make provenance` after data pipeline work and before declaring data-producing work complete.

## Asset Index

`docs/data/provenance-ledger/index.toml` registers every data-bearing asset or
logical asset directory:

```toml
[[assets]]
asset_id = "dataset_biodiversity_01"
path = "data/raw/biodiversity.csv"
metadata = "docs/data/provenance-ledger/assets/dataset_biodiversity_01.toml"
dossier = "docs/data/provenance-ledger/assets/dataset_biodiversity_01.md"
status = "complete"
```

Directories may be registered as logical assets when the real asset is a
multi-file dataset, raster stack, shapefile bundle, or replication package.

## Asset Metadata

Each `assets/<asset_id>.toml` file must include these fields:

```toml
asset_id = "dataset_biodiversity_01"
asset_name = "biodiversity.csv"
path = "data/raw/biodiversity.csv"
asset_type = "dataset"
stage = "raw"
format = "csv"
status = "complete"
created_or_downloaded_at = "2026-06-26T13:22:00Z"
producer_scripts = ["code/00_fetch/00_download_biodiversity.sh"]
upstream_assets = []
source_documents = ["docs/sources/author_2026_biodiversity.md"]
reproduction_command = "make fetch"
dossier = "docs/data/provenance-ledger/assets/dataset_biodiversity_01.md"
last_updated = "2026-06-26"

[[variables]]
id = "var_alpha_diversity"
name = "alpha_diversity"
kind = "continuous"
data_type = "float"
description = "Local species diversity within a site, as defined by the source paper."
unit = "Shannon index"
missing_value_codes = ["NaN"]
allowed_values = []
derivation = "Downloaded from the authors' replication file without transformation."
source_evidence = ["docs/sources/author_2026_biodiversity.md#data"]
status = "complete"
```

For categorical, coded, raster-class, or classification variables, `allowed_values`
must enumerate values with meanings, class definitions, algorithms, thresholds,
temporal rules, and uncertainty flags where relevant. If the values cannot be
fully recovered, keep the variable entry but flag it.

## Narrative Dossier

Each `assets/<asset_id>.md` file should explain:

- Asset identity, file path, stage, and role in the project.
- Exact generation procedure from raw sources to this asset.
- External source documents consulted, with paths, pages, sections, URLs, or commands.
- Variable-level definitions, units, transformations, codes, missing-value rules, and known limitations.
- Reproduction command and validation checks.
- Open provenance gaps and what was tried.

## Status Values

- `complete`: source-grounded asset and variable provenance are documented.
- `partial-flagged`: usable but some non-blocking provenance remains incomplete.
- `missing-blocker`: provenance is too incomplete for reliable use; the checker fails.
- `accepted-limited`: the user accepted a known limitation after being warned.
