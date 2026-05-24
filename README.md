# Personal Research Project Template

This is my personal research project template. It is based on Pedro Sant'Anna's original [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) template and Hugo Sant'Anna's paper-focused fork, [hugosantanna/clo-author](https://github.com/hugosantanna/clo-author), with project structure, naming, document organization, Makefile conventions, and paper-first workflow adjusted to my taste.

The template is designed for empirical paper projects using staged code, host-native Make targets, and a paper-first Claude/Codex workflow.

This version includes:
- a canonical paper at `docs/deliverables/articles/main.tex`
- staged code folders (`code/00_fetch`, `code/01_build`, `code/02_analyze`)
- explicit host-native file-based pipelines via `make`
- lockfile-based dependency setup when available
- Beamer only for presentations, with talks derived from the paper
- selective clo-author-style worker/critic agents and paper quality gates
- tracked placeholder folders, including `data/` and `results/`; add project-specific ignore rules only after forking if desired

---

## Project Layout

```text
.
├── AGENTS.md
├── CLAUDE.md
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
- The canonical manuscript is `docs/deliverables/articles/main.tex`.
- Section files live in `docs/deliverables/articles/sections/`.
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
- `docs/deliverables/articles/main.tex`
- `Makefile` target/output names, if your project needs a custom dependency graph

---

## Make Targets

Run `make help` to view target descriptions.

Default template targets include:
- `setup`: restore lockfile dependencies if present
- `fetch`, `build`, `analysis`: staged project tasks
- `all`: run the full host-native pipeline
- `clean`: remove generated artifacts

---

## Paper Compile Reference

```bash
cd docs/deliverables/articles
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
if grep -q "\\citation" main.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex main; fi
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
TEXINPUTS=../preambles:./sections:$TEXINPUTS xelatex -interaction=nonstopmode main.tex
```

## Beamer Talk Compile Reference

```bash
cd docs/deliverables/slides
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
if grep -q "\\citation" talk.aux; then BIBINPUTS=../../sources:$BIBINPUTS bibtex talk; fi
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
TEXINPUTS=../preambles:$TEXINPUTS xelatex -interaction=nonstopmode talk.tex
```

---

## Quality Gates

- `80`: commit threshold
- `90`: PR threshold
- `95`: submission/excellence threshold

Weighted paper quality lives in `.claude/rules/quality-gates.md`. Reviews and checkpoints live in `docs/work/`.
