---
name: review-slides
description: Review a rendered Beamer talk for paper fidelity, narrative, pedagogy, and visual clarity.
disable-model-invocation: true
---

# Review a research talk

Use this when Leo requests review of a Beamer deck. This is a read-only review. The
canonical paper and generated results govern the deck's claims. Do not edit slides or
make research decisions.

## Workflow

1. Resolve the requested deck and its compiled PDF. Read the canonical paper sections
   and `results/` outputs relevant to the deck, the shared Beamer preamble, and
   `../../references/slide-writing-principles.md`. Use
   `../../references/tikz-visual-quality.md` when the deck contains relevant TikZ.
2. If the PDF is missing or stale, run `make slides` when the project supports it.
   Inspect the rendered PDF as well as the source. If compilation or rendering is
   unavailable, report that limitation and distinguish content findings from visual
   findings that could not be verified.
3. Review four connected questions:
   - **Paper fidelity:** Do claims, numbers, notation, and uncertainty match the
     manuscript and generated results?
   - **Argument and pedagogy:** Does the opening establish the question, stakes, gap,
     contribution, headline answer, and main threat? Is there an intuition bridge and
     does the sequence fit the audience and duration?
   - **Prose and notation:** Are titles substantive, text concise, and notation clear
     and consistent?
   - **Rendered design:** Are figures, tables, labels, colors, and spacing readable?
     Check overflow, clutter, backup placement, transitions, and overlays in the PDF.
4. Report prioritized findings with frame numbers or titles, the problem, why it
   matters, and a concrete correction. Keep factual mismatches separate from delivery
   preferences. Do not infer that an unpublished result is settled; flag it for Leo.
5. Return the strongest elements, material issues, and a short readiness judgment.
   Save a review report only if Leo asks for a file.

The review is complete when the source and rendered deck have been covered, or the
verification limits are explicit, and each material finding has a location.
