---
paths:
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/appendices/**/*.tex"
  - "docs/deliverables/slides/**/*.tex"
  - "docs/work/reviews/**"
---

# Proofreading Protocol (Paper, Appendices, Talks)

Before commits that modify manuscript, appendix, or talk content, run a proofreading pass.

## What To Check

1. Grammar and phrasing clarity
2. Typos and duplicated words
3. Notation consistency with the canonical paper
4. Citation style consistency
5. Style-guide consistency with `.claude/references/personal-style-guide.md`
6. Obvious overflow risk in dense frames, generic slide titles, slide text that should move to notes/backup, final takeaway gaps, or awkward paper line breaks

## Three-Phase Workflow

### Phase 1: Review & Propose (No direct edits)

- Produce a report with: location, current text, proposed fix, category.
- Save report under `docs/work/reviews/`.

### Phase 2: Approve

- User approves all or selected fixes.

### Phase 3: Apply

- Apply only approved edits.
- Re-compile edited files.
