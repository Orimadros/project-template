---
name: validate-bib
description: Validate bibliography entries against citations in the canonical paper, appendices, and Beamer talks.
allowed-tools: ["Read", "Grep", "Glob"]
---

# Validate Bibliography

## Steps

1. Read `docs/sources/references.bib` and collect keys.
2. Scan these files for citation keys:
   - `docs/deliverables/articles/**/*.tex`
   - `docs/deliverables/appendices/**/*.tex`
   - `docs/deliverables/slides/**/*.tex`
3. Cross-reference:
   - missing bibliography entries (critical)
   - unused bibliography entries (informational)
   - likely citation key typos
4. Report findings with fix suggestions.

## Rule

Do not fabricate bibliographic entries. If a citation cannot be verified from `docs/sources/` or a known source, flag it for the user.
