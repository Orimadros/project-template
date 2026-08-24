---
name: analyze
description: Paper-centric empirical analysis workflow using code/ for scripts and results/ for generated paper outputs.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Analyze

Use this for reproducible empirical work that should feed the canonical paper.

**Arguments:** [analysis goal, table, figure, or robustness check]

## Constraints

- Fetch scripts live in `code/00_fetch/`.
- Build scripts live in `code/01_build/`.
- Estimation/reporting scripts live in `code/02_analyze/`.
- A pipeline entry script in those directories must be named `NN_verb_noun.<extension>` (for example, `01_solve_model.py`); its two-digit prefix establishes execution order within its stage. Unnumbered modules and helpers, such as `biodiversity_model.py`, are not pipeline entry points and may use other names.
- Generated tables, figures, and model outputs live in `results/`.
- Paper text lives in `docs/deliverables/articles/`; do not hand-edit generated results.
- Any governed file created, changed, moved, or deleted under pipeline code, `code/99_explorations/`, `data/`, or `results/` must be represented in the Asset Graph with immutable identity, lifecycle history, manually inspected direct dependencies, and a fresh review hash. Data-bearing assets also require nested variable/code/layer entries.

## Workflow

1. Clarify the target paper claim, table, figure, or robustness check.
2. Implement or update the smallest relevant staged script.
3. Run the narrowest Make target that regenerates the output.
4. Manually inspect the changed file contract and update Asset Graph nodes/events/activities plus source-grounded asset and variable-level provenance.
5. Run `make provenance`.
6. Route code through `coder-critic` and verification through `verifier`.
7. If results change paper claims, update or flag the relevant article section.

## Output

- Changed scripts and generated output paths
- Provenance Ledger entries changed or gaps flagged
- Commands run
- Result interpretation for the paper
- Any follow-up needed in `docs/work/plans/`
