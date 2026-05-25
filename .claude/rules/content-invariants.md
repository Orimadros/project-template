---
paths:
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/slides/**/*.tex"
  - "code/**/*.R"
  - "code/**/*.py"
  - "code/**/*.sh"
---

# Content Invariants

These are non-negotiable checks for paper-centric empirical work.

## Paper Invariants

- Table notes must define the sample, unit, standard errors, controls, fixed effects, and significance notation.
- Figures must have captions that state the sample, variables, and interpretation.
- Tables use publication-style rules; avoid vertical rules and unexplained abbreviations.
- Abstract states the question, setting, method, result, and contribution without overclaiming.
- Keywords and JEL codes are placeholders until filled for a real project.
- Notation must be consistent across sections, tables, figures, appendix, and slides.
- Causal language requires an explicit identification argument.
- Claims about prior literature must match the cited source.
- Numbers in text must match generated outputs in `results/`.
- Plot titles should not duplicate captions; exported figures should be clean enough to include in paper or talks.

## Code Invariants

- Stochastic code must set a seed.
- Packages/imports belong at the top of scripts.
- Use relative paths only.
- Scripts write derived data to `data/clean/` or `data/tmp/` and generated outputs to `results/`.
- Script names should reflect execution order and purpose.
- Avoid manual edits to generated results; fix code and rerun.

## Talk Invariants

- Slides derive from the paper's argument and notation.
- Every slide-level empirical claim must be traceable to the paper or generated outputs.
- Beamer is the only presentation format unless the user explicitly requests otherwise.
- Follow `.claude/rules/slide-writing-principles.md`: one point per slide, Big 5 opening, substantive frame titles, empirical credibility, readable data graphics, accessible color, and dense material in backup.
- Do not use casual `\pause`; controlled overlays are allowed only when they clarify a figure/table build.

## Traceability Invariant

When a numerical claim changes, update all dependent paper text, tables/figures, appendices, and slides in the same task or record a follow-up plan in `docs/work/plans/`.
