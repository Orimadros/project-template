---
name: data-analysis
description: End-to-end empirical data analysis workflow from setup to estimation to paper-ready outputs.
argument-hint: "[dataset path, paper claim, table, figure, or analysis goal]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Data Analysis Workflow

Use this workflow for reproducible analysis under the staged project structure.

## Constraints

- Follow `.claude/rules/r-code-conventions.md` and `.claude/references/coding-standards-r.md` when applicable.
- Save scripts in stage folders under `code/`.
- Save generated artifacts to `data/clean/`, `data/tmp/`, or `results/`.
- Use `saveRDS()` for heavy computed objects.
- Use relative paths only.
- Treat `docs/deliverables/articles/main.tex` as the canonical consumer of results.

## Phases

1. Setup and load data.
2. Explore and diagnose in `code/99_explorations/` when the path is uncertain.
3. Build reproducible staged scripts.
4. Estimate and validate.
5. Export tables/figures/model outputs to `results/`.
6. Update or flag paper claims affected by the outputs.
7. Save outputs and run review (`/review-r`, `/review code`, or `coder-critic`).

## Deliverables

- Reproducible script(s) in `code/01_build/` or `code/02_analyze/`.
- Output artifacts in `results/` and optionally `data/clean/`.
- Brief note describing assumptions, checks performed, and paper implications.
