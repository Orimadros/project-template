---
name: review-paper
description: Comprehensive manuscript review of the canonical paper or an external paper, with referee-style objections and quality components.
argument-hint: "[optional paper path or filename in docs/sources/]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
---

# Manuscript Review

Produce a thorough, constructive review of an academic manuscript.

## Target Resolution

Default to `docs/deliverables/articles/main/main.tex`. If `$ARGUMENTS` is provided, check:

- direct path from `$ARGUMENTS`
- `docs/sources/$ARGUMENTS`
- partial matches under `docs/sources/` and `docs/deliverables/articles/`

If the target resolves to a PDF, follow `.claude/rules/pdf-processing.md`:
create a MarkItDown Markdown version and read that unless visual/layout
information is essential to the review.

## Workflow

1. Read the manuscript and relevant section files.
2. Read `.claude/references/domain-profile.md` and `.claude/references/journal-profiles.md` if available.
3. Evaluate the paper across weighted quality components:
   - Literature 10%
   - Data 10%
   - Identification 25%
   - Code 15%
   - Paper 25%
   - Polish 10%
   - Replication 5%
4. Generate 3-5 referee objections.
5. Save to `docs/work/reviews/paper_review_[sanitized_name].md`.

## Output Format

```markdown
# Manuscript Review: [Paper Title]

**Date:** [YYYY-MM-DD]
**Reviewer:** review-paper skill
**File:** [path]

## Summary Assessment

**Overall recommendation:** [Accept / Minor / Major / Reject]
**Aggregate score:** [0-100]

## Component Scores

| Component | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Literature | 10% | [N] | [notes] |
| Data | 10% | [N] | [notes] |
| Identification | 25% | [N] | [notes] |
| Code | 15% | [N] | [notes] |
| Paper | 25% | [N] | [notes] |
| Polish | 10% | [N] | [notes] |
| Replication | 5% | [N] | [notes] |

## Major Concerns

## Minor Concerns

## Referee Objections

## Suggested Revision Plan
```
