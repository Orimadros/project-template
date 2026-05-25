---
paths:
  - "code/**/*"
  - "data/**/*"
  - "results/**/*"
  - "docs/deliverables/articles/**/*.tex"
  - "docs/deliverables/slides/**/*.tex"
  - "docs/deliverables/assets/**/*"
---

# Single Source of Truth: Paper-Centric Empirical Pipeline

## Authoritative Layers

```text
data/raw/*                                      immutable project inputs
code/00_fetch/*                                 retrieval scripts
code/01_build/*                                 construction/transformation scripts
code/02_analyze/*                               estimation/report scripts
docs/deliverables/articles/main/main.tex        canonical paper source
docs/deliverables/articles/main/sections/*.tex  canonical paper sections
docs/sources/references.bib                     canonical bibliography
```

The paper is authoritative for the research argument, notation, empirical claims, tables, and figures. Beamer talks and appendices must derive from it.

## Derived Layers

```text
data/clean/*
data/tmp/*
results/*
docs/deliverables/slides/*/*.tex               derivative talk material
compiled PDFs
```

## Rules

- Never hand-edit generated artifacts in `data/clean/`, `data/tmp/`, or `results/`.
- Regenerate outputs by running scripts or Make targets.
- Keep raw data immutable unless the user explicitly requests replacement.
- If a derived output looks wrong, fix upstream code, then rebuild.
- If a slide contradicts the paper, update the slide or explicitly revise the paper first.
- If a slide is hard to read, fix the Beamer source according to `.claude/rules/slide-writing-principles.md`; do not create a parallel presentation artifact.
- Every numerical claim in the paper should be traceable to a script and generated output.
- Keep root article and slide documents one per folder: `articles/<name>/<name>.tex` and `slides/<name>/<name>.tex`.

## Verification Checklist

- [ ] Upstream script(s) updated, not only outputs
- [ ] Pipeline rerun for impacted stage(s)
- [ ] Outputs regenerated at expected paths
- [ ] Paper claim updated if results changed
- [ ] Talks/appendices checked for derived-claim consistency
