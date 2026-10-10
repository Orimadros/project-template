---
name: write-paper
description: Draft or revise the canonical article from claims and research choices Leo has settled.
disable-model-invocation: true
---

# Write the paper

Use this when Leo asks to draft or revise article text. Treat the canonical paper as
the source of truth for the argument, notation, claims, tables, and figures. Implement
settled research choices; Leo retains authority over research and logic decisions.

## Workflow

1. Identify the requested files, section, and change. Read `CONTEXT.md`, the canonical
   `docs/deliverables/articles/main/main.tex`, and only the relevant section files.
2. Read the relevant entries in `results/`, cited source documents, and
   `docs/sources/references.bib` before changing claims. Read
   `.claude/references/domain-profile.md`, `personal-style-guide.md`, or
   `journal-profiles.md` only when the task needs them and their contents are
   meaningfully filled in. Treat placeholders as unknowns.
3. Tie every substantive factual or empirical claim to a generated result, a cited
   source, or an explicit assumption. Preserve the distinction between association and
   causal effect; state identifying assumptions before interpreting causal estimates.
   Keep numbers aligned with generated outputs, citations faithful to their sources,
   and notation consistent with the rest of the paper.
4. Make the requested change in the authoritative source files. Keep generated tables
   and figures in `results/`; do not hand-copy results into a new table or figure.
5. If the requested text requires an unsettled choice about the estimand, mechanism,
   identification, interpretation, or another research decision, stop at that point and
   explain the alternatives to Leo. Do not write around the open choice as if it were
   settled.
6. After changing LaTeX, run `make articles` and report the result. Apply the defaults
   in `../../references/working-paper-format.md` only where the project has no settled
   convention.

## Return

Report the files changed, the claims materially added or revised with their evidence
paths, the relevant compile result, and any research choice that remains open. The task
is complete when the requested settled change is present and its relevant verification
has been reported.
