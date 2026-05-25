---
paths:
  - "docs/deliverables/slides/**/*.tex"
  - "docs/deliverables/preambles/**/*.tex"
---

# Beamer Integrity Rule (Talks Derive From Paper)

This template is Beamer-only for slide authoring, but it is paper-first for research content.
Slide writing follows `.claude/rules/slide-writing-principles.md`.

## Rule

- `docs/deliverables/articles/main/main.tex` is the canonical research source.
- Root Beamer decks live one per folder as `docs/deliverables/slides/<deck>/<deck>.tex`.
- `docs/deliverables/slides/*/*.tex` root files are the only slide-content source.
- Do not create or maintain parallel slide-authoring systems unless explicitly requested.
- Slide claims, notation, and empirical numbers must derive from the paper or generated outputs.
- New decks should use `\documentclass[notes,11pt,aspectratio=169]{beamer}` and input `docs/deliverables/preambles/beamer-preamble.tex` unless the project has a stronger local theme.
- New section dividers should use `\sectiontransition[optional subtitle]{Title}` from the shared preamble, not manually styled full-slide color blocks.
- New and revised decks should follow the central slide-writing standard for Big 5 opening, substantive titles, empirical credibility, data-graphics integrity, accessible color, and backup placement.
- After any content edit in `docs/deliverables/slides/` or `docs/deliverables/preambles/`, run Beamer verification before completion.

## Required Workflow

1. Check the paper for the authoritative claim/notation.
2. Apply the slide edit in Beamer `.tex`, following the slide-writing principles.
3. Compile with XeLaTeX, using BibTeX and 3 passes when bibliography/math references are involved.
4. Check for compilation errors and overfull boxes.
5. Confirm output PDF updates successfully.

## Enforcement Check

Before marking a slide task complete, ask:

> Did I verify the edited Beamer file compiles and remains consistent with the paper?
