# AGENTS.md -- Paper-Centric Empirical Research Template (Make + Beamer Talks)

**Project:** [YOUR PROJECT NAME]
**Institution:** [YOUR INSTITUTION]
**Branch:** main

---

## Core Principles

- **Plan first** -- for non-trivial work, save plans to `docs/work/plans/`
- **Verify after** -- run the relevant Make target(s) or LaTeX compile before declaring done
- **Paper is authoritative** -- `docs/deliverables/articles/main/main.tex` is the source of truth for the argument, notation, claims, tables, and figures
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
├── .agents/
│   └── skills/             # Codex repo skills: one SKILL.md per skill
├── .codex/
│   ├── agents/             # Codex project custom agents: one TOML file per agent
│   ├── hooks/              # Codex hook scripts
│   └── hooks.json          # Codex project hook wiring; requires trust in Codex
├── .claude/
│   ├── agents/             # Claude Code subagents
│   ├── skills/             # Claude Code skills
│   ├── hooks/              # Claude Code hook scripts
│   ├── references/         # Shared domain/style/journal calibration
│   └── rules/              # Shared workflow and quality rules
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
        ├── articles/        # One folder per article document
        │   └── main/        # main/main.tex plus sections/ and compile outputs
        ├── slides/          # One folder per Beamer deck
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

# LaTeX documents (host, with TeX installed)
make articles   # compile every root .tex document under docs/deliverables/articles/
make slides     # compile every root .tex document under docs/deliverables/slides/
make latex      # compile both articles and slides
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

## Codex Project Customization

- Codex project instructions come from `AGENTS.md`; keep this file small and route to detailed references instead of duplicating them.
- Codex custom agents live in `.codex/agents/*.toml`. Each file defines one project-scoped custom agent with `name`, `description`, and `developer_instructions`.
- Codex project skills live in `.agents/skills/*/SKILL.md`. Do not create `.codex/skills/`; Codex does not use that as the repo skill location.
- Codex hooks live in `.codex/hooks.json` and `.codex/hooks/`. Project-local hooks only run after the project `.codex/` layer is trusted in Codex. Hook commands must resolve scripts from the git root with `$(git rev-parse --show-toplevel)` and must not contain machine-specific absolute paths.
- Codex has no Claude-style `Notification` hook event. Use Codex hook events from the official set, especially `PermissionRequest`, `PreToolUse`, `PostToolUse`, `PreCompact`, `SessionStart`, and `Stop`.
- Shared calibration remains in `.claude/rules/` and `.claude/references/` so Claude and Codex use the same source of truth. Codex agents and skills should read those files when relevant rather than mirroring them.
- Do not commit local Codex secrets or auth. This template may commit `.codex/agents/`, `.codex/hooks.json`, and `.codex/hooks/`, but should not include a project `.codex/config.toml` unless it contains only non-secret project defaults.

---

## Paper Style And Preferences

- Field calibration lives in `.claude/references/domain-profile.md`
- Personal writing preferences live in `.claude/references/personal-style-guide.md`
- Journal constraints live in `.claude/references/journal-profiles.md`
- Shared LaTeX config lives in `docs/deliverables/preambles/`

## Slide Writing Principles

- Beamer talks follow `.claude/rules/slide-writing-principles.md`, adapted from Paul Goldsmith-Pinkham's Beamer tips.
- Default new talks should use 16:9 Beamer, `docs/deliverables/preambles/beamer-preamble.tex`, generous spacing, sparse text, substantive frame titles, and color-blind-conscious accents.
- A good Beamer request should provide audience, duration, talk type/status, and goal; agents then choose the right talk/review skills.
- Research-talk openings should answer the Big 5 early: question, stakes, gap, contribution, headline answer, and main credibility threat.
- Empirical slides should make data sources, variable levels, identification variation, units, transformations, uncertainty, and threats visible when they affect credibility.
- Section dividers should use `\sectiontransition[optional subtitle]{Title}` from the shared Beamer preamble, not hand-rolled full-slide color blocks.
- Each slide should make one point clearly; dense proofs, full tables, and robustness detail belong in backup slides with links.
- Do not shrink fonts to fit crowded slides; split the slide, use a clearer visual, or move detail to backup.
- Use low-clutter, directly labeled figures and compact `booktabs`/`siunitx` tables; do not rely on hue alone for load-bearing distinctions.
- Avoid casual `\pause`; controlled builds are acceptable only when they clarify a figure/table reveal.

---

## Current Project State

| Module | Path | Status | Notes |
|--------|------|--------|-------|
| Paper | `docs/deliverables/articles/main/main.tex` | [TODO/ACTIVE] | [Research question + manuscript scope] |
| Fetch | `code/00_fetch/` | [TODO/ACTIVE] | [Data sources] |
| Build | `code/01_build/` | [TODO/ACTIVE] | [Prep pipeline] |
| Analyze | `code/02_analyze/` | [TODO/ACTIVE] | [Models/notebooks/results] |
| Slides | `docs/deliverables/slides/` | [TODO/ACTIVE] | [Derivative Beamer talk scope] |
