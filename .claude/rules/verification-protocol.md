---
paths:
  - "Makefile"
  - "code/**/*"
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/slides/**/*.tex"
---

# Task Completion Verification Protocol

Every substantive task must end with a runnable verification step.

## For Pipeline Changes (`code/`, `Makefile`)

1. Run the narrowest relevant target first (`make fetch`, `make build`, or `make analysis`).
2. If stage-level behavior changed broadly, run `make all`.
3. Confirm expected outputs exist and are non-empty (`data/clean/`, `results/`).
4. Report what was run and what passed/failed.

## For R Scripts (`.R`)

1. Execute script directly or through the Make stage.
2. Check output artifacts exist with non-zero size.
3. Spot-check key values for plausibility.

## For Python / Notebooks (`.py`, `.ipynb`)

1. Run script/notebook execution target.
2. Ensure execution completes without errors.
3. Confirm generated outputs are written to expected locations.

## For The Paper (`docs/deliverables/articles/main.tex`)

1. Compile with XeLaTeX.
2. If citations are involved, run BibTeX and the full 3-pass compile.
3. Check for hard errors, undefined citations/references, and major overfull boxes.
4. Verify generated numbers/tables/figures trace back to `results/`.

## For Beamer Talks (`docs/deliverables/slides/*.tex`)

1. Compile with XeLaTeX.
2. If citations are involved, run BibTeX and the full 3-pass compile.
3. Check for hard errors and major overfull box warnings.
4. Verify slide claims derive from the paper.

## Verification Checklist

- [ ] Relevant command(s) executed
- [ ] No blocking runtime/compile errors
- [ ] Expected output files created
- [ ] Paper/slides checked for claim consistency
- [ ] Results reported to user
