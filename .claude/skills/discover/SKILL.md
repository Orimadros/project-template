---
name: discover
description: Paper-centric discovery workflow for literature, sources, data possibilities, and research terrain mapping.
argument-hint: "[topic, paper title, dataset, or research question]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
---

# Discover

Use this at the beginning of a project or when opening a new research direction.

## Required Context

- `docs/sources/`
- `docs/sources/references.bib`
- `.claude/rules/pdf-processing.md`
- `.claude/references/domain-profile.md`
- existing paper files under `docs/deliverables/articles/`

## Workflow

1. Parse `$ARGUMENTS` into the research question, topic, paper, or data source being explored.
2. Search existing sources and bibliography before asking for new material.
3. For PDF sources, follow `.claude/rules/pdf-processing.md`: create a MarkItDown Markdown version and read that unless visual/layout information is essential.
4. Use `librarian` for source mapping and `librarian-critic` for coverage/citation gaps.
5. If data feasibility matters, route to `data-engineer` or `explorer`.
6. Write a concise discovery memo to `docs/work/reviews/` or a next-step plan to `docs/work/plans/`.

## Output

- Research terrain summary
- Candidate contribution angles
- Must-read sources already present
- Missing sources to obtain
- Data feasibility notes
- Recommended next action
