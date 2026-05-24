# CLAUDE.md -- Paper-Centric Empirical Research Template (Make + Beamer Talks)

**Project:** [YOUR PROJECT NAME]
**Institution:** [YOUR INSTITUTION]
**Branch:** main

---

## Core Principles

- **Plan first** -- for non-trivial work, save plans to `docs/work/plans/`
- **Verify after** -- run the relevant Make target(s) or LaTeX compile before declaring done
- **Paper is authoritative** -- `docs/deliverables/articles/main.tex` is the source of truth for the argument, notation, claims, tables, and figures
- **Slides derive from the paper** -- Beamer decks in `docs/deliverables/slides/` are talks based on the canonical paper, not a parallel source of truth
- **Reproducibility first** -- `code/` creates data/results; lockfiles pin dependencies; the Makefile defines the host pipeline
- **Worker/critic separation** -- creative agents draft; critic agents evaluate; creators never self-score
- **[LEARN] tags** -- save corrections as `[LEARN:category] wrong -> right` in `MEMORY.md`

---

## Folder Structure

```text
[YOUR-PROJECT]/
├── AGENTS.md
├── CLAUDE.md
├── Makefile                # Runs the staged pipeline on the host
├── code/
│   ├── 00_fetch/           # Raw data download scripts
│   ├── 01_build/           # Data construction/prep scripts
│   ├── 02_analyze/         # Estimation + notebook execution
│   ├── 03_quality/         # Template quality-check utilities
│   └── 99_explorations/    # Sandbox for experiments; graduate to staged folders
├── data/                   # Tracked empty scaffold; add project policy after fork
│   ├── raw/
│   ├── clean/
│   └── tmp/
├── results/                # Generated tables, figures, model outputs
└── docs/
    ├── sources/             # External reference/input documents + references.bib
    ├── work/                # Process docs created while working
    │   ├── plans/
    │   ├── task_requirements/
    │   ├── session_logs/
    │   ├── checkpoints/
    │   ├── reviews/
    │   ├── merge_reports/
    │   └── templates/
    └── deliverables/        # Repo-produced document outputs and document-facing assets
        ├── articles/        # Canonical paper source; main.tex lives here
        │   └── sections/
        ├── slides/          # Beamer talks derived from the paper
        ├── appendices/
        ├── preambles/
        └── assets/
```

---

## Naming Conventions

- Stage scripts by execution order:
  - `code/00_fetch/00_download_xxx.sh`
  - `code/01_build/00_clean_xxx.R`
  - `code/02_analyze/01_estimate_xxx.R`
- Keep names imperative and explicit: `prep_`, `build_`, `estimate_`, `predict_`, `export_`
- Each script should have a clear file contract: inputs, outputs, and stage responsibility
- Generated empirical tables and figures belong in `results/`; paper/talk files include them rather than hand-copying results

---

## Commands

```bash
# Dependency setup (if lockfiles are present)
make setup

# Data pipeline
make fetch
make build
make analysis
make all

# Paper compile (host, with TeX installed)
cd docs/deliverables/articles
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
if grep -q "\\citation" main.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex main; fi
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex

# Beamer talk compile (talks derive from the paper)
cd docs/deliverables/slides
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
if grep -q "\\citation" talk.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex talk; fi
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
```

---

## Quality Thresholds

| Score | Gate | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR | Ready for review |
| 95 | Submission | Aspirational paper/submission gate |

Weighted paper quality follows `.claude/rules/quality-gates.md`.

---

## Paper Style And Preferences

- Field calibration lives in `.claude/references/domain-profile.md`
- Personal writing preferences live in `.claude/references/personal-style-guide.md`
- Journal constraints live in `.claude/references/journal-profiles.md`
- Shared LaTeX config lives in `docs/deliverables/preambles/`

---

## Current Project State

| Module | Path | Status | Notes |
|--------|------|--------|-------|
| Paper | `docs/deliverables/articles/main.tex` | [TODO/ACTIVE] | [Research question + manuscript scope] |
| Fetch | `code/00_fetch/` | [TODO/ACTIVE] | [Data sources] |
| Build | `code/01_build/` | [TODO/ACTIVE] | [Prep pipeline] |
| Analyze | `code/02_analyze/` | [TODO/ACTIVE] | [Models/notebooks/results] |
| Slides | `docs/deliverables/slides/` | [TODO/ACTIVE] | [Derivative Beamer talk scope] |
