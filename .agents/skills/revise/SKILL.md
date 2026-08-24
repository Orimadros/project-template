---
name: revise
description: Convert reviews into a classified revision plan and, when asked, implement paper/code/talk revisions.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Revise

Use this after a review report, referee report, or internal critic pass.

**Arguments:** [review report path or revision goal]

## Workflow

1. Read the target review report or infer the active review from `docs/work/reviews/`.
2. Classify comments as `NEW ANALYSIS`, `CLARIFICATION`, `DISAGREE`, or `MINOR`.
3. Create a revision plan in `docs/work/plans/` for non-trivial revisions.
4. Route implementation:
   - `NEW ANALYSIS` -> strategist/coder/provenance-ledger/coder-critic/verifier
   - `CLARIFICATION` -> writer/writer-critic
   - `DISAGREE` -> strategist/methods-referee/editor
   - `MINOR` -> proofread/compile
5. Verify with Make and/or LaTeX compile.

## Output

- Comment classification table
- Files changed or planned
- Asset Graph identity/lineage updates for governed code/data/results changes, plus variable-level provenance when data-bearing assets change
- Commands run
- Remaining open decisions
