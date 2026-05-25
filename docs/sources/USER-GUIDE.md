# USER GUIDE - Running a Paper-Centric Empirical Project

**What this is:** a practical guide to using this repository as a paper-first empirical research scaffold. The canonical manuscript lives at `docs/deliverables/articles/main/main.tex`; code generates data/results; talks and appendices derive from the paper.

**Template note:** placeholders like `[YOUR PROJECT NAME]` are intentional. Fork the repo for a project, fill in the project-specific files, and keep process artifacts in `docs/work/`.

_Last updated: 2026-05-23_

---

## 1. What You Get

| Layer | Purpose | Where |
|-------|---------|-------|
| Paper | Canonical source of truth for argument, notation, claims, tables, figures | `docs/deliverables/articles/main/main.tex` |
| Paper sections | Modular manuscript text | `docs/deliverables/articles/main/sections/` |
| Talks | Beamer decks derived from the paper | `docs/deliverables/slides/` |
| Sources | External papers, reports, reference material, bibliography | `docs/sources/` |
| Staged pipeline | Fetch, build, analyze, quality utilities | `code/00_fetch` ... `code/03_quality` |
| Sandbox | Experiments before they graduate to staged code | `code/99_explorations/` |
| Data zones | Tracked placeholder folders; choose project-specific data policy after forking | `data/raw`, `data/clean`, `data/tmp` |
| Results | Generated tables, figures, and model outputs | `results/` |
| Work records | Plans, task requirements, session logs, checkpoints, reviews | `docs/work/` |
| Agent calibration | Domain, journal, and personal style preferences | `.claude/references/` |
| Codex customization | Repo skills, project agents, and project hooks | `.agents/skills/`, `.codex/` |
| Claude Code customization | Claude agents, skills, hooks, settings, rules, references | `.claude/` |

The defining idea: **the paper is authoritative; code is authoritative for generated evidence; slides and appendices derive from them.**

---

## 2. First-Time Setup

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
make setup
make help
```

Then customize:

- `AGENTS.md` and `CLAUDE.md`
- `.claude/references/domain-profile.md`
- `.claude/references/personal-style-guide.md`
- `.claude/references/journal-profiles.md`
- `docs/deliverables/articles/main/main.tex`
- `Makefile`, if your project needs a custom dependency graph

---

## 3. Daily Operating Loop

```text
Instruction
  -> Plan        (for non-trivial work; save to docs/work/plans/)
  -> Implement   (code, paper, appendix, or talk)
  -> Verify      (make target or LaTeX compile)
  -> Critic      (worker/critic review when useful)
  -> Report      (what changed, what passed, what remains)
```

Use `docs/work/task_requirements/` for complex ambiguous tasks, `docs/work/checkpoints/` for resumable state snapshots, and `docs/work/session_logs/` for narrative session records.

---

## 4. Project Lifecycle

### A. Discover

Use `/discover`, `/lit-review`, `/research-ideation`, or `/interview-me` to map the idea, literature, data possibilities, and contribution. Store external documents in `docs/sources/` and bibliography entries in `docs/sources/references.bib`.

### B. Strategize

Use `/strategize` for empirical design. The output should clarify the estimand, identification assumptions, threats, robustness checks, required code, expected outputs, and paper sections affected.

### C. Fetch And Build Data

- Acquisition scripts: `code/00_fetch/`, run with `make fetch`
- Cleaning/construction scripts: `code/01_build/`, run with `make build`
- Raw data in `data/raw/` is immutable by default
- Derived data goes to `data/clean/` or `data/tmp/`

### D. Analyze

- Estimation/reporting scripts: `code/02_analyze/`, run with `make analysis`
- Generated tables, figures, and model outputs go to `results/`
- Use `/analyze` or `/data-analysis` for paper-facing empirical work
- If a result changes, update the relevant paper claim or record a follow-up plan

### E. Write The Paper

- Main file: `docs/deliverables/articles/main/main.tex`
- Sections: `docs/deliverables/articles/main/sections/`
- Shared article style: `docs/deliverables/preambles/article-preamble.tex`
- Root article and slide documents live one per folder: `articles/<name>/<name>.tex` and `slides/<name>/<name>.tex`
- Use `make latex` to compile every root article and slide document
- Use `/write` for drafting and `/review paper` or `/review-paper` for manuscript review

### F. Build Talks

- Beamer decks live in `docs/deliverables/slides/`
- Slide writing follows `.claude/rules/slide-writing-principles.md`, adapted from Paul Goldsmith-Pinkham's Beamer tips
- New talks should use `docs/deliverables/preambles/beamer-preamble.tex` unless the project has a stronger local theme
- Section divider slides should use `\sectiontransition[optional subtitle]{Title}` from the shared preamble
- When asking for a talk, provide audience, duration, talk type/status, and goal when you know them
- Agents should plan the Big 5 opening, intuition bridge, empirical credibility sequence, talk-length budget, and backup material before drafting
- Empirical slides should use low-clutter data graphics, direct labels where useful, explicit units/transformations/uncertainty, accessible non-hue-only encodings, and compact `booktabs`/`siunitx` tables
- Use `/talk` to derive talks from the paper
- Use `/slide-excellence`, `/visual-audit`, `/pedagogy-review`, and `/proofread` for talk review

### G. Revise

Use `/revise` after reviews. Classify comments as `NEW ANALYSIS`, `CLARIFICATION`, `DISAGREE`, or `MINOR`, then route them to the right worker/critic loop.

---

## 5. Compile Commands

### Paper

```bash
make articles
```

### Beamer Talk

```bash
make slides
```

Use `/compile-latex` for the guided version.

---

## 6. Agent System

This repo uses a selective clo-author-style worker/critic system.

Codex and Claude use different discovery conventions:

- Codex reads `AGENTS.md` for project instructions, `.agents/skills/*/SKILL.md` for repo skills, `.codex/agents/*.toml` for project custom agents, and `.codex/hooks.json` for project hooks after the project `.codex/` layer is trusted.
- Claude Code reads the parallel `.claude/` setup: `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, `.claude/settings.json`, and `.claude/hooks/`.
- Shared research rules and references intentionally stay in `.claude/rules/` and `.claude/references/`; Codex is pointed to them from `AGENTS.md` and from the Codex skills/agents.
- Do not create `.codex/skills/`; repo-scoped Codex skills belong in `.agents/skills/`.

| Worker | Critic | Purpose |
|--------|--------|---------|
| `librarian` | `librarian-critic` | literature and citation fidelity |
| `explorer` | `explorer-critic` | exploratory analysis discipline |
| `strategist` | `strategist-critic` | design and identification |
| `coder` | `coder-critic` | reproducible implementation |
| `writer` | `writer-critic` | paper drafting and claim discipline |
| `storyteller` | `storyteller-critic` | talks derived from the paper and slide-writing principles |

Standalone agents include `data-engineer`, `domain-referee`, `methods-referee`, `editor`, `orchestrator`, and `verifier`.

Core rule: **workers create, critics evaluate, creators do not self-score.**

---

## 7. Quality Gates

| Score | Meaning |
|-------|---------|
| 80 | Commit threshold |
| 90 | PR / serious internal review |
| 95 | Submission or excellence candidate |

Weighted paper components:

| Component | Weight |
|-----------|--------|
| Literature | 10% |
| Data | 10% |
| Identification | 25% |
| Code | 15% |
| Paper | 25% |
| Polish | 10% |
| Replication | 5% |

The authoritative rubric lives in `.claude/rules/quality-gates.md`. Quick checks can be run with:

```bash
python3 code/03_quality/quality_score.py docs/deliverables/articles/main/main.tex
```

---

## 8. Single Source Of Truth

Authoritative:

- `data/raw/*`
- `code/**`
- `docs/deliverables/articles/main/main.tex`
- `docs/deliverables/articles/main/sections/*.tex`
- `docs/sources/references.bib`

Derived:

- `data/clean/*`
- `data/tmp/*`
- `results/*`
- Beamer talks
- compiled PDFs

If a derived output looks wrong, fix upstream code and rerun the pipeline. Do not patch generated outputs by hand.

---

## 9. Quick Reference

**Make targets:** `setup`, `fetch`, `build`, `analysis`, `all`, `clean`

**Paper workflow:** `/discover`, `/strategize`, `/analyze`, `/write`, `/review`, `/revise`, `/talk`, `/checkpoint`, `/tools`

**Existing utilities:** `/compile-latex`, `/validate-bib`, `/proofread`, `/review-paper`, `/review-r`, `/data-analysis`, `/slide-excellence`, `/visual-audit`, `/pedagogy-review`, `/devils-advocate`, `/commit`, `/learn`, `/context-status`

**Key folders:**

```text
code/{00_fetch,01_build,02_analyze,03_quality,99_explorations}
data/{raw,clean,tmp}        results/
docs/sources/               docs/deliverables/{articles,slides,appendices,preambles,assets}
docs/work/{plans,task_requirements,session_logs,checkpoints,reviews,merge_reports,templates}
.claude/references/
```

---

## 10. Reset For Your Next Project

Clear project-specific artifacts before using the template again:

- project-specific contents in `data/**`, preserving `.gitkeep` placeholders
- generated `results/**`, preserving `.gitkeep` placeholders
- `docs/work/{plans,session_logs,reviews,merge_reports,checkpoints}/*`
- project-specific entries in `docs/sources/`
- paper/slides/appendix contents under `docs/deliverables/`
- project-specific `[LEARN]` entries in `MEMORY.md`

Keep the scaffold, rules, skills, agents, hooks, `Makefile`, and folder structure. For Codex template portability, commit `.agents/skills/`, `.codex/agents/`, `.codex/hooks.json`, and `.codex/hooks/` when they contain only repo-portable scripts and no local auth or secrets.
