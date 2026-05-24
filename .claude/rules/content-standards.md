---
paths:
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/slides/**/*.tex"
  - "results/**/*"
---

# Content Standards

## Tables

- Tables should be self-contained: sample, variable definitions, controls, fixed effects, standard errors, and significance notation must be clear.
- Generated LaTeX or CSV tables should come from `code/02_analyze/` and land in `results/`.
- Do not paste numbers by hand unless the user explicitly chooses a manual table; even then, record the source.

## Figures

- Figures should communicate one idea clearly.
- Generated empirical figures should land in `results/figures/` or another explicit `results/` subfolder.
- Document-facing assets that are not generated analysis outputs may live in `docs/deliverables/assets/`.

## Paper Text

- Use precise causal language.
- State identifying assumptions before interpreting causal estimates.
- Distinguish statistical significance, economic magnitude, and substantive importance.
- Avoid generic contribution paragraphs; position the paper against specific literatures.

## Talks

- Talks are derivative: they simplify and sequence the paper, but should not introduce independent claims.
- Prefer figures and verbal interpretation over dense regression tables.
- Keep notation aligned with the paper.
