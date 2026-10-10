# Agent workflow guide

Leo decides what the research does. Agents identify consequential choices, explain
tradeoffs, recommend options, and implement his decisions. An agent may choose
equivalent coding details. It may not silently choose an estimand, sample,
aggregation, model, numerical method, or presentation claim that changes meaning.

For a task to track, invoke `open-issue`. It checks whether the request is one
deliverable and writes a short GitHub issue. Once the choices are settled,
`to-spec` writes one immutable change contract for that issue. For a difficult
task, invoke `grill-to-spec` instead: it surfaces hidden decisions and teaches
the concepts needed to choose before writing the same kind of spec. A spec
describes this change, not the script's permanent state.

Invoke `implement` to delegate settled work. Candidate code, outputs, checks,
and the spec stay together under `pending-approval/issue-<number>-<slug>/`.
Invoke `code-review` for an independent review, then invoke `ship` with the exact
component subset to accept. Shipping moves the reviewed outputs into production
and changes the candidate paths fixed in the scripts. It does not rerun an
approved output. When all components are shipped, invoke `close-issue` to
archive the spec, commit, push, and close the GitHub issue.

An exact small edit to an accepted script can go directly to the working copy
through `implement`, without a new issue or spec. Trial graphs and regressions
can be iterated under `code/99_explorations/`. They do not change canonical
results until Leo chooses a tracked promotion. `sitrep` reports open issue
components and recent logs. `handoff` writes a short temporary file for a new
session and immediately returns its path. `teach` explains a method only when
invoked.

The research skills are `discover`, `write-paper`, `review-paper`,
`write-slides`, and `review-slides`. Language preferences live in `coding-r`,
`coding-python`, and `coding-julia`; the implementer or reviewer receives only
the relevant one. All of these action/support skills require deliberate use.
`unslop` is the one automatic skill because it governs every sentence Leo reads.

See [README](../../README.md) for the folder map and Make commands. The scripts
themselves document their current inputs, outputs, and analysis choices.
