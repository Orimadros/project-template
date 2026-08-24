# Asset Graph independent code review

**Date:** 2026-08-19  
**Reviewer role:** code critic  
**Decision:** Pass; ready for PR review  
**Score:** 96/100  
**Blockers:** None

## Scope

This review covers `code/03_quality/asset_graph.py`, `code/03_quality/asset_graph_lib/`, the integration in `code/03_quality/check_provenance_ledger.py`, the Asset Graph test suite, Make/CI targets, the shared provenance hook contract, and the `inspect-asset-graph` command map.

The implementation correctly constrains graph coverage to:

- `code/00_fetch`
- `code/01_build`
- `code/02_analyze`
- `code/99_explorations`
- `data`
- `results`

Documents, `code/03_quality`, hooks, skills, and other control-plane files remain outside Asset Graph node coverage. The graph tooling validates and queries manually authored TOML; it does not infer or write semantic dependency relationships.

## Findings

### Critical

None.

### Major

None.

### Minor

1. **Variable identities and names are not required to be unique within an asset overlay.**

   `code/03_quality/asset_graph_lib/validation.py:1018` validates every `[[variables]]` record independently, but the loop through line 1073 never checks duplicate variable `id` or `name` values. A temporary fixture with the same variable table appended twice produced no findings. Duplicate queryable units could make field-level provenance ambiguous. Add per-asset uniqueness checks for normalized variable IDs and names.

2. **Historical Git-blob verification bypasses the hash cache and can become expensive as tombstones accumulate.**

   `code/03_quality/asset_graph_lib/validation.py:1197` and `:1239` stream each retired producer blob from Git on every full validation, while the ignored stat-keyed cache only covers current filesystem files. Since the reminder invokes hook validation on every prompt and stop (`.agents/hooks/provenance-reminder.py:164-184`), a mature ledger with many large retired files can approach the 25/30-second hook limits. Cache historical blob digests by immutable Git object identity, or batch the Git-object reads.

3. **Same-timestamp lifecycle events are ordered by random UUID rather than an explicit sequence.**

   `code/03_quality/asset_graph_lib/validation.py:572`, `code/03_quality/asset_graph_lib/validation.py:1260-1263`, and `code/03_quality/asset_graph_lib/graph.py:53-56` break timestamp ties with `event.id`. UUID ordering is deterministic but has no lifecycle meaning, so two legitimate events recorded at the same instant can reconstruct in the wrong order. Reject duplicate timestamps per node or add an append-only sequence field.

## Post-review resolution

- Resolved finding 1: strict validation now rejects duplicate variable IDs and
  names within an asset overlay, with a regression fixture.
- Finding 2 is accepted as an integrity tradeoff: historical Git evidence is
  re-read from its immutable revision during strict validation rather than
  trusting a local cache. Current large files retain the ignored stat-keyed
  cache used by hook/query preflight.
- Resolved finding 3: lifecycle events for one node may not share a timestamp,
  so history never depends on UUID ordering. A regression fixture covers this.

Final post-resolution verification remains 24/24 tests with provenance,
conformance, compilation, skill validation, and diff checks passing.

## Verified behavior

- The strict root allowlist is encoded in `code/03_quality/asset_graph_lib/validation.py:21-28`, enforced against the configured roots at lines 168-190, and matches `docs/data/provenance-ledger/index.toml:9-16` exactly.
- Current governed files require one immutable typed UUID identity, fresh hashes, lifecycle history, and manual source inspection attestations for governed code.
- Moves, restores, deletions, supersession, path reuse, expected outputs, symlink identities, and alias relationships have dedicated fixture coverage.
- Historical activities and production relationships survive producer retirement. `producers`, `lineage`, `script-io`, and `rebuildability` expose historical producers, their last paths, and recovery metadata.
- Current impact follows operational edges; historical impact is opt-in.
- Structural invalidity fails queries with exit code 4. Staleness fails with exit code 3 unless explicitly overridden; the override does not bypass structural errors. Warning-bearing answers are labeled non-authoritative.
- Activity-derived edges are projected from manually authored activity records. Authored duplicates of activity-derived relationships are rejected. No static source parser or runtime tracer writes dependencies.
- Data-bearing overlays and nonempty dossiers are required. Structured formats require variable records with fields, status, units, derivations, code values, and source evidence; overlay format must agree with node `file_type`.
- The shared hook is non-mutating apart from its ignored digest cache, filters non-governed `PostToolUse` operations, respects tool workdirs, and performs full checks on `UserPromptSubmit` and `Stop`.
- CI checks out full Git history, runs the Asset Graph tests, validates provenance, and runs cross-harness conformance.
- The current repository is an intentionally empty template baseline: coverage, orphan, unresolved, and export queries return empty graph data with zero validation findings. Historical-lineage and data-overlay requirements are exercised by the 24-test fixture suite.
- Paper-claim matching and stochastic seeding are not applicable to this infrastructure-only change. No empirical generated outputs were introduced by the implementation.

## Exact verification commands

All commands were run from the repository root.

```bash
make asset-graph-test
make provenance
make check
git diff --check
python3 -m py_compile code/03_quality/asset_graph.py code/03_quality/asset_graph_lib/*.py code/03_quality/check_provenance_ledger.py .agents/hooks/provenance-reminder.py
python3 code/03_quality/asset_graph.py validate --format json
python3 code/03_quality/asset_graph.py coverage --format json
python3 code/03_quality/asset_graph.py orphans --format json
python3 code/03_quality/asset_graph.py unresolved --format json
python3 code/03_quality/asset_graph.py export --format json
python3 code/03_quality/asset_graph.py export --format dot
```

Hook simulations were run by sending JSON payloads for `UserPromptSubmit`, `Stop`, and a non-governed `PostToolUse` operation directly to `.agents/hooks/provenance-reminder.py`. Each exited 0 with no output on the fresh graph.

The duplicate-variable stress test instantiated `FixtureRepository` in a temporary directory, appended an identical `[[variables]]` table to `asset_panel.toml`, reloaded the ledger, and printed `validate_ledger(...)` findings. It returned `[]`.

## Results

- `make asset-graph-test`: 24 tests, all passed.
- `make provenance`: `Provenance Ledger / Asset Graph: PASS`.
- `make check`: `Conformance: PASS`.
- `git diff --check`: passed.
- Python compilation: passed.
- Strict CLI validation: zero errors and zero warnings.
- Coverage, orphan, unresolved, JSON export, and DOT export smoke tests: passed.
- Fresh hook simulations: passed.

## Overall assessment

The implementation satisfies the durable-identity, historical-lineage, manual-maintenance, narrow-scope, and stale-query safety requirements. The remaining findings are bounded hardening improvements; none affects correctness of the current acceptance fixtures or blocks merge.
