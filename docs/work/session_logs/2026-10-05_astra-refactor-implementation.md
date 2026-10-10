# 2026-10-05: Template workflow refactor

## What changed

- Replaced the broad root instructions, path-scoped rules, automatic learning,
  most hooks, and redundant agent roles with a short `AGENTS.md`, 19 scoped
  skills, two named agents, and one raw-file guard.
- Added one issue-linked, immutable change contract per tracked change; candidates
  live under `pending-approval/`, and shipping names the exact subset to accept.
  Small exact edits and exploration can work directly without that route.
- Added R, Python, and Julia helpers that record registered direct input paths
  and modification times beside each generated output. Failed, missing-output,
  and stale-output runs cannot leave a new success marker.
- Retired the Asset Graph and Provenance Ledger, updated Make and CI, and rewrote
  the active guides and templates around the new workflow.

## Decisions and discoveries

- Leo chose moving the reviewed output to production during `ship` and writing
  factual session logs at the end of substantial work.
- An independent review found gaps in candidate identity, deletions, partial
  shipping with dependent scripts, and stale navigation text. Review now
  records candidate SHA-256 digests; shipping verifies them and stops if a
  requested subset would strand pending work.
- The first real GitHub issue will be the live test of creation, partial
  shipping, closure, and `sitrep`; no disposable issue or commit was created.

## Checks

- `make check`: passed, including ten tests. R and Julia were available and
  their helper examples ran.
- `make all`: passed on the empty template pipeline.
- `make articles` and `make slides`: compiled their template documents.
- `git diff --check` and Codex agent-generation check: passed.

## Still open

- Exercise the issue-to-closure lifecycle on the first real tracked change.
