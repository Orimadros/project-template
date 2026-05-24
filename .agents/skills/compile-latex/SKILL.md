---
name: compile-latex
description: Compile the canonical paper or a derivative Beamer talk with XeLaTeX and BibTeX.
argument-hint: "[main|talk filename without .tex|path]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Compile LaTeX

Compile the canonical article or a Beamer talk using XeLaTeX with citation resolution when needed.

## Target Resolution

- Default paper target: `docs/deliverables/articles/main.tex`
- Article targets live in `docs/deliverables/articles/`
- Beamer targets live in `docs/deliverables/slides/`

## Paper Command

```bash
cd docs/deliverables/articles
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
if grep -q "\\citation" main.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex main; fi
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
```

## Beamer Talk Command

```bash
cd docs/deliverables/slides
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode $ARGUMENTS.tex
if grep -q "\\citation" $ARGUMENTS.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex $ARGUMENTS; fi
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode $ARGUMENTS.tex
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

## Checks

- Grep output for hard errors.
- Check for undefined citations or references.
- Count major overfull hbox warnings.
- Confirm the PDF exists.

## Important

- Use XeLaTeX by default.
- Use BibTeX with `docs/sources/references.bib` unless the project explicitly opts into `biblatex`/`biber`.
- Shared preambles live in `docs/deliverables/preambles/`.
