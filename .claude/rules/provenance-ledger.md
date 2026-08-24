---
paths:
  - "data/**/*"
  - "results/**/*"
  - "docs/data/provenance-ledger/**/*"
  - "code/00_fetch/**/*"
  - "code/01_build/**/*"
  - "code/02_analyze/**/*"
  - "code/99_explorations/**/*"
---

# Provenance Ledger And Asset Graph

The Provenance Ledger is the authoritative record for file identity and lineage
across governed pipeline code, data, and results, plus variable-level provenance
for data-bearing assets. Documents and repository-control files are outside the
Asset Graph node universe.

```text
docs/data/provenance-ledger/{index.toml,manifests/,dependencies/,history/,assets/}
```

## Required Behavior

- Govern only `code/00_fetch/`, `code/01_build/`, `code/02_analyze/`, `code/99_explorations/`, `data/`, and `results/`.
- Give every governed substantive file one immutable UUID-backed node ID. Preserve it across moves and renames; keep deleted nodes and historical edges queryable. Explicitly exclude documentation and directory/repository-control placeholders instead of registering them.
- After adding, changing, moving, deleting, reading, or writing a governed file, inspect its direct file contract and update nodes, lifecycle events, activities, edges, review hashes, and asset metadata as needed.
- Dependency records are agent-authored from source inspection. Do not use automated discovery to write relationships.
- Store direct edges once as upstream to downstream. Use graph queries to derive downstream adjacency and transitive lineage.
- Claude/Codex may add new files to `data/raw/`, but must not overwrite, edit, delete, rename over, or chmod existing raw files.
- Document every asset and every queryable unit nested inside it: columns, variables, fields, raster bands, layers, class codes, model-output fields, and figure-data fields.
- Ground provenance in actual sources: code, downloaded documentation, codebooks, replication packages, papers, source websites, metadata files, or direct inspection. Do not fill gaps from memory.
- Use repo-relative paths for local evidence and URLs for external evidence; local paths referenced in the Ledger must exist.
- If exact provenance cannot be found, record the gap with `status = "partial-flagged"` or `status = "missing-blocker"` and warn the user.
- Run `make provenance` after data pipeline work and before declaring data-producing work complete.

## Historical Identity

- A move retains the node ID and appends a `moved` lifecycle event.
- A deletion retains the node as `retired`, including last-known path, hash, Git revision, and historical producer/consumer relationships.
- A restored logical file may reactivate its old ID only after agent confirmation.
- Reuse of a retired path for unrelated content requires a new ID.
- Historical provenance edges may point to retired nodes; current operational edges may not depend on a retired required node.

Logical assets may group multi-file datasets, but never satisfy individual file coverage.

## Asset Metadata

Each `assets/<asset_id>.toml` file must include these fields:

```toml
asset_id = "dataset_biodiversity_01"
node_id = "file_immutable_uuid"
asset_name = "biodiversity.csv"
asset_type = "dataset"
format = "csv"
status = "complete"
created_or_downloaded_at = "2026-06-26T13:22:00Z"
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

## Querying

Use `/inspect-asset-graph` or the Asset Graph CLI for immediate upstream/downstream, full lineage, raw sources, producers, path history, impact, and rebuildability. Inspection is read-only and must label stale records as non-authoritative.
