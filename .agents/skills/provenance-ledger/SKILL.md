---
name: provenance-ledger
description: Maintain immutable file identity, historical dependency lineage, and source-grounded asset and variable provenance for data code, data, and results. Use when files under code/00_fetch, code/01_build, code/02_analyze, code/99_explorations, data, or results are created, changed, moved, restored, deleted, generated, reviewed, or found stale; also use for unresolved variable meanings, codes, units, missing values, or generation procedures.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Provenance Ledger

Maintain `docs/data/provenance-ledger/` manually. Govern only files under
`code/00_fetch/`, `code/01_build/`, `code/02_analyze/`,
`code/99_explorations/`, `data/`, and `results/`. Documents may provide evidence
for asset definitions, but they and repository-control placeholders are not graph nodes. Never infer or write
dependencies with an automated parser or tracer.

**Arguments:** [affected path, immutable node ID, hook finding, or variable/code question]

## Maintenance Workflow

1. Read `.claude/rules/provenance-ledger.md`, the ledger index, and the hook's
   affected-path report. Run
   `python3 code/03_quality/asset_graph.py validate --format json`.
2. Resolve the previous node by immutable ID, current or former path, and
   reviewed hash. Inspect the affected file and its immediate producer/consumer
   neighborhood only.
3. Classify the change:
   - **New logical file:** generate a new UUID-backed ID and append `created`.
   - **Move/rename:** confirm identity, retain the ID, update `current_path`, and
     append `moved`. Treat hash/Git matches as suggestions, not proof.
   - **Delete:** retain the node as a tombstone, set `state = "retired"`, retain
     its last path/hash/Git revision, and append `deleted`.
   - **Restore:** reactivate the confirmed prior ID and append `restored`.
   - **Path reuse:** create a new ID; never reassign the retired identity.
   - **Absent expected output:** retain its active ID and expected-output state;
     do not retire it.
4. Manually update activities and upstream-to-downstream edges. Preserve
   historical revisions and close their validity intervals instead of erasing
   them. Active operational edges may not require retired producers; historical
   provenance edges may reference tombstones.
5. For data-bearing assets, update the `node_id` overlay, dossier, and every
   queryable variable/field/band/class with source-grounded units, codes,
   missing-value rules, derivations, and evidence. Use `partial-flagged` or
   `missing-blocker` for unresolved facts.
6. Record the inspection profile, evidence locator, review date, and current
   SHA-256 only after completing manual inspection.
7. Run `make provenance`. Route material pipeline-lineage changes through the
   project's independent review workflow.

## Manual Inspection Checklist

- R: `source()`, packages, readers/writers, constructed paths, and system calls.
- Python: local imports, file readers/writers, `open`, `pathlib`, subprocesses,
  and constructed paths.
- Julia: `include()`, imports, file operations, and processes.
- Shell: sourced files, invoked scripts, redirections, and file arguments.
- Make-driven pipeline behavior: invokers, prerequisites, recipes, and outputs
  that touch the governed roots.
- Notebooks/configuration within governed roots: referenced inputs, helpers,
  outputs, and dynamic path expressions.

Represent unresolved dynamic paths explicitly; do not guess. Never overwrite,
edit, delete, rename over, or chmod an existing file under `data/raw/`.
