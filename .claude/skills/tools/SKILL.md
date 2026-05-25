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
make articles
```

### Compile talk

```bash
make slides
```

### Score a file

```bash
python3 code/03_quality/quality_score.py docs/deliverables/articles/main/main.tex
```

### Validate bibliography

Use `/validate-bib`; it scans `docs/sources/references.bib`, paper files, and Beamer talks.
