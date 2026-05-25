# Personal Research Project Template

This is my personal research project template. It is based on Pedro Sant'Anna's original [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) template and Hugo Sant'Anna's paper-focused fork, [hugosantanna/clo-author](https://github.com/hugosantanna/clo-author), with project structure, naming, document organization, Makefile conventions, and paper-first workflow adjusted to my taste.

The template is designed for empirical paper projects using staged code, host-native Make targets, and a paper-first Claude/Codex workflow.

This version includes:
- a canonical paper at `docs/deliverables/articles/main/main.tex`
- staged code folders (`code/00_fetch`, `code/01_build`, `code/02_analyze`)
- explicit host-native file-based pipelines via `make`
- lockfile-based dependency setup when available
- Beamer only for presentations, with talks derived from the paper
- slide-writing standards adapted from Paul Goldsmith-Pinkham's Beamer tips
- selective clo-author-style worker/critic agents and paper quality gates
- tracked placeholder folders, including `data/` and `results/`; add project-specific ignore rules only after forking if desired

---

## Project Layout

```text
.
├── AGENTS.md
├── CLAUDE.md
├── .agents/                # Codex repo skills
├── .codex/                 # Codex project agents and hooks
├── .claude/                # Claude Code agents, skills, hooks, rules, references
├── Makefile
├── code/
│   ├── 00_fetch/
│   ├── 01_build/
│   ├── 02_analyze/
│   ├── 03_quality/
│   └── 99_explorations/
├── data/                   # Tracked empty scaffold; add project policy after fork
│   ├── raw/
│   ├── clean/
│   └── tmp/
├── results/                # Generated tables, figures, model outputs
└── docs/
    ├── sources/             # External reference/input documents + references.bib
    ├── work/                # Plans, task requirements, logs, checkpoints, reviews
    └── deliverables/        # Articles, slides, appendices, preambles, document assets
```

---

## Workflow Philosophy

### 1. The paper is the source of truth
- The canonical manuscript is `docs/deliverables/articles/main/main.tex`.
- Section files live in `docs/deliverables/articles/main/sections/`.
- Root article and slide documents live one per folder: `articles/<name>/<name>.tex` and `slides/<name>/<name>.tex`.
- `make latex` compiles every root `.tex` document under `articles/` and `slides/`.
- Slides and appendices derive from the paper's argument, notation, claims, tables, and figures.

### 2. Scripts are staged and explicit
- `00_fetch`: acquire raw inputs
- `01_build`: construct analysis datasets/objects
- `02_analyze`: estimate models and generate results
- `03_quality`: template utilities for scoring/checking files

### 3. Makefile encodes orchestration
- The root `Makefile` runs directly on the host
- Targets encode the staged pipeline: setup, fetch, build, analysis, all, clean

### 4. Results are generated, not hand-edited
- Generated empirical outputs belong in `results/`
- If a result looks wrong, fix upstream code and rerun the relevant Make target
- Paper and slides include generated outputs rather than copying numbers by hand

### 5. Worker and critic roles stay separate
- Creative agents draft or implement
- Critic agents review but do not create
- Quality gates use weighted paper components, with identification and paper quality carrying the most weight

### 6. Talks are simple, visual, and paper-derived
- Beamer talks follow `.claude/rules/slide-writing-principles.md`.
- New decks should use `docs/deliverables/preambles/beamer-preamble.tex` for 16:9 defaults, spacing helpers, color-blind-conscious accents, `\sectiontransition` dividers, and backup-slide helpers.
- A good talk request should include audience, duration, talk type/status, and goal; the agents then plan the Big 5 opening, intuition bridge, empirical credibility sequence, and review loop.
- Slides make one point at a time, with substantive frame titles, low-clutter data graphics, compact `booktabs`/`siunitx` tables, and non-hue-only encodings; dense tables, proofs, and robustness detail move to linked backup slides.

### 7. Agent customization is tool-native
- Codex intentionally uses both `.codex/` and `.agents/`. This differs from Claude Code, which puts agents, skills, hooks, and settings under `.claude/`.
- For Codex, `.codex/` is for project agents, hooks, and optional portable config: `.codex/agents/*.toml`, `.codex/hooks.json`, and `.codex/hooks/`.
- For Codex, `.agents/skills/` is the repo skill location: `.agents/skills/<skill-name>/SKILL.md`. Do not move these to `.codex/skills/`.
- Codex reads project instructions from `AGENTS.md`, repo skills from `.agents/skills/`, custom agents from `.codex/agents/*.toml`, and project hooks from `.codex/hooks.json` after the project `.codex/` layer is trusted.
- Claude Code keeps its parallel setup in `.claude/`: agents, skills, hooks, settings, rules, and references.
- Shared research calibration lives once in `.claude/rules/` and `.claude/references/`; Codex instructions point there instead of mirroring those files.

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
make setup
make help
```

Then customize:
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/references/domain-profile.md`
- `.claude/references/personal-style-guide.md`
- `.claude/references/journal-profiles.md`
- `.claude/rules/slide-writing-principles.md`
- `.agents/skills/` for Codex repo skills, if the project needs new workflows
- `.codex/agents/` for Codex project agents, if the project needs role changes
- `docs/deliverables/articles/main/main.tex`
- `Makefile` target/output names, if your project needs a custom dependency graph

---

## Make Targets

Run `make help` to view target descriptions.

Default template targets include:
- `setup`: restore lockfile dependencies if present
- `fetch`, `build`, `analysis`: staged project tasks
- `all`: run the full host-native pipeline
- `articles`: compile every root `.tex` document in `docs/deliverables/articles/`
- `slides`: compile every root `.tex` document in `docs/deliverables/slides/`
- `latex`: compile all article and slide documents
- `clean`: remove generated artifacts

---

## Paper Compile Reference

```bash
make articles
```

## Beamer Talk Compile Reference

```bash
make slides
```

---

## Quality Gates

- `80`: commit threshold
- `90`: PR threshold
- `95`: submission/excellence threshold

Weighted paper quality lives in `.claude/rules/quality-gates.md`. Reviews and checkpoints live in `docs/work/`.
