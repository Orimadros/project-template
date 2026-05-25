---
paths:
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/preambles/**/*.tex"
---

# Working Paper Format

## Canonical Files

- Main paper: `docs/deliverables/articles/main/main.tex`
- Sections: `docs/deliverables/articles/main/sections/`
- Shared preambles: `docs/deliverables/preambles/`
- Bibliography: `docs/sources/references.bib`
- Generated empirical outputs: `results/`

## Default Structure

1. Title and author block
2. Abstract
3. Keywords and JEL codes
4. Introduction
5. Background and related literature
6. Data
7. Empirical strategy
8. Results
9. Conclusion
10. References

## LaTeX Defaults

- Use XeLaTeX by default.
- Use BibTeX with `docs/sources/references.bib` unless a project explicitly opts into `biblatex`/`biber`.
- Keep shared style in `docs/deliverables/preambles/`.
- Prefer `booktabs` for tables and `cleveref` for cross-references.
- Keep each root article document in its own folder: `docs/deliverables/articles/<name>/<name>.tex`.
- Supporting fragments such as `sections/*.tex` belong inside the owning article folder and are not compiled directly.

## Compile Command

```bash
make articles
```
