---
paths:
  - "docs/work/plans/**"
---

# Plan-First Workflow

**For any non-trivial task, enter plan mode before writing code.**

## The Protocol

1. **Enter Plan Mode** — use `EnterPlanMode`
2. **Check MEMORY.md** — read any `[LEARN]` entries relevant to this task
3. **Draft the plan** — resolve ambiguity first (see below), then write what changes, which files, in what order
4. **Save to disk** — write to `docs/work/plans/YYYY-MM-DD_short-description.md` using `docs/work/templates/plan.md`
5. **Present to user** — wait for approval
6. **Exit plan mode** — only after approval
7. **Save initial session log** — capture goal and key context while fresh
8. **Implement via orchestrator** — see the "Orchestrator protocol (contractor mode)" entry under Standing Rules in `AGENTS.md`

## Resolving Ambiguity Before Drafting

Every plan file includes a **Clarity Status** table and MUST/SHOULD/MAY requirements list — there is no separate pre-planning artifact or folder to remember. Fill these in as part of Step 3, before the Approach section, not after.

**When the Clarity Status table needs real entries (not just "CLEAR — user specified"):**
- Task is high-level or vague ("improve the paper", "analyze the data")
- Multiple valid interpretations exist
- Significant effort required (>1 hour or >3 files)

**When it's fine to mark everything CLEAR and move on:**
- Task is clear and specific ("fix typo in line 42")
- Simple single-file edit
- User has already provided detailed requirements

**Protocol:**
1. Use AskUserQuestion to clarify ambiguities (max 3-5 questions) *before* writing the plan's Approach section
2. In the plan file, mark each requirement:
   - **MUST** (non-negotiable)
   - **SHOULD** (preferred)
   - **MAY** (optional)
3. In the plan file, declare clarity status for each major aspect:
   - **CLEAR:** Fully specified
   - **ASSUMED:** Reasonable assumption (user can override)
   - **BLOCKED:** Cannot proceed until answered
4. If any aspect is BLOCKED, do not proceed to the Approach section — resolve it first
5. Get user approval on the whole plan (requirements + approach together)

**Why this helps:** Catches ambiguity BEFORE the approach is drafted, without adding a second file/folder that's easy to skip. A prior version of this rule used a separate `docs/work/task_requirements/` file for this step; across nine real plans it was never used, so it was folded into the plan template instead.

## Plans on Disk

Plans survive context compression. Save every plan to:

```
docs/work/plans/YYYY-MM-DD_short-description.md
```

Use `docs/work/templates/plan.md`: Status (DRAFT/APPROVED/COMPLETED), Clarity Status, MUST/SHOULD/MAY requirements, approach, files to modify, verification steps.
For data-producing tasks, also list expected Provenance Ledger asset entries and variable/code/layer entries.

## Context Management

### General Principles
- Prefer auto-compression over `/clear`
- Save important context to disk before it's lost
- `/clear` only when context is genuinely polluted

### Context Survival Strategy

**Before Auto-Compression:**
When approaching context limits, ensure:
1. MEMORY.md has all `[LEARN]` entries from this session
2. Session log is current (updated within 10 minutes)
3. Active plan is saved to disk
4. Open questions are documented in session log

The pre-compact hook will remind you of this checklist.

**After Compression:**
First message should be: "Resuming after compression. Last task: [read most recent plan + git log]. Status: [next step]."

## Session Recovery

After compression or new session:
1. Read `CLAUDE.md` + most recent plan in `docs/work/plans/`
2. Check `git log --oneline -10` and `git diff`
3. State what you understand the current task to be
