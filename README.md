# Research project template

This template starts an empirical research project with staged code, a canonical paper,
Beamer talks, and a small set of agent skills. It builds on
[Pedro Sant'Anna's workflow](https://github.com/pedrohcgs/claude-code-my-workflow) and
[Hugo Sant'Anna's paper-focused fork](https://github.com/hugosantanna/clo-author).

## Where work lives

| Path | Purpose |
|---|---|
| `code/00_fetch/`, `code/01_build/`, `code/02_analyze/` | Numbered pipeline entry scripts, run in order by Make |
| `code/lib/` | Shared R, Python, and Julia input/run-record helpers |
| `code/99_explorations/` | Trial plots and diagnostics, outside the canonical pipeline |
| `data/raw/`, `data/clean/`, `data/tmp/` | Source, assembled, and temporary data |
| `results/` | Generated tables, figures, and model outputs |
| `docs/deliverables/articles/main/main.tex` | Canonical paper |
| `docs/deliverables/slides/` | Beamer talks derived from the paper |
| `pending-approval/` | Issue-specific candidate code, outputs, spec, and review |
| `docs/work/` | Archived specs, plans, and factual session logs |

Each entry script names its inputs and outputs in the source and explains its
current purpose and substantive choices there. For work that generates data or
results, the shared helper records the direct inputs the script registers, their
observed modification times, and the last run's status beside each output. A
directory or filename pattern registers many files in one lightweight call. The
record does not discover undeclared reads or prove the old inputs' contents.

## Working with agents

`AGENTS.md` holds the few rules that always apply. Skills in `.agents/skills/`
provide task-specific procedures for Codex; `.claude/skills/` links to the same
files for Claude Code. Leo makes substantive research choices. Agents can advise,
teach when asked, and implement settled choices. An instruction becomes lasting
only when Leo deliberately adds it to a routed project file or skill.

For tracked work, invoke `open-issue`, settle the choices, then invoke `to-spec`
or `grill-to-spec`. The spec describes one change to the repository and lists
independently shippable components. `implement` builds candidates under that
issue's `pending-approval/` folder; `code-review` checks them separately.
Invoke `ship` with the particular components to move the reviewed files and
outputs into their production paths. Invoke `close-issue` after every component
is shipped; it archives the unchanged spec, commits, pushes, and closes the
issue. `sitrep` reads issue progress from the spec and files, without a separate
status ledger. A small, exact edit can go straight to the working copy, and
exploration needs no issue or spec unless Leo wants it tracked.

`implement` uses a Luna agent at `xhigh` effort in Codex and a Sonnet agent at
`xhigh` effort in Claude Code unless Leo specifies a model and effort together.
`unslop` applies to all natural-language text Leo will read. Other action skills
require explicit invocation. See [the user guide](docs/sources/USER-GUIDE.md)
for their names and boundaries.

## Commands

Run `make help` for the target list. `make setup` restores available lockfiles.
`make fetch`, `make build`, and `make analysis` run numbered `.R`, `.py`, `.jl`,
and `.sh` entry scripts in their respective folders. `make all` runs the three
stages in sequence, then `make check`. `make check` verifies the harness wiring,
bibliography keys, and shared-helper tests. `make articles`, `make slides`, and
`make latex` compile the paper and talks when a TeX installation is available.

Existing files under `data/raw/` are append-only. A narrow Claude/Codex hook
blocks direct agent edits to those files; scripts and other indirect writes still
need care. Generated results should be changed by editing and rerunning their
producer, not by hand.
