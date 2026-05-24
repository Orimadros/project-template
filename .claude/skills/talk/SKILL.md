---
name: talk
description: Create or revise Beamer talks that derive from the canonical paper.
argument-hint: "[talk goal, audience, duration, or deck path]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Talk

Use this for Beamer presentations derived from the paper.

## Required Context

- `docs/deliverables/articles/main.tex`
- relevant paper sections in `docs/deliverables/articles/sections/`
- generated outputs in `results/`
- existing decks in `docs/deliverables/slides/`
- shared preambles in `docs/deliverables/preambles/`

## Workflow

1. Identify audience, duration, and goal.
2. Extract the talk spine from the paper: question, setting, design, results, contribution.
3. Use `storyteller` to draft or revise Beamer `.tex`.
4. Use `storyteller-critic`, `slide-auditor`, and/or `pedagogy-reviewer` to review.
5. Compile the deck with XeLaTeX and BibTeX if needed.

## Output

- Deck path
- Paper sections used
- Claims that require paper/results traceability
- Compile/review status
