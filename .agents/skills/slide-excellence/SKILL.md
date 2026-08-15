---
name: slide-excellence
description: Multi-agent Beamer talk review for derivative decks: paper consistency, slide-writing principles, visual quality, pedagogy, proofreading, and TikZ.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Slide Excellence (Paper-Derived Beamer Talk)

## Steps

1. Resolve `$ARGUMENTS` to `docs/deliverables/slides/*/*.tex`.
2. Read `docs/deliverables/articles/main/main.tex` and relevant section files for source-of-truth claims.
3. Read `.claude/rules/slide-writing-principles.md` and `docs/deliverables/preambles/beamer-preamble.tex`.
4. Run these reviews in parallel:
   - storyteller-critic -> paper consistency, Big 5 opening, contribution framing, and talk arc
   - slide-auditor -> layout, data-graphics integrity, table readability, accessibility beyond color, section-divider style, overlays, and backup placement
   - pedagogy-reviewer -> research-audience narrative flow, intuition bridge, pacing, first-five-minutes clarity, and final takeaway
   - proofreader -> language/notation
   - tikz-reviewer (if TikZ present)
5. Save reports under `docs/work/reviews/`.
6. Synthesize a single prioritized action list:
   - critical blockers
   - medium improvements
   - polish items

Return a concise readiness judgment: READY / NEEDS WORK, including whether the deck satisfies the slide-writing principles, especially opening architecture and empirical graphics credibility.

> For the manuscript itself, use `/review paper` or `/review-paper`.
