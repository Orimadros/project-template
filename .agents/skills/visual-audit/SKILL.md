---
name: visual-audit
description: Perform adversarial visual audit of Beamer talks for overflow, hierarchy, spacing, and readability issues.
argument-hint: "[TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task", "Bash"]
---

# Visual Audit (Beamer Talk)

## Steps

1. Read `docs/deliverables/slides/$ARGUMENTS`.
2. Compile and inspect warnings, especially overfull boxes.
3. Check that visual emphasis does not distort claims from the canonical paper.
4. Audit for:
   - overflow and density
   - typography consistency
   - box fatigue and visual clutter
   - weak framing transitions
5. Produce a slide-by-slide issue report with severity and fixes.

Prioritize spacing and layout fixes before font-size reduction.
