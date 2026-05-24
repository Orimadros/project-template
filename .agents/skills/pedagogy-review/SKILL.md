---
name: pedagogy-review
description: Run narrative/delivery review on research-talk slides. Checks story arc, audience prerequisites, examples, notation clarity, and pacing.
argument-hint: "[TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Talk Narrative Review (Beamer slides)

## Steps

1. Resolve `$ARGUMENTS` to a file in `docs/deliverables/slides/`.
2. Launch the `pedagogy-reviewer` agent on that file.
3. Save report to:
   - `docs/work/reviews/[FILENAME]_pedagogy_report.md`
4. Summarize:
   - strongest points
   - top pedagogical risks
   - 3-5 prioritized recommendations

Read-only review: do not edit source files.
