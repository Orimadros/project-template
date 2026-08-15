# Pipeline Script Naming Convention

**Status:** COMPLETED

## Objective

Make the execution order and entry-point role of the staged pipeline explicit:
pipeline scripts in `code/00_fetch/`, `code/01_build/`, and
`code/02_analyze/` use `NN_verb_noun.<extension>`.  Supporting modules and
other scripts that are not pipeline entry points remain exempt.

## Approach

1. Update the repository’s primary agent guidance and shared code invariants
   with the precise rule, examples, and module exemption.
2. Make `make fetch`, `make build`, and `make analysis` select only numbered
   pipeline entry scripts, in lexical order, while supporting shell, Python,
   and R entry scripts.
3. Update the user guide and the mirrored Claude/Codex analysis skills so new
   work follows the convention.
4. Validate Makefile parsing and run the pipeline targets against the empty
   scaffold; confirm no helpers in the three stage directories are selected.

## Files Expected To Change

- `AGENTS.md`
- `CLAUDE.md`
- `Makefile`
- `.claude/rules/content-invariants.md`
- `.claude/WORKFLOW_QUICK_REF.md`
- `.claude/skills/analyze/SKILL.md`
- `.agents/skills/analyze/SKILL.md`
- `docs/sources/USER-GUIDE.md`

## Verification

- Passed: `make help`
- Passed: `make -n fetch build analysis`
- Passed: `make fetch build analysis`
- Passed: a contained fetch-stage test ran `01_report_start.sh` before
  `02_report_finish.py` and did not run unnumbered `biodiversity_model.py`
- Passed: `make provenance` (no data-bearing assets or data-generating code
  changed, so no ledger entry was needed)
- Passed: the two mirrored analysis skills are byte-identical
- Passed: `git diff --check`
