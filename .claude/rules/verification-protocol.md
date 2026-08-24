---
paths:
  - "Makefile"
  - "code/**/*"
  - "data/**/*"
  - "results/**/*"
  - "docs/data/provenance-ledger/**/*"
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/slides/**/*.tex"
---

# Task Completion Verification Protocol

Every substantive task must end with a runnable verification step.

## For Pipeline Changes (`code/`, `Makefile`)

1. Run the narrowest relevant target first (`make fetch`, `make build`, or `make analysis`).
2. Run `make provenance` after any data/results asset is created or changed.
3. If stage-level behavior changed broadly, run `make all`.
4. Confirm expected outputs exist and are non-empty (`data/clean/`, `results/`).
5. Report what was run and what passed/failed.
6. For any governed file addition, content change, move, or deletion, confirm its immutable node, lifecycle event, review hash, and direct relationships are current.

## For R Scripts (`.R`)

1. Execute script directly or through the Make stage.
2. Check output artifacts exist with non-zero size.
3. Spot-check key values for plausibility.

## For Python / Notebooks (`.py`, `.ipynb`)

1. Run script/notebook execution target.
2. Ensure execution completes without errors.
3. Confirm generated outputs are written to expected locations.
4. Confirm generated data-bearing outputs are represented in `docs/data/provenance-ledger/`.

## For The Paper (`docs/deliverables/articles/main/main.tex`)

1. Run `make articles`.
2. If citations are involved, run BibTeX and the full 3-pass compile.
3. Check for hard errors, undefined citations/references, and major overfull boxes.
4. Verify generated numbers/tables/figures trace back to `results/`.

## For Beamer Talks (`docs/deliverables/slides/*/*.tex`)

1. Run `make slides`.
2. If citations are involved, run BibTeX and the full 3-pass compile.
3. Check for hard errors and major overfull box warnings.
4. Verify slide claims derive from the paper.
5. Spot-check against `.claude/rules/slide-writing-principles.md` for Big 5 opening, substantive titles, empirical credibility, data-graphics integrity, accessible color, density, and backup placement.

## Verification Checklist

- [ ] Relevant command(s) executed
- [ ] No blocking runtime/compile errors
- [ ] Expected output files created
- [ ] `make provenance` passes when data/results changed
- [ ] Paper/slides checked for claim consistency
- [ ] Results reported to user
