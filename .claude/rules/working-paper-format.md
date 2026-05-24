---
paths:
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/preambles/**/*.tex"
---

# Working Paper Format

## Canonical Files

- Main paper: `docs/deliverables/articles/main.tex`
- Sections: `docs/deliverables/articles/sections/`
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

## Compile Command

```bash
cd docs/deliverables/articles
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
if grep -q "\\citation" main.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex main; fi
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
```
