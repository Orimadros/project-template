---
paths:
  - "docs/work/reviews/**/*.md"
  - "docs/work/plans/**/*.md"
  - "docs/deliverables/articles/**/*.tex"
---

# Revision Workflow

Use this workflow for referee-style reviews, internal critic reports, and major paper revisions.

## Comment Classes

- `NEW ANALYSIS`: requires new code, data work, tables, figures, or robustness checks.
- `CLARIFICATION`: requires clearer text, notation, framing, or assumptions.
- `DISAGREE`: the paper should explicitly defend the current choice or reject the suggestion.
- `MINOR`: typo, formatting, citation, or small wording fix.

## Routing

- `NEW ANALYSIS` -> strategist, coder, provenance-ledger, coder-critic, verifier.
- `CLARIFICATION` -> writer, writer-critic, domain-referee.
- `DISAGREE` -> strategist, methods-referee, editor.
- `MINOR` -> proofreader or direct edit, then compile.

## Required Output

For non-trivial reviews, create a revision plan in `docs/work/plans/` with:

- source review report path
- comment classification table
- planned response
- files expected to change
- expected Provenance Ledger updates when data/results change
- verification commands

Do not bury revision decisions in chat only.
