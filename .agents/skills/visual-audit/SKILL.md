---
name: visual-audit
description: Perform adversarial visual audit of Beamer talks for overflow, hierarchy, spacing, and readability issues.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task", "Bash"]
---

# Visual Audit (Beamer Talk)

## Steps

1. Resolve `$ARGUMENTS` to a root deck file, usually `docs/deliverables/slides/<deck>/<deck>.tex`.
2. Read `.claude/rules/slide-writing-principles.md`.
3. Compile and inspect warnings, especially overfull boxes.
4. Check that visual emphasis does not distort claims from the canonical paper.
5. Audit for:
   - overflow and density
   - typography consistency
   - 45-75 character line targets and one-point-per-slide discipline
   - substantive frame titles rather than generic section labels
   - graph/table labels readable from a seminar room
   - data-graphics integrity: direct labels, low clutter, appropriate chart type, visible units/transformations/uncertainty, and correct baselines
   - slide tables rounded, decimal-aligned, and large enough for the room
   - color-blind-conscious and semantically consistent accents that do not carry meaning by hue alone
   - box fatigue and visual clutter
   - weak framing transitions
   - section dividers that do not use `\sectiontransition[optional subtitle]{Title}` from the shared preamble
   - end-of-bullet references not de-emphasized with `\smallcitation`, or `\smallcitation` misapplied to a load-bearing inline citation
   - full-slide high-saturation transition frames, especially yellow/blue blocks
   - backup placement for dense proofs, robustness, and full tables
   - controlled overlays only when they clarify a figure/table build
   - no dependence on visible buttons, mouse access, or live interaction during the main talk
6. Produce a slide-by-slide issue report with severity and fixes.

Prioritize spacing and layout fixes before font-size reduction.
