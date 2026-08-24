# Session Log: Merge task_requirements Into the Plan Template

**Date:** 2026-08-14

## Goal

Fix `plan-first-workflow.md` Step 3 (task requirements) never actually being used — 9 plans existed in `docs/work/plans/`, 0 files existed in `docs/work/task_requirements/`.

## Key Decision

Root cause was two-fold: (1) the step was a self-graded soft instruction with no mechanical enforcement, unlike the hook-enforced raw-data lock; (2) it directly conflicts with the "Auto Mode" system bias toward proceeding without pausing to ask. User chose to fix this by merging the Clarity Status / MUST-SHOULD-MAY sections directly into the plan file itself (new `docs/work/templates/plan.md`), removing the separate file/folder rather than adding a hard hook gate or dropping the concept entirely.

## Scope

`.claude/rules/plan-first-workflow.md`, new `docs/work/templates/plan.md`, deleted `docs/work/templates/task-requirements.md` and the empty `docs/work/task_requirements/` folder, and reference cleanup across CLAUDE.md, AGENTS.md, `.claude/rules/quality-gates.md`, `docs/sources/USER-GUIDE.md`, README.md. No code or data changes.

## Verification

`grep -rln "task_requirements|task-requirements|task requirement" -i .` (excluding `.git/`) returns only the intentional historical-explanation sentence left in `plan-first-workflow.md`. Full plan and rationale recorded in [docs/work/plans/2026-08-14_merge-task-requirements-into-plan-template.md](../plans/2026-08-14_merge-task-requirements-into-plan-template.md).


---
**Context compaction (manual) at 10:56**
Check git status/log and docs/work/plans/ for current state.
