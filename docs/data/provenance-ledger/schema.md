# Provenance Ledger v2 schema

## Boundary

The ledger describes only files and lineage within the configured data-code,
data, and results roots in `index.toml`. Repository documents, deliverables,
workflow configuration, agent definitions, and ledger control files are outside
the graph even when a scoped file mentions them. Within a governed root, every
current file or symlink must have exactly one active node unless it matches one
documented exclusion. Logical assets never replace file-level coverage.
The template explicitly excludes `.gitkeep` placeholders and directory
documentation; local nodes with `lifecycle = "control"` or `"documentation"`
are invalid.

The committed TOML is authoritative. Relationships are found by manual source
inspection and are never inferred into the ledger by a parser or runtime tracer.

## Nodes and immutable identity

Each `[[nodes]]` record has an immutable UUID-backed `id`. Its path may change;
its identity must not. Required fields for an active local node are:

- `id`, `node_type`, `current_path`, and `state`;
- `file_type`, `stage`, `role`, `lifecycle`, and `presence_policy`;
- `graph_status` and `provenance_status`;
- `created_at`, `reviewed_sha256`, `last_reviewed`,
  `last_known_git_commit`, and `review_method`;
- `inspection_profile` and `inspection_evidence`.

`node_type` is one of `file`, `symlink`, `expected_file`, `logical_asset`,
`pattern`, `external_source`, `external_package`, or `unresolved`. A symlink has
its own ID and an `alias` edge to a scoped target. An absent `expected_file`
remains active. External and unresolved nodes may not use a local
`current_path`.

- A `symlink` has exactly one active target-to-symlink `alias` edge; its target
  must itself be a registered scoped node.
- A `file` or `symlink` uses `presence_policy = "required"`.
- An `expected_file` uses `presence_policy = "expected-output"` and records
  `last_observed_presence = "present"` or `"absent"`.
- A `pattern` records `pattern`, a governed `base_path`, `resolution_status`,
  and the manually enumerated local file IDs in `matches`. The relative glob may
  not escape its base path, and each match is also connected to the pattern by
  an active `membership` edge so lineage traversal can reach the concrete files.
- A `logical_asset` has active member-to-asset `membership` edges and one asset
  overlay. External and unresolved nodes carry explicit source/package
  identifiers or a gap description.

A retired local node has no `current_path`. It retains `last_known_path`,
`retired_at`, `last_reviewed_sha256`, `last_known_git_commit`, and the original
classification. If it was replaced, `superseded_by` points to the successor's
immutable ID. Reusing a retired path for a different logical file requires a new
ID. Restoring the same logical file may reactivate the old ID only after manual
confirmation.

`reviewed_sha256` is the SHA-256 of the file bytes at manual review time,
prefixed with `sha256:`. For a symlink it hashes the link target text without
dereferencing it. A mismatch makes the graph stale. Ledger control files
are schema-validated rather than self-hashed because they are outside the graph.

## File events and path history

Append-only `[[file_events]]` records use UUID-backed IDs and contain
`node_id`, `event`, `occurred_at`, and `observed_commit`. Events are `created`,
`moved`, `deleted`, `restored`, or `superseded`.

- `created` and `restored` require `to_path`.
- `moved` requires `from_path` and `to_path`.
- `deleted` requires `from_path` and a source-grounded `reason`.
- `superseded` requires `from_path`, `successor_id`, and `reason`.

Events for a node must form one continuous chronological path history. The
timestamps within one node's history must be distinct so order never depends on
an arbitrary UUID tie-break. The
latest event must agree with the node's materialized active or retired state.
The first event agrees with `created_at`; a terminal deletion or supersession
agrees with `retired_at`, `last_known_path`, and `last_known_git_commit`.
Events are never rewritten to conceal a move or deletion. If an untracked file
was deleted before its bytes or Git revision were preserved, retire it with
`graph_status = "missing-blocker"`.

## Activities

An `[[activities]]` record is a manually inspected production step. Required
fields are `id`, `revision_id`, `kind`, `status`, `valid_from`, `producer`, all
relationship lists, `reproduction_command`, `producer_sha256`,
`producer_revision`, `graph_status`, `reviewed_at`, `review_method`, and
`evidence`. Lists are `reads`, `imports`, `sources`, `includes`, `configures`,
`writes`, and `invoked_by`. All values are node IDs; out-of-scope repository
files are not added as nodes merely to satisfy a relationship.
The producer must be an executable file or symlink under a governed data-code
root. Every production and activity-derived relationship is recorded through
an activity revision, never as a standalone authored edge.
Executable code and activity revisions use
`review_method = "manual-source-inspection"`; parser- or tracer-generated
dependency attestations are invalid.

When a producer moved within a historical revision, optional `producer_path`
records its path at `producer_revision`; otherwise validation reconstructs its
last active path before `valid_to`. In a Git checkout, historical activities
and tombstones are checked against the recoverable blob and attested SHA-256.

When an activity's dependency contract changes materially, retain `id`, close
the old revision with `valid_to`, and add a new `revision_id`. Activities project
to direct upstream-to-downstream edges:

| Activity field | Direct relationship |
|---|---|
| input in `reads` to producer | `data_read` |
| helper in `imports` to producer | `local_import` |
| file in `sources` to producer | `source_include` |
| file in `includes` to producer | `source_include` |
| configuration in `configures` to producer | `configuration` |
| invoker in `invoked_by` to producer | `invocation` |
| producer to output in `writes` | `production` |
| input in `reads` to output | `generation_input` |
| helper in `imports` or `sources` to output | `generation_code` |
| configuration in `configures` to output | `generation_config` |

## Direct edges

Use `[[edges]]` for relationships not represented by activities. Every edge has
an immutable `id`, `upstream`, `downstream`, `relationship`, `edge_class`,
`valid_from`, `status`, `provenance_relevance`, `operational_relevance`, and
source-grounded `evidence`. Historical edges also have `valid_to` and
`operational_relevance = false`.

Allowed non-production relationships are `pinning`, `membership`, `alias`,
`defines`, and `supersedes`. Document inclusion, documentation,
bibliography, citation, figure inclusion, and other publication-only relations
are intentionally outside this graph. Reverse adjacency is always derived and
must never be authored.

Active operational edges may not depend on retired required nodes. Historical
provenance edges may reach retired nodes. Causal production relationships must
be acyclic; membership, alias, and supersession relationships
are excluded from causal cycle checks.

## Data-asset overlay

Every real data-bearing file or logical dataset has one
`assets/<asset_id>.toml` overlay keyed by `node_id`, plus a narrative dossier.
Structured data, rasters, model outputs, tables, and figure data enumerate every
queryable variable, field, code, layer, band, or output measure. Definitions,
units, missing values, derivations, and allowed coded values must cite actual
source evidence. A complete variable has nonempty identity, definition, unit,
derivation, and source-evidence fields, and its dossier contains a nonempty
source-grounded narrative. Use `partial-flagged` or `missing-blocker` rather than filling
gaps from memory. Empty `.gitkeep` scaffold markers and directory documentation
are explicitly excluded from graph-node coverage.
The overlay `format` must agree with its linked node's `file_type`; structured
variable coverage is derived from both fields, so relabeling an overlay cannot
hide columns or other nested units.
Variable IDs and names are unique within each asset overlay.

## Freshness and query semantics

Strict validation checks scoped coverage, unique IDs and active paths, event
continuity, hashes, node references, temporal consistency, duplicate direct
relationships, asset overlays, and causal cycles. `show`, `lineage`,
`producers`, and `raw-sources` include provenance-relevant historical edges and
label retired nodes. `impact` uses current operational edges unless historical
traversal is requested. `rebuildability` distinguishes known historical lineage
from a currently executable pipeline. A stale graph may provide labeled
last-known information but is not authoritative.

Hook validation may update only `.cache/asset-graph/hash-cache-v1.json`, which
is ignored by Git. Its stat key includes size, mtime, ctime, inode, mode, and
symlink target; CI and `make provenance` always rehash bytes without the cache.
The `[storage]` lists are authoritative, and every listed path must remain
beneath `docs/data/provenance-ledger/`.
