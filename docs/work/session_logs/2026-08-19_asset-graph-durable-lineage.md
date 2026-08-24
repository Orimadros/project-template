# Session Log: 2026-08-19 -- Asset Graph Durable Lineage

**Status:** COMPLETED

## Objective

Implement a manually maintained, queryable dependency graph for pipeline code, data, and results with immutable file IDs and historical lineage through moves and deletions.

## Changes Made

| File | Change | Reason | Quality Score |
|------|--------|--------|---|
| `docs/data/provenance-ledger/**` | Added v2 policy, grouped registries, history, schema, and templates | Durable identity and manually maintained lineage | 96/100 |
| `code/03_quality/asset_graph*` | Added strict validator, query engine, CLI, and 24-test fixture suite | Query historical lineage without repository-wide inspection | 96/100 |
| `.agents/hooks/`, `.agents/skills/`, `.codex/`, `.claude/` | Added maintenance notifications and read-only inspection workflow | Keep the graph fresh across both harnesses | 96/100 |
| Make/CI/rules/guides | Integrated graph validation and documented the narrowed scope | Make the workflow reproducible and discoverable | 96/100 |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Govern only pipeline/data/result roots | Whole-repository graph | User explicitly excluded documents and other repository infrastructure. |
| Exclude placeholders and directory documentation | Assign UUIDs to every path under a governed root | These are repository-control/documentation files, not data code, data, or results; explicit exclusions keep coverage exhaustive without polluting lineage. |
| Agent-authored dependency records | Automated static/runtime discovery | User requires the agent to inspect and maintain relationships manually. |
| Immutable UUID plus tombstone | Path-derived identity or deletion | Preserves lineage after moves and producer deletion. |
| Cached hook hashes, uncached CI | Rehash every large asset after every tool call | Stat-keyed ignored cache keeps hooks responsive; `make provenance` and CI still hash bytes directly. |

## Incremental Work Log

**2026-08-19:** Plan approved and narrowed to pipeline code, data, and results before implementation.

**2026-08-19:** Operational rules now treat exploration files as governed while keeping papers, slides, work documents, Makefile, hooks, skills, and ledger control files outside graph-node coverage.

**2026-08-19:** Independent review showed the empty scaffold should not create graph noise. Added explicit exclusions for `.gitkeep` and the exploration README; the template baseline now has zero substantive graph nodes.

**2026-08-19:** Hardened strict validation for typed IDs and fields, authoritative storage paths, lifecycle continuity and non-overlap, supersession, Git-recoverable tombstone/activity hashes, temporal node lifetimes, symlink aliases, expected outputs, structured asset overlays/dossiers, and malformed-policy fail-fast behavior.

**2026-08-19:** Separated current operational rebuildability/script I/O from historical lineage, reconstructed state in as-of views, made default agent output compact, and expanded end-to-end fixtures from 10 to 24 cases.

**2026-08-19:** Independent code and data reviews each scored 96/100 with no critical or major findings. Closed the actionable minor findings for workdir-aware hooks, broader code attestation, structured-overlay disguises, duplicate variable identities, and ambiguous same-time lifecycle events.

## Learnings & Corrections

- [LEARN:provenance] Repository-wide graph coverage -> govern only pipeline code, data, and results; documents and control infrastructure are outside the graph.

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| Asset Graph unit/integration suite | 24 tests pass | PASS |
| `make provenance` | Strict v2 validation passes | PASS |
| `make check` | Cross-harness conformance passes | PASS |
| Hook validation and simulations | Fresh graph passes; stale UserPrompt/Stop behavior passes | PASS |
| Inspection skill validation | Skill package passes `quick_validate.py` | PASS |
| Independent code/data review | 96/100 each; no critical or major findings | PASS |

## Provenance Ledger

| Asset | Record Updated | Variable/Code/Layer Entries | Status |
|-------|----------------|-----------------------------|--------|
| Template scaffold | Explicitly excluded (no substantive assets) | N/A | complete |

## Open Questions / Blockers

- [x] None.

## Next Steps

- [x] Implement schema, graph tooling, hooks, skills, tests, and documentation.
- [x] Complete final independent re-review and close the session.
