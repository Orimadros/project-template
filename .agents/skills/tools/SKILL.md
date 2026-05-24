---
name: tools
description: Utility commands for compiling paper/talks, validating bibliography, and running quality checks.
argument-hint: "[compile|bib|score|help] [target]"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Tools

Use this for quick maintenance commands.

## Common Commands

### Compile paper

```bash
cd docs/deliverables/articles
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
if grep -q "\\citation" main.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex main; fi
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
```

### Compile talk

```bash
cd docs/deliverables/slides
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
if grep -q "\\citation" talk.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex talk; fi
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
```

### Score a file

```bash
python3 code/03_quality/quality_score.py docs/deliverables/articles/main.tex
```

### Validate bibliography

Use `/validate-bib`; it scans `docs/sources/references.bib`, paper files, and Beamer talks.
