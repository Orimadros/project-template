---
name: provenance-ledger
description: Maintain source-grounded asset and variable-level provenance for every dataset, intermediate file, clean dataset, raster, model output, table, or data-bearing result. Use whenever Claude fetches data, writes data-generating code, creates or updates data/results assets, reviews data pipelines, or answers questions about variable meanings, code values, raster classes, units, missing values, or how an asset was generated.
argument-hint: "[asset path, variable/code question, or data task]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Provenance Ledger

Maintain `docs/data/provenance-ledger/` as the authoritative source for how each data-bearing asset and queryable unit was generated.

## Required Context

- `.claude/rules/provenance-ledger.md`
- `docs/data/provenance-ledger/index.toml`
- Relevant files under `code/00_fetch/`, `code/01_build/`, `code/02_analyze/`
- Source material under `docs/sources/` and source/provider documentation

## Workflow

1. Identify every affected asset under `data/raw/`, `data/tmp/`, `data/clean/`, or `results/`.
2. Add new files to `data/raw/` when needed, but do not overwrite, edit, delete, rename over, or chmod existing raw files.
3. Identify every queryable unit inside each asset: variables, columns, fields, raster bands, layers, class codes, model-output fields, and figure-data fields.
4. Ground definitions and generation procedures in actual sources: source docs, codebooks, papers, replication packages, provider pages, metadata files, or project code. Do not rely on memory.
5. Update `index.toml`, `assets/<asset_id>.toml`, and `assets/<asset_id>.md`.
6. Use `status = "partial-flagged"` for non-blocking gaps, `status = "missing-blocker"` for unreliable assets, and warn the user about either.
7. Run `make provenance` before declaring the work complete.

## Asset Metadata Rules

- Every asset TOML must include the fields defined in `.claude/rules/provenance-ledger.md`.
- Every structured, geospatial, raster, model-output, table, or figure-data asset must include `[[variables]]` entries.
- Every categorical, code-like, class, or raster-class variable must document `allowed_values` or explicitly carry an incomplete status.
- Directories may be registered as assets only when they are logical multi-file datasets.

## Query Answers

When asked what a variable, code, class, layer, or output field means, answer from the Provenance Ledger first. If the Ledger is missing or incomplete, investigate from actual sources, update the Ledger, and clearly state any remaining uncertainty.
