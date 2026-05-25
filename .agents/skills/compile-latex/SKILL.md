---
name: compile-latex
description: Compile the canonical paper or a derivative Beamer talk with XeLaTeX and BibTeX.
argument-hint: "[articles|slides|all|optional document path]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Compile LaTeX

Compile root article and Beamer documents using the project Makefile, which runs XeLaTeX and BibTeX when needed.

## Target Resolution

- Default paper target: `docs/deliverables/articles/main/main.tex`
- Article root documents live one per folder: `docs/deliverables/articles/<name>/<name>.tex`
- Beamer root documents live one per folder: `docs/deliverables/slides/<name>/<name>.tex`
- Supporting fragments, such as `sections/*.tex`, live inside the owning document folder and are not compiled directly.

## Commands

```bash
make articles   # every root article .tex
make slides     # every root slide .tex
make latex      # articles + slides
```

Use `make latex` when `$ARGUMENTS` is empty or `all`. Use `make articles` for paper-only work and `make slides` for talk-only work.

## Checks

- Grep output for hard errors.
- Check for undefined citations or references.
- Count major overfull hbox warnings.
- Confirm the PDF exists.

## Important

- Use XeLaTeX by default.
- Use BibTeX with `docs/sources/references.bib` unless the project explicitly opts into `biblatex`/`biber`.
- Shared preambles live in `docs/deliverables/preambles/`.
