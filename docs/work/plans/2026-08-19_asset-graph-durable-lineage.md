# Asset Graph With Durable Historical Lineage

**Date:** 2026-08-19
**Status:** COMPLETED

---

## Objective

Upgrade the Provenance Ledger into a manually maintained, queryable dependency graph for pipeline code, data, and results, with immutable file identities and durable lineage through moves and deletions.

## Clarity Status

| Aspect | Status | Notes |
|--------|--------|-------|
| Governed scope | CLEAR | User limited graph nodes to `code/00_fetch`, `code/01_build`, `code/02_analyze`, `code/99_explorations`, `data`, and `results`. |
| Discovery | CLEAR | Agents inspect dependencies manually; tooling validates and queries but does not infer relationships. |
| Historical identity | CLEAR | Every file has an immutable UUID; moves retain it and deletions become queryable tombstones. |
| Inspection workflow | CLEAR | Read-only inspection skill queries committed TOML records and fails fast on stale records. |

## Requirements

### MUST Have (Non-Negotiable)
- [x] Exactly one immutable node ID for every governed current file.
- [x] Typed upstream-to-downstream edges with derived reverse adjacency.
- [x] Durable path history, retired nodes, and historical producer relationships.
- [x] Manual dependency maintenance with hook notifications for create/change/move/delete events.
- [x] Preserve variable-level asset metadata and narrative dossiers.
- [x] Exclude documents, placeholders, Makefile, skills, hooks, and ledger control files from graph-node coverage.

### SHOULD Have (Preferred)
- [x] Compact CLI queries for lineage, producers, raw sources, impact, history, and rebuildability.
- [x] Deterministic JSON/TOML/DOT output and representative fixtures.
- [x] Cross-harness maintenance and inspection skills.

### MAY Have (Optional, If Time)
- [x] Date-filtered historical views when temporal metadata is available.

## Approach

1. Replace the v1 index/checker with a v2 schema, grouped manifests, graph library, CLI, and advisory-to-strict validation.
2. Explicitly exclude the template's `.gitkeep` placeholders and exploration README; the baseline registry remains empty until substantive data code, data, or results exist.
3. Add maintenance notifications and the read-only `inspect-asset-graph` skill; update the existing provenance workflow.
4. Update Make targets, rules, agents, and user documentation without expanding graph scope.
5. Run fixtures, provenance/conformance gates, independent review, and repair all blocking findings.

## Files Expected To Change

- `docs/data/provenance-ledger/**`
- `code/03_quality/check_provenance_ledger.py`
- `code/03_quality/asset_graph_lib/**`
- `.agents/skills/{provenance-ledger,inspect-asset-graph}/**` and `.claude/skills/inspect-asset-graph`
- `.agents/hooks/provenance-reminder.py`, `.claude/settings.json`, `.codex/hooks.json`
- `Makefile`, rules, agent definitions, `README.md`, `AGENTS.md`, and `docs/sources/USER-GUIDE.md`

## Verification

- [x] `python3 -m unittest discover -s code/03_quality/tests -p 'test_asset_graph*.py'`
- [x] `make provenance`
- [x] `make check`
- [x] Query smoke tests for current, moved, and retired producers.
- [x] Independent code/data review and final re-verification.

## Provenance Ledger Impact

- **Affected assets:** none at the empty template baseline; future substantive files under pipeline code, `data/`, and `results/` are governed
- **Nested records required:** `.gitkeep`/README scaffold files are explicitly excluded; existing asset-variable requirements remain in force
- **Expected status:** complete

## Approval

[x] User approved: 2026-08-19, with graph scope narrowed to data code, data, and results.
