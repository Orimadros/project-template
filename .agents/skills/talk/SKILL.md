---
name: talk
description: Create or revise Beamer talks that derive from the canonical paper and follow the project slide-writing principles.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Talk

Use this for Beamer presentations derived from the paper.

**Arguments:** [talk goal, audience, duration, or deck path]

## Required Context

- `docs/deliverables/articles/main/main.tex`
- relevant paper sections in `docs/deliverables/articles/main/sections/`
- generated outputs in `results/`
- existing decks in `docs/deliverables/slides/*/`
- shared preambles in `docs/deliverables/preambles/`
- `.claude/rules/slide-writing-principles.md`
- `docs/deliverables/preambles/beamer-preamble.tex`

## Slide Standard

- Use the full standard in `.claude/rules/slide-writing-principles.md`: one point per slide, Big 5 opening, substantive frame titles, intuition bridge, empirical credibility, data-graphics integrity, accessible color, and dense material in backup.
- Default new decks to one folder per deck, `docs/deliverables/slides/<deck>/<deck>.tex`.
- In new deck roots, use `\documentclass[notes,11pt,aspectratio=169]{beamer}` and `\input{../../preambles/beamer-preamble}` unless the project has a stronger local theme.
- Use `wideitemize`, central figures, compact `booktabs`/`siunitx` tables, and speaker notes where helpful.
- For section dividers, use `\sectiontransition[optional subtitle]{Title}` from `beamer-preamble.tex`; do not hand-roll full-slide yellow/blue transition frames.
- For a reference at the end of a bullet, wrap it in `\smallcitation{...}` so it renders small and muted; keep load-bearing inline citations (e.g. "the Rozendaal (2008) procedure") at normal size.
- Avoid casual `\pause`; use controlled `\only`, `\onslide`, or `\uncover` only for a clear figure/table build.
- Do not build a short talk by rushing a seminar deck; cut claims and details to match the audience, duration, talk type, and project status.

## Workflow

1. Identify audience, duration, talk type/status, and goal.
2. Read the slide-writing principles and the shared Beamer preamble.
3. Extract the Big 5 from the paper: question, stakes, gap, contribution, headline answer, and main credibility threat.
4. Plan the opening, intuition bridge, empirical credibility sequence, and backup material before drafting.
5. Use `storyteller` to draft or revise Beamer `.tex`.
6. Use `storyteller-critic`, `slide-auditor`, and/or `pedagogy-reviewer` to review.
7. Compile slide decks with `make slides`.

## Output

- Deck path
- Paper sections used
- Claims that require paper/results traceability
- Opening Big 5 and pacing assumptions
- Slide-principles compliance notes
- Compile/review status
