---
paths:
  - "docs/deliverables/slides/**/*.tex"
  - "docs/deliverables/preambles/**/*.tex"
---

# Beamer Integrity Rule (Talks Derive From Paper)

This template is Beamer-only for slide authoring, but it is paper-first for research content.

## Rule

- `docs/deliverables/articles/main.tex` is the canonical research source.
- `docs/deliverables/slides/*.tex` files are the only slide-content source.
- Do not create or maintain parallel slide-authoring systems unless explicitly requested.
- Slide claims, notation, and empirical numbers must derive from the paper or generated outputs.
- After any content edit in `docs/deliverables/slides/` or `docs/deliverables/preambles/`, run Beamer verification before completion.

## Required Workflow

1. Check the paper for the authoritative claim/notation.
2. Apply the slide edit in Beamer `.tex`.
3. Compile with XeLaTeX, using BibTeX and 3 passes when bibliography/math references are involved.
4. Check for compilation errors and overfull boxes.
5. Confirm output PDF updates successfully.

## Enforcement Check

Before marking a slide task complete, ask:

> Did I verify the edited Beamer file compiles and remains consistent with the paper?
