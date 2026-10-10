---
name: write-slides
description: Create or revise a Beamer talk derived from the canonical paper and generated results.
disable-model-invocation: true
---

# Write a research talk

Use this when Leo asks for a new or revised Beamer deck. The deck derives from the
canonical paper and generated results; it may change order and emphasis for its
audience, but it does not add unsupported claims.

## Workflow

1. Resolve the deck path and scope. For a new talk, establish or infer from the request
   the audience, duration, talk type, project status, and goal. Ask Leo about any
   missing detail that would materially change the talk; state reasonable minor
   assumptions and proceed.
2. Read `CONTEXT.md`, the relevant canonical paper sections, generated outputs used in
   the talk, the shared Beamer preamble, and
   `../../references/slide-writing-principles.md`. Read existing slides when revising a
   deck. Use `../../references/tikz-visual-quality.md` if creating or changing TikZ.
3. Build the opening and arc from settled paper content. Establish the question, stakes,
   gap, contribution, headline answer, and main credibility threat early. Add an
   intuition bridge before dense technical material. Match the number and depth of
   claims to the time and audience.
4. Create or edit the requested `.tex` source. By default, put a new deck at
   `docs/deliverables/slides/<deck>/<deck>.tex`, use the shared preamble, and follow
   the existing project's Beamer setup. Use substantive frame titles, accessible
   figures and tables, and backup slides for dense detail.
5. Keep every empirical value traceable to `results/` and every substantive claim
   consistent with the paper. Surface unresolved research choices to Leo; do not
   settle them in the slides.
6. Run `make slides`, inspect the compiled PDF and warnings, and report the result. Fix
   compilation or visible layout problems caused by the change before finishing.

The work is complete when the requested deck is present, its claims trace to the paper
or generated results, and the compiled output has been inspected. Report the deck path,
paper sections and outputs used, compile result, and any unresolved choice.
