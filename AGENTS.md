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
- **Raw data is append-only** -- Claude/Codex hooks allow new files in `data/raw/` but block edits, overwrites, chmods, and deletes of existing raw files
- **Provenance Ledger required** -- every governed pipeline-code, data, and result file has an immutable Asset Graph identity and every data-bearing asset retains nested variable/code/layer provenance
- **Worker/critic separation** -- creative agents draft; critic agents evaluate; creators never self-score
- **[LEARN] tags** -- save corrections as `[LEARN:category] wrong -> right` in `MEMORY.md`

---

## Standing Rules

These three rules apply to every session regardless of which file is being touched, so they live here rather than as separate path-scoped files in `.claude/rules/`.

**Template vs. project (meta-governance).** This repo is both a working project and a reusable template. When editing infrastructure, ask: is this generic across projects (folder conventions, Make patterns, verification/quality rules, session-logging templates) -- commit it; or project-specific (raw-data idiosyncrasies, machine paths, institutional formatting) -- keep it local. `MEMORY.md` stores transferable learnings only. Keep `AGENTS.md`, `CLAUDE.md`, and `README.md` consistent, keep examples placeholder-based, and update rules and Make scaffolding together when workflow philosophy changes.

**Orchestrator protocol (contractor mode).** After a plan is approved, work proceeds autonomously through: implement -> verify (compile/render/check outputs; fix and re-verify on failure) -> review (route to review agents by file type) -> fix (critical -> major -> minor) -> re-verify -> score against the quality-gates rubric. Loop back to review if under threshold, max 5 rounds; critic-fixer sub-loops also cap at 5 rounds; verification retries cap at 2. Never loop indefinitely. When the user says "just do it" / "handle it": skip the final approval pause and auto-commit if score >= 80, but still run the full verify-review-fix loop and still present the summary.

**Session logging.** Log to `docs/work/session_logs/YYYY-MM-DD_description.md` (template: `docs/work/templates/session-log.md`) at three points, proactively: right after plan approval (goal, approach, rationale, key context); incrementally, 1-3 lines whenever a design decision is made, a problem is solved, the user corrects something, or the approach changes -- do not batch; and at session end (summary, quality scores, open questions, blockers). Quality reports are generated only at merge time, not at every commit/PR, saved to `docs/work/merge_reports/YYYY-MM-DD_[branch-name].md` using `docs/work/templates/quality-report.md`.

---

## Folder Structure

```text
[YOUR-PROJECT]/
├── AGENTS.md
├── CLAUDE.md
├── .agents/skills/         # canonical skills (Agent Skills standard)
├── .codex/{agents,hooks,hooks.json}  # Codex subagents (generated), shared hooks wiring
├── .claude/{agents,skills,rules,references,settings.json}  # Claude subagents, skills/ (symlinks into .agents/skills/), shared rules/calibration, hook wiring
├── Makefile                # host pipeline + make check / make agents
├── code/{00_fetch,01_build,02_analyze,03_quality,99_explorations}
├── data/{raw,clean,tmp}    # tracked empty scaffold; add project policy after fork
├── results/                # generated tables, figures, model outputs
└── docs/
    ├── data/provenance-ledger/
    ├── sources/             # external reference/input documents + references.bib
    ├── work/                # plans (with Clarity Status + MUST/SHOULD/MAY), session_logs,
    │                        # meetings (YYYY-MM-DD_topic-slug.md), checkpoints, reviews,
    │                        # merge_reports, templates
    └── deliverables/{articles/main,slides,appendices,preambles,assets}
```

---

## Naming Conventions

- Pipeline entry scripts in `code/00_fetch/`, `code/01_build/`, and `code/02_analyze/` use `NN_verb_noun.<extension>`, where `NN` is a two-digit execution-order prefix and the remaining name is lowercase `snake_case`:
  - `code/00_fetch/01_download_biodiversity.sh`
  - `code/01_build/03_construct_panel.R`
  - `code/02_analyze/05_make_tables.py`
- `make fetch`, `make build`, and `make analysis` run only those numbered pipeline entry points, in lexical order. Executed analysis notebooks follow the same pattern.
- Supporting modules, shared engines, and other scripts that are not pipeline entry points are exempt; keep them unnumbered so Make does not run them directly (for example, `biodiversity_model.py`, imported by `01_solve_model.py`). They need not use a verb--noun filename.
- Keep names imperative and explicit: `prep_`, `build_`, `estimate_`, `predict_`, `export_`
- Meeting notes and transcripts in `docs/work/meetings/` must use `YYYY-MM-DD_topic-slug.md`: a real ISO calendar date, followed by one lowercase, hyphen-separated topic slug. For example, `docs/work/meetings/2026-08-10_bard-harstad-theta.md`. Claude/Codex hooks reject non-conforming meeting-file paths.
- Each script should have a clear file contract: inputs, outputs, and stage responsibility
- Scripts should be readable to someone not yet familiar with the project: start with a concise purpose/data-flow description, use descriptive variable names, and organize repeated or multi-step logic into clearly named functions so the main script reads like an intuitive chain of steps
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
make provenance
make asset-graph-test
make all

# LaTeX documents (host, with TeX installed)
make articles   # compile every root .tex document under docs/deliverables/articles/
make slides     # compile every root .tex document under docs/deliverables/slides/
make latex      # compile both articles and slides
```

---

## Provenance Ledger

- Follow `.claude/rules/provenance-ledger.md` for files under `code/00_fetch/`, `code/01_build/`, `code/02_analyze/`, `code/99_explorations/`, `data/`, and `results/`. Documents and repository-control infrastructure are outside Asset Graph node coverage.
- Every governed file has one immutable UUID-backed node ID. Preserve it across moves and renames; retain deleted files as tombstones with path history and historical relationships.
- Agents that add, change, move, delete, or consume governed files must inspect the affected file contracts and update `docs/data/provenance-ledger/` manually. Graph tooling validates and queries; it does not infer dependency relationships.
- Store direct typed edges once as upstream to downstream. Derive reverse adjacency and transitive lineage with the graph CLI.
- Use `/inspect-asset-graph` for producers, raw sources, lineage, path history, rebuildability, and impact questions. If the graph is stale, use `/provenance-ledger` to repair it before relying on the answer.
- The ledger must document every asset plus nested queryable units: variables, columns, fields, raster bands/layers, class codes, model-output fields, units, missing-value rules, and derivations.
- Definitions and generation procedures must come from actual sources, code, codebooks, metadata, papers, or provider documentation. Do not fill provenance from memory.
- If exact provenance cannot be found, record the gap with `partial-flagged` or `missing-blocker`, warn the user, and run `make provenance`.
- Claude/Codex may add new files to `data/raw/`, but must not overwrite, edit, delete, rename over, or chmod existing raw files.

---

## PDF Source Reading

- When reading a PDF's contents, follow `.claude/rules/pdf-processing.md`: first create a Markdown version with `uv run python code/03_quality/pdf_to_markdown.py docs/sources/hyperdominance-paper.pdf --output docs/sources/hyperdominance-paper.md` and read the Markdown instead of the PDF.
- Use the original PDF or page images as a supplement when Markdown would lose important information, especially scanned pages, figures, diagrams, equations, complex tables, slide layouts, pagination, or visual design.

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

Track live paper/pipeline/slides status in `docs/work/plans/` and `docs/data/provenance-ledger/` rather than in a static table here -- a placeholder table drifts the moment real work starts.

---

## Rules Index

`.claude/rules/` and `.claude/references/` are shared, harness-neutral calibration -- the directory name is historical, not Claude-only. Claude Code auto-loads these by `paths:` frontmatter when a matching file is touched; Codex receives the same content via a PostToolUse rule-injector hook (`.codex/hooks.json`) plus this index as a fallback. Every rule below is path-scoped; the three standing rules above are not, because they apply everywhere.

| Rule | Applies to |
|------|------------|
| `agents.md` | agent/skill definitions -- worker/critic pairing |
| `beamer-integrity.md` | Beamer slides + preambles |
| `content-invariants.md` | articles, slides, code, data, results |
| `content-standards.md` | articles, slides, results |
| `exploration-fast-track.md` | `code/99_explorations/` |
| `exploration-folder-protocol.md` | `code/99_explorations/` |
| `knowledge-base-template.md` | articles, slides, R/Python code, Makefile |
| `no-pause-beamer.md` | Beamer slides |
| `orchestrator-research.md` | R code, explorations |
| `pdf-processing.md` | `docs/sources/` |
| `plan-first-workflow.md` | `docs/work/plans/` |
| `proofreading-protocol.md` | articles, appendices, slides, reviews |
| `provenance-ledger.md` | governed pipeline code, explorations, data/results, and ledger maintenance files |
| `quality-gates.md` | articles, slides, code, Makefile |
| `r-code-conventions.md` | R scripts |
| `replication-protocol.md` | R scripts |
| `revision.md` | reviews, plans, articles |
| `single-source-of-truth.md` | code, data, results, articles, slides, assets |
| `slide-writing-principles.md` | Beamer slides/preambles; agent/skill definitions |
| `tikz-visual-quality.md` | slides, articles, assets (TikZ) |
| `verification-protocol.md` | Makefile, code, data, results, articles, slides |
| `working-paper-format.md` | articles, preambles |
