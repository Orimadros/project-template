---
name: strategize
description: Turn a paper idea into a research design, identification strategy, analysis plan, and paper outline.
argument-hint: "[research question or design problem]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Strategize

Use this for research design decisions before code or paper drafting.

## Required Context

- `.claude/references/domain-profile.md`
- `docs/deliverables/articles/main/main.tex`
- `docs/deliverables/articles/main/sections/`
- `docs/work/plans/`
- relevant source documents in `docs/sources/`
- `.claude/rules/provenance-ledger.md`

## Workflow

1. Identify the estimand, unit of analysis, and empirical setting.
2. State the identifying assumptions and main threats.
3. Propose the minimum viable analysis and robustness sequence.
4. Map each analysis step to expected scripts under `code/`, outputs under `results/`, and Provenance Ledger asset/variable entries.
5. Route the design through `strategist-critic`; use `methods-referee` for causal claims.
6. Save non-trivial plans to `docs/work/plans/`.

## Output

- Research design summary
- Identification assumptions
- Analysis dependency map
- Provenance Ledger implications for planned datasets and outputs
- Paper section implications
- Critic findings and unresolved decisions
