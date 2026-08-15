# Session Log: Pipeline Script Naming

**Date:** 2026-08-07

## Goal

Embed the user-specified convention that only pipeline entry scripts in the
fetch, build, and analysis stages use `NN_verb_noun.<extension>`.

## Key Decision

The numbered filename is the executable-entry-point marker for the Make
pipeline. Unnumbered modules and helpers remain available for imports and are
not invoked directly by `make`.

## Scope

Repository guidance, the mirrored analysis skills, the user guide, shared code
invariants, and Make target selection. No data-bearing asset or data-generating
code changes are planned.

## Verification

`make fetch` executed temporary numbered shell and Python entries in lexical
order and skipped a temporary unnumbered helper. The temporary test files were
removed afterward. `make help`, `make -n fetch build analysis`, `make fetch
build analysis`, `make provenance`, the mirrored-skill comparison, and `git
diff --check` all passed.
