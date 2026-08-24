---
name: data-analysis
description: End-to-end empirical data analysis workflow from setup to estimation to paper-ready outputs.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Data Analysis Workflow

Use this workflow for reproducible analysis under the staged project structure.

**Arguments:** [dataset path, paper claim, table, figure, or analysis goal]

## Constraints

- Follow `.claude/rules/r-code-conventions.md` and `.claude/references/coding-standards-r.md` when applicable.
- Save scripts in stage folders under `code/`.
- Save generated artifacts to `data/clean/`, `data/tmp/`, or `results/`.
- Use `saveRDS()` for heavy computed objects.
- Use relative paths only.
- Treat `docs/deliverables/articles/main/main.tex` as the canonical consumer of results.
- Treat `docs/data/provenance-ledger/` as the canonical record for immutable identity and lineage of governed pipeline code, data, and results, plus data asset and variable-level generation.

## Phases

1. Setup and load data.
2. Explore and diagnose in `code/99_explorations/` when the path is uncertain.
3. Build reproducible staged scripts.
4. Estimate and validate.
5. Export tables/figures/model outputs to `results/`.
6. Manually inspect and update Asset Graph identities, lifecycle events, activities, and edges for every governed change; update nested variable/code/layer provenance for generated data-bearing assets.
7. Run `make provenance`.
8. Update or flag paper claims affected by the outputs.
9. Save outputs and run review (`/review-r`, `/review code`, or `coder-critic`).

## Deliverables

- Reproducible script(s) in `code/01_build/` or `code/02_analyze/`.
- Output artifacts in `results/` and optionally `data/clean/`.
- Provenance Ledger entries for changed assets and variables, or explicit flagged gaps.
- Brief note describing assumptions, checks performed, and paper implications.
