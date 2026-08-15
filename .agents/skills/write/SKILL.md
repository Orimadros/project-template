---
name: write
description: Draft or revise the canonical paper using domain profile, personal style guide, citations, and generated results.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Task"]
---

# Write

Use this for paper drafting and revision.

## Required Context

Before drafting, read:

- `docs/deliverables/articles/main/main.tex`
- relevant files in `docs/deliverables/articles/main/sections/`
- `.claude/references/domain-profile.md`
- `.claude/references/personal-style-guide.md`
- `docs/sources/references.bib`
- relevant outputs in `results/`

## Workflow

1. Identify the target section or claim from `$ARGUMENTS`.
2. Check whether the claim is supported by generated outputs, sources, or explicit assumptions.
3. Use `writer` to draft or revise.
4. Use `writer-critic` for claim discipline, structure, notation, and style fidelity.
5. Compile the paper if `.tex` changed.

## Output

- Paper files changed
- Claims added or revised
- Evidence/source path for each substantive claim
- Compile command and result
