---
name: pedagogy-review
description: Run narrative/delivery review on research-talk slides. Checks story arc, audience prerequisites, examples, notation clarity, and pacing.
argument-hint: "[TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Talk Narrative Review (Beamer slides)

## Steps

1. Resolve `$ARGUMENTS` to a root deck file, usually `docs/deliverables/slides/<deck>/<deck>.tex`.
2. Read `.claude/rules/slide-writing-principles.md`.
3. Launch the `pedagogy-reviewer` agent on that file and ask it to include the slide-writing baseline in the deck-level assessment, especially Big 5 opening, first-five-minutes clarity, intuition bridge, talk-length pacing, early threats/credibility, and final takeaway.
4. Save report to:
   - `docs/work/reviews/[FILENAME]_pedagogy_report.md`
5. Summarize:
   - strongest points
   - top pedagogical risks
   - 3-5 prioritized recommendations

Read-only review: do not edit source files.
