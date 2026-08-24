---
name: inspect-asset-graph
description: Read the repository Asset Graph to answer lineage questions about data code, data, and results. Use for questions such as what produced a file, which raw data it depends on, which scripts or helpers were involved, what depends on it, where a moved file used to live, whether a deleted script produced it, whether it remains rebuildable, or what its lineage was at a date.
---

# Inspect Asset Graph

Use the committed graph as the sole dependency reference for paths under
`code/00_fetch/`, `code/01_build/`, `code/02_analyze/`,
`code/99_explorations/`, `data/`, and `results/`. The skill is read-only.

## Workflow

1. Run `python3 code/03_quality/asset_graph.py validate --format json --hook`.
   This performs the full validation contract while using only the ignored,
   stat-keyed digest cache for unchanged large files; it never changes graph
   records.
2. If validation returns `status = "fail"` or any error finding, stop and report
   the structural or provenance blockers. Do not attempt a normal query. If any
   finding has `stale = true`, report last-known graph
   facts as non-authoritative only when useful, list the stale records, and
   direct maintenance to `$provenance-ledger`. Do not inspect source files to
   fill gaps. If the user explicitly needs last-known data, rerun only the
   narrowest query with `--allow-stale` before the command, for example
   `python3 code/03_quality/asset_graph.py --allow-stale show PATH_OR_ID`.
   If validation instead passes with warnings, the query may proceed, but report
   every warning and preserve the CLI result's `authoritative = false` label.
3. Run the narrowest query that answers the question:

   | Question | Command |
   |---|---|
   | Node and immediate relationships | `show PATH_OR_ID --format agent` |
   | Former locations or lifecycle | `path-history PATH_OR_ID` |
   | Direct or transitive inputs | `upstream PATH_OR_ID --depth 1\|all` |
   | Direct or transitive consumers | `downstream PATH_OR_ID --depth 1\|all` |
   | Full ancestry | `lineage PATH_OR_ID [--as-of YYYY-MM-DD]` |
   | Ultimate files under `data/raw/` | `raw-sources PATH_OR_ID` |
   | Pipeline entry scripts and helpers | `producers PATH_OR_ID` |
   | A script's reads/imports/config/writes | `script-io PATH_OR_ID` |
   | Current affected descendants | `impact PATH_OR_ID` |
   | Current plus historical descendants | `impact PATH_OR_ID --include-historical` |
   | Whether the asset can be regenerated now | `rebuildability PATH_OR_ID` |
   | Disconnected nodes | `orphans` |
   | Known graph gaps | `unresolved` |
   | Machine or visual export | `export --format json\|dot` |

   Prefix each query with `python3 code/03_quality/asset_graph.py`.
4. Default to compact agent output. Use `--format json` where a command supports
   structured follow-up, `show --format toml` for a node record, and DOT only
   when a graph visualization is requested.

## Reporting

- Give exact repository-relative paths and immutable node IDs.
- Distinguish immediate from transitive relationships and current operational
  edges from historical provenance edges.
- For a retired node, include its last path, retirement date, last known Git
  revision, successor when recorded, and the reported recovery command.
- For rebuildability, distinguish known historical provenance from a currently
  runnable pipeline.
- Treat documents, `code/03_quality/`, and all paths outside the governed roots
  as out of scope; do not search them or add them to the graph.
- Never edit manifests, regenerate graph metadata, or scan the repository to
  compensate for missing or stale records.
