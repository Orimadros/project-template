---
name: slide-excellence
description: Multi-agent Beamer talk review for derivative decks: paper consistency, visual quality, pedagogy, proofreading, and TikZ.
argument-hint: "[TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
context: fork
---

# Slide Excellence (Paper-Derived Beamer Talk)

## Steps

1. Resolve `$ARGUMENTS` to `docs/deliverables/slides/*.tex`.
2. Read `docs/deliverables/articles/main.tex` and relevant section files for source-of-truth claims.
3. Run these reviews in parallel:
   - storyteller-critic -> paper consistency and talk arc
   - slide-auditor -> visual/layout
   - pedagogy-reviewer -> research-audience narrative flow
   - proofreader -> language/notation
   - tikz-reviewer (if TikZ present)
4. Save reports under `docs/work/reviews/`.
5. Synthesize a single prioritized action list:
   - critical blockers
   - medium improvements
   - polish items

Return a concise readiness judgment: READY / NEEDS WORK.

> For the manuscript itself, use `/review paper` or `/review-paper`.
