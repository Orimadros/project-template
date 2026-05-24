---
name: proofread
description: Run proofreading protocol on the canonical paper, appendices, and derivative Beamer talks. Produces a report without editing files.
argument-hint: "[filename, 'paper', or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Proofread Paper, Appendices, And Talks

## Steps

1. Identify files:
   - If `$ARGUMENTS` is `paper` or empty, review `docs/deliverables/articles/main.tex` and section files.
   - If `$ARGUMENTS` is a filename, review only that file.
   - If `$ARGUMENTS` is `all`, review `.tex` files in `docs/deliverables/articles/`, `docs/deliverables/appendices/`, and `docs/deliverables/slides/`.

2. Review for:
   - Grammar and wording clarity
   - Typos / duplicated words
   - Notation and citation consistency
   - Style-guide consistency with `.claude/references/personal-style-guide.md`
   - Overlong lines and awkward spacing in papers
   - Overflow risk in dense Beamer frames

3. Produce a report with:
   - location
   - current text
   - proposed fix
   - category/severity

4. Save report to `docs/work/reviews/[FILENAME]_proofread_report.md`.

5. Do not edit source files in this step.
