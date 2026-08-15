# Merge task_requirements Into the Plan Template

**Date:** 2026-08-14
**Status:** COMPLETED

---

## Objective

Stop losing the "resolve ambiguity before planning" step by folding it into the plan file itself, since the separate `docs/work/task_requirements/` file was never used across 9 real plans.

---

## Clarity Status

| Aspect | Status | Notes |
|--------|--------|-------|
| Fix approach (merge vs. hook vs. explicit-skip vs. drop entirely) | CLEAR | User chose "merge into plan template" via AskUserQuestion |
| Whether to remove the `docs/work/task_requirements/` folder itself | ASSUMED | User said "merge," implying the separate folder becomes redundant; folder removed along with the template file. User can restore if they wanted the folder kept as a no-op |
| Whether existing plans should be retroactively updated | ASSUMED | No — only new plans use the new template; the 9 existing plans stay as historical record |

## Requirements

### MUST Have (Non-Negotiable)
- [x] New plans include a mandatory Clarity Status table and MUST/SHOULD/MAY requirements section, without a separate file to create
- [x] `.claude/rules/plan-first-workflow.md` no longer references a separate `docs/work/task_requirements/` step
- [x] All references to `docs/work/task_requirements/` removed repo-wide (CLAUDE.md, AGENTS.md, quality-gates.md, USER-GUIDE.md, README.md)

### SHOULD Have (Preferred)
- [x] The rule file explains *why* the change was made (so a future session doesn't reintroduce the old pattern)

### MAY Have (Optional, If Time)
- [ ] Retroactively backfill Clarity Status tables into the 9 existing plans — not done; out of scope, historical plans left as-is

---

## Approach

1. Confirm the empirical claim (9 plans, 0 task_requirements files) and inspect one plan ([2026-08-07_pipeline-script-naming.md](2026-08-07_pipeline-script-naming.md)) for a concrete example of silently-resolved ambiguity.
2. Diagnose root cause: the step was a self-graded soft instruction with no mechanical gate, and directly conflicts with the "Auto Mode" bias toward not stopping to ask.
3. Ask the user to choose a fix among: merge into plan template / mechanical hook gate / explicit skip logging / drop entirely.
4. Create `docs/work/templates/plan.md`, merging the old `task-requirements.md` template's Clarity Status + MUST/SHOULD/MAY sections into the existing freeform plan structure (Objective, Approach, Files Expected To Change, Verification, Provenance Ledger Impact, Approval).
5. Rewrite `.claude/rules/plan-first-workflow.md`: remove the separate Step 3, fold ambiguity resolution into Step 3 "Draft the plan," renumber remaining steps.
6. Delete `docs/work/templates/task-requirements.md` and the empty `docs/work/task_requirements/` folder.
7. Remove all other references to the old convention (folder-tree diagrams and prose) in CLAUDE.md, AGENTS.md, `.claude/rules/quality-gates.md`, `docs/sources/USER-GUIDE.md`, README.md.
8. Verify no dangling references remain.

## Files Expected To Change

- `.claude/rules/plan-first-workflow.md`
- `docs/work/templates/plan.md` (new)
- `docs/work/templates/task-requirements.md` (deleted)
- `docs/work/task_requirements/.gitkeep` (deleted)
- `CLAUDE.md`
- `AGENTS.md`
- `.claude/rules/quality-gates.md`
- `docs/sources/USER-GUIDE.md`
- `README.md`

## Verification

- [x] `grep -rln "task_requirements|task-requirements|task requirement" -i .` (excluding `.git/`) returns only the intentional historical explanation sentence in `plan-first-workflow.md`
- [x] `docs/work/templates/plan.md` renders the same sections the old two-file flow produced (Clarity Status, MUST/SHOULD/MAY, plus the original Approach/Files/Verification/Provenance fields)
- [ ] Not run: `make provenance` / `make articles` / `make slides` — no data-bearing or LaTeX content touched by this change

## Provenance Ledger Impact

- **Affected assets:** N/A — documentation/rules/template change only, no data or code
- **Nested records required:** N/A
- **Expected status:** N/A

---

## Approval

[x] User approved: 2026-08-14 (approved the "merge into plan template" approach via AskUserQuestion; implementation proceeded under Auto Mode without a separate plan-mode pause)
