---
name: analyze
description: Paper-centric empirical analysis workflow using code/ for scripts and results/ for generated paper outputs.
argument-hint: "[analysis goal, table, figure, or robustness check]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Analyze

Use this for reproducible empirical work that should feed the canonical paper.

## Constraints

- Fetch scripts live in `code/00_fetch/`.
- Build scripts live in `code/01_build/`.
- Estimation/reporting scripts live in `code/02_analyze/`.
- Generated tables, figures, and model outputs live in `results/`.
- Paper text lives in `docs/deliverables/articles/`; do not hand-edit generated results.

## Workflow

1. Clarify the target paper claim, table, figure, or robustness check.
2. Implement or update the smallest relevant staged script.
3. Run the narrowest Make target that regenerates the output.
4. Route code through `coder-critic` and verification through `verifier`.
5. If results change paper claims, update or flag the relevant article section.

## Output

- Changed scripts and generated output paths
- Commands run
- Result interpretation for the paper
- Any follow-up needed in `docs/work/plans/`
