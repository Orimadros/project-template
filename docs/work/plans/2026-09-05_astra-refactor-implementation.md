# Astra refactor: proposed changes and order of work

**Date:** 2026-09-05
**Updated:** 2026-10-05
**Status:** IMPLEMENTED — local checks pass; live GitHub lifecycle awaits the first real issue

## Objective

Replace the template's overlapping instructions and manual bookkeeping with a smaller
set of deliberately invoked skills, human-approved change contracts, and code that
explains and records its own work. Target future greenfield projects.

This roadmap directs the one-time refactor Leo authorized on 2026-10-05. Future tracked
changes use the issue-linked contracts established here.

## Clarity Status

| Aspect | Status | Agreement or remaining choice |
|---|---|---|
| Research authority | CLEAR | Leo makes substantive choices; agents advise and implement them. |
| Coding discretion | CLEAR | Agents follow prewritten standards and may choose equivalent implementations. |
| Issues and specifications | UPDATED | Use issues to track planned work Leo wants tracked; a spec-driven change has one issue and at most one immutable delta spec. Exact small edits and exploration do not require an issue or spec. |
| Specification path | CLEAR | `to-spec` records decisions already settled in conversation. Leo can invoke `grill-to-spec` for a deeper interview that surfaces decisions and relevant knowledge gaps before the same single spec is written. |
| Review location | CLEAR | `pending-approval/issue-<number>-<slug>/` contains candidate code, outputs, spec, and verification. |
| Inputs and output paths | UPDATED | Scripts contain fixed input and output paths, with no CLI path arguments. Candidate code points to files under its issue's `pending-approval/` folder. On `ship`, references to candidate files change to the production paths named in the spec, such as a dedicated `02_analyze/` path when that is the chosen destination. |
| Input records | CLEAR | In R, Python, and Julia, one helper call can register a fixed file pattern or directory for a multi-file dataset. It records each matched file's path and modification time using filesystem metadata only; it does not read or hash file contents or scan unrelated directories. Coverage is checked in code review. |
| Teaching and lasting preferences | CLEAR | Teaching is explicitly requested; nudges are selective; experience never becomes lasting instructions automatically. |
| Supported apps | CLEAR | Claude Code and Codex, with shared content and app-specific invocation/model settings. |
| Core work lifecycle | UPDATED | Tracked production changes use the issue/spec/review/ship/close path. Exact small edits can go directly to the working copy, and exploration stays in the exploration area; neither requires an issue or spec. |
| Small edits and exploration | CLEAR | Small, explicit tweaks to an active candidate stay under its existing issue without a new spec. After shipping, small explicit edits go directly to the working copy and are returned with a diff and relevant check. Exploratory plots and diagnostic regressions can be iterated without tickets, specs, or formal plans. |
| Implementation model | CLEAR | Default to Luna at extra-high effort in Codex and Sonnet at extra effort in Claude Code. Use another model and effort only when Leo explicitly specifies both. |
| Natural-language style | CLEAR | `unslop` applies to every human-facing natural-language string, including chat, documents, issue text, specs, reviews, commit messages, and code comments. Executable code syntax is outside its scope. |
| Issue progress state | CLEAR | `sitrep`, `ship`, and `close-issue` derive progress from the component paths in the immutable spec and the files in `pending-approval/` and their production locations. Do not maintain a separate status file. If existing production files make a component's state unclear, report that uncertainty rather than guess. No-spec tasks with no repository artifacts cannot be assessed from files; Leo closes them when done. |
| Session logs | CLEAR | Write factual logs at the end of substantial work without a blocking reminder hook; `sitrep` reads the three latest logs. |
| Other skill names and consolidation | APPROVED | Leo requested implementation of the proposed shortlist on 2026-10-05. |
| Rules and hooks | APPROVED | Remove automatic path-based rule injection and retain a narrow raw-data guard. |
| Shipping generated outputs | CLEAR | `ship` changes hard-coded paths and moves the exact reviewed output to its production path, preserving the original run record and recording the new location. |
| Acceptance and task recovery details | CLEAR | `ship` moves the reviewed output, `close-issue` archives the spec, and `sitrep` derives progress from the issue, spec, review, diff, and files. |
| Existing projects | CLEAR | Migration is deferred. |

## Requirements

### MUST

- [x] Preserve the decisions in ADRs 0001–0004 and the interview record.
- [x] Agree on the skill shortlist, its invocation rules, and examples before installing replacements or deleting existing skills.
- [x] Draft every new or rewritten skill while following `writing-for-agents`, including its mechanics reference.
- [x] Apply `unslop` to everything agents write in natural language for Leo, including prose embedded in code; put this universal trigger in the skill description.
- [x] Use GitHub issues for planned work Leo wants tracked. Do not require an issue or spec for a small, explicit edit or an exploratory session. `open-issue` remains available when Leo wants a task tracked.
- [x] Do not require a formal plan document for small direct edits or exploratory sessions; the user request is enough to start those bounded tasks.
- [x] Associate every spec with exactly one issue and allow no more than one spec per issue. Tracked work that needs no repository change may have no spec.
- [x] Offer two user-invoked ways to write a spec: `to-spec` for a settled discussion, and `grill-to-spec` when Leo wants a thorough decision interview. `grill-to-spec` must identify consequential choices and likely hidden choices, explain unfamiliar concepts needed to choose, present options and tradeoffs, and give a reasoned recommendation. Leo makes every substantive choice; if a required choice remains open, do not write a ready-to-implement spec.
- [x] Keep code and the explanation of its current behavior together; maintain no separate manual for every script.
- [x] For spec-driven changes, route implementation through the agreed contract, active-harness model default, separate code review, and Leo's explicit `ship` request. For an exact small edit, use the user's request as the brief, edit the working copy directly, and show the diff and relevant check; do not create an issue, spec, or candidate folder, or commit/push automatically.
- [x] Let small refinements to an active pending candidate continue under the same issue and spec. Keep that spec unchanged; code review considers it alongside Leo's later explicit instructions.
- [x] Let exploratory plots and diagnostic regressions run without an issue or spec in `code/99_explorations/` with temporary outputs. Do not promote exploratory artifacts into canonical pipeline or paper locations until Leo chooses a result for a tracked change.
- [x] Require each `ship` request to identify the subset to incorporate. Ask Leo to choose from the pending components when the subset is unclear.
- [x] Close an issue only through `close-issue`, after every spec component is shipped or the no-spec task is complete.
- [x] Set `disable-model-invocation: true` in the Agent Skills frontmatter for every user-invoked action skill in both Codex and Claude Code. Keep `unslop` model-invoked.
- [x] Supply only relevant coding preferences and helpers to each implementer and code reviewer.
- [x] Record registered direct inputs and their local modification times without claiming automatic discovery of all reads or historical reconstruction. A multi-file dataset can be registered with one fixed directory or file-pattern declaration, which the helper expands to individual file records without reading or hashing file contents.
- [x] Remove automatic learning and the instructions that promote task corrections into memory or skills.
- [x] Preserve raw-data protection, canonical data use, generated results, and applicable paper/talk verification.
- [ ] Verify the full issue-to-closure workflow with concrete examples in R, Python, and Julia; helper examples pass locally, but the GitHub lifecycle awaits the first real issue.
- [x] Make `sitrep` report every open issue by shipped, pending-approval, and unimplemented work; include the three latest closed-issue titles and a summary of the three latest session logs.
- [x] Make `handoff` write to the operating system's temporary directory and immediately report the exact file path.

### SHOULD

- [x] Keep root instructions to a few obligations and pointers; move conditional detail to the place that uses it.
- [x] Reduce the number of commands without losing useful literature, writing, or review capabilities.
- [x] Let the planning conversation continue while a named, smaller model implements an approved change.
- [x] Replace mandatory numerical workflow grades with relevant checks, explicit findings, and Leo's approval through `ship`; retain substantive review rubrics on demand.

### MAY

- [ ] Retain additional standalone research commands if Leo uses them enough to justify separate entry points.
- [ ] Add support for further languages when a project needs them, using the same helper behavior.

## Proposed tracked-work, direct-edit, and exploration workflow

The workflow adapts three Matt Pocock skills to a research repository:

- [`to-spec`](https://www.aihero.dev/skills-to-spec) turns an already completed
  discussion into a handoff document.
- [`implement`](https://www.aihero.dev/skills-implement) executes work whose decisions
  are already settled.
- [`code-review`](https://www.aihero.dev/skills-code-review) checks the result separately
  against the spec and the repository's coding standards.

We omit the separate ticket-conversion step in the referenced software workflow. A change
contract in this template is usually small enough to pass directly to one implementer.

Use the issue/spec route for planned changes Leo wants tracked through delivery, especially
changes to canonical data, analysis, or paper outputs and work that needs substantive decisions
settled in advance. `open-issue` is optional; it creates a concise issue only when Leo invokes
it to track a task. A no-code task may have an issue without a spec.

For tracked work, Leo settles the research and design choices before `to-spec` writes the
issue's one immutable change contract. The spec lists each candidate path and its intended
production path. It does not record future repository state. `to-spec` does not lead research
interviews, suggest missing choices, or turn assumptions into requirements; if a decision is
open, it reports the gap.

For long or technically difficult work, Leo can invoke `grill-to-spec` instead. It borrows the
question-led, persistent interview style of Leo's `grill-with-docs` skill, adapted to prepare
one implementation contract. It maps decisions the work requires, including choices that may
be easy to miss before implementation, and explains why each consequential choice matters.
When Leo needs background to choose, it teaches the relevant concepts first, then lays out
practical options, tradeoffs, and a clear recommendation with reasons. Leo chooses; the skill
must not turn its recommendation or an unstated assumption into a requirement. For example,
planning a numerical solution to a dynamic model may require Leo to choose what can be solved
analytically and what needs numerical integration, which quadrature method fits the problem,
and how the dynamic program will represent and solve its state and value function.
`grill-to-spec` should raise the choices that apply, teach enough for Leo to decide, and pause
for his answers. It writes the same single issue-linked delta contract as `to-spec` only after
the consequential choices are settled. If a decision cannot yet be made, it records no ready
spec and identifies what remains to resolve. Use this path only when Leo invokes it; it is not
a general license to teach or interview during ordinary work. It creates no extra ADR or
glossary by default.

`implement` delegates spec-based implementation using the active harness default: Luna at
extra-high effort in Codex or Sonnet at extra effort in Claude Code. Use a different model and
effort only when Leo explicitly names both. The implementer works in
`pending-approval/issue-<number>-<slug>/`, uses fixed paths in scripts, and runs the checks in
the spec. It reports newly discovered substantive choices instead of making them.
`code-review` independently compares that candidate with the original spec and the applicable
coding and research standards.

While a candidate remains pending approval, a small refinement Leo specifies stays in that
candidate under the same issue; do not open another issue or write another spec. Leave the
original spec unchanged. A later code review considers it alongside Leo's explicit follow-up
instructions. Leo invokes `ship` with the subset to incorporate. `ship` moves only those
reviewed files into production, adjusts their hard-coded output paths, removes their candidate
artifacts while preserving the spec and review report, and checks the remaining components. It
does not commit, push, or close the issue. Once every spec change is verifiably in production,
`ship` suggests `close-issue`; Leo invokes that skill to commit the issue's files, push, and
close the GitHub issue.

For a small, exact edit after its issue has shipped or closed, Leo may invoke `implement` with
the edit request itself as the brief; no new issue, spec, or pending-approval folder is needed.
The implementer edits the working copy, runs the relevant check, and returns a diff. It does
not commit or push unless Leo asks. Update script comments when the edit changes a substantive
analysis choice. If the request leaves a research choice open, the agent asks Leo rather than
choosing. If the edit materially changes the research
design or a durable deliverable, recommend the tracked route and let Leo decide whether to open
an issue.

Exploratory plotting and diagnostic regressions need no issue or spec. Leo can iterate in
`code/99_explorations/` and a temporary output location without moving each trial through
review and shipping. These trials do not update canonical pipeline or paper outputs. If Leo
chooses a result for permanent use, he can then open one issue and spec for the change that
promotes it. He may open a no-spec issue if he wants the exploration itself on his task list.

`close-issue` also handles no-spec tracking tasks when Leo says they are complete. Exploratory
work and direct edits are not automatically added to GitHub issues. `sitrep` reports issues and
their deliverables; it does not label scratch iterations as issue components.

Each invoked stage receives bounded context. `implement` does not recursively call
`code-review`; separate review keeps the comparison independent of implementation reasoning.

## Skill set

The slash notation is shorthand here; use the invocation syntax of the current app.

| Skill | What it does | When its instructions are supplied |
|---|---|---|
| `unslop` | Applies Leo's writing standard to every human-facing natural-language string, including replies, documents, issues, specs, reviews, commit messages, and prose inside code. | Model-invoked for every natural-language output. Its description carries the universal trigger. |
| `open-issue` | Checks that work Leo wants tracked is one atomic unit, then creates a concise GitHub issue stating the problem and what counts as done. If it recommends a split, it asks Leo before creating anything. | Leo invokes it when he wants a task tracked. |
| `to-spec` | Turns an agreed conversation into the issue's single delta-based change contract. It records decisions; it does not make them or reopen the discussion. | Leo invokes it after the conversation is settled and the issue exists. |
| `grill-to-spec` | Interviews Leo about a difficult tracked change, surfaces consequential and likely hidden decisions, teaches relevant concepts when needed, compares options, and recommends a path. It writes the same single delta contract only after Leo has made the decisions. | Leo invokes it when he wants a thorough design interview, especially for long or technically difficult work; the issue must exist. |
| `implement` | Delegates either an issue's completed spec or Leo's exact small-edit request using the active harness default: Luna at extra-high effort in Codex or Sonnet at extra effort in Claude Code. Spec work goes to the issue's pending-approval folder; a post-ship small edit goes directly to the working copy. | Leo invokes it with a completed spec or an exact edit request. |
| `code-review` | Reviews a spec candidate against its original spec and applicable standards, or a direct edit against Leo's explicit request and applicable standards. It reports findings without editing. | Leo invokes it when an independent review is wanted. |
| `ship` | Incorporates only the reviewed pending components Leo names, changes their hard-coded references from `pending-approval/` to the production paths in the spec, and reports progress by checking those paths. | Leo invokes it with the subset to ship. |
| `close-issue` | Verifies that the issue is complete, commits its repository changes, pushes the current branch, and closes the GitHub issue. It also closes no-spec tracking issues when their deliverable is complete. | Leo invokes it. |
| `sitrep` | Reports all open issues with shipped, pending-approval, and unimplemented components; names the three latest closed issues; and summarizes the three latest session logs with recent decisions and discoveries. | Leo invokes it. |
| `teach` | Teaches a requested concept in Leo's preferred way, without implementing a research change or judging whether he may proceed. | Leo invokes it. |
| `discover` | Searches literature and sources, synthesizes findings, and verifies citations. | Proposed separate user command; confirm whether Leo wants it. |
| `write-paper` | Drafts or revises paper text using settled claims, sources, and writing preferences. | Proposed separate user command; confirm whether Leo wants it. |
| `review-paper` | Reviews a canonical or external paper. The request selects the lens, such as referee review, methods, or focused proofreading; code and slides are outside its scope. | Leo invokes it. |
| `write-slides` | Creates or revises Beamer slides from the canonical paper and generated results, following `.claude/rules/slide-writing-principles.md` and the shared preamble. | Proposed separate user command; confirm whether Leo wants it. |
| `review-slides` | Reviews a rendered talk for its argument, pedagogy, and visual layout without editing the deck. | Proposed separate user command; confirm whether Leo wants it. |
| `handoff` | Writes Matt Pocock's compact handoff document outside the workspace in the operating system's temporary directory, then immediately tells Leo the exact path. | Leo invokes it, optionally describing the next session's focus. |
| `coding-r` | R preferences, script documentation, canonical data use, and shared R helpers. | Deliberately supplied for approved R work and R code review. |
| `coding-python` | Python preferences, script documentation, and shared Python helpers. | Deliberately supplied for approved Python work and Python code review. |
| `coding-julia` | Julia preferences, script documentation, and shared Julia helpers. | Deliberately supplied for approved Julia work and Julia code review. |

Keep issue creation, teaching, specification, implementation, review, shipping, issue closure,
status reporting, and handoff explicitly requested. Set `disable-model-invocation: true` in the
Agent Skills frontmatter of each user-invoked skill; Codex and Claude Code use the same standard
setting. `unslop` is the deliberate exception: it stays model-invoked because every agent must
reach it before producing natural language Leo will read. The language coding skills remain
support skills that `implement` and `code-review` can reach only in their approved workflows.

A reviewer reports choices that need attention; it does not make those choices. A proofreading
request must not silently launch a full methods review. The writing preference applies to
replies, not just deliverables.

The proposed `unslop` description is:

> Apply Leo's writing standard to every natural-language string he will read, including chat
> replies, plans, specifications, issues, documentation, reviews, commit messages, and comments
> or prose inside code. Use whenever producing or editing human-facing natural language;
> executable code syntax is outside scope.

Write the other user-invoked descriptions as one-line human-facing summaries. Their bodies,
not their descriptions, contain the workflow branches.

Every skill above must be written using `writing-for-agents`. In practice, its authoring pass
must give the skill a narrow purpose, explicit invocation and completion criteria, concrete
examples, and pointers to context that already exists. Supporting material belongs beside the
skill or in one shared reference when several skills need it. Do not repeat the same instructions
in the root file, skill body, and reference files.

Use `disable-model-invocation: true` in the Agent Skills frontmatter for explicit-only skills in
both apps, then verify that both harnesses honor it. Passing a known preference file's content
to an implementer is deliberate context supply, not automatic skill selection. Do not assume
Claude's preload field can load an explicit-only skill; pass the required contents or readable
reference paths directly.

## Derive issue progress from files

Do not create a separate mutable status file or GitHub checklist. Each spec must name the
candidate path and intended production path for every repository component. When `sitrep`,
`ship`, or `close-issue` runs, it reads the open issues and their specs, then checks those paths:

- A candidate artifact at its issue's `pending-approval/` path is pending approval.
- A shipped component is at its intended production path, and its candidate artifact has been
  moved out of `pending-approval/`. Preserve the spec and review report there until the issue
  closes, but remove or move the shipped candidate artifacts so their location shows progress.
- A component at neither location has not been written yet.
- If a production file existed before this issue, inspect its current diff or history to see
  whether this issue's change is present. If that still does not resolve it, report the state as
  unclear and ask Leo; do not treat file existence alone as proof.

`close-issue` uses the spec's paths to identify the files to commit and checks for unfinished or
unclear components, unrelated worktree changes, and path conflicts with other open issues. For
a no-spec issue, there may be no repository files to inspect. `sitrep` reports it as an open
tracking issue without claiming whether Leo's off-repository work is complete; Leo closes it
when done. A completed no-spec issue with no repository changes closes without an empty commit.

## Implementation model and effort by harness

`implement` delegates to one implementer by default. In Codex, use Luna at extra-high effort;
in Claude Code, use Sonnet at extra effort. If Leo explicitly names both a model and an effort
level, use that pair instead. Do not infer an override from naming only a model or only an effort.
If the active harness cannot run the requested pair, report that limitation and ask Leo how to
proceed rather than silently substituting another model or effort. Additional implementers are
appropriate only when the spec divides into non-overlapping file sets with explicit ownership.
The main agent keeps the planning conversation available and orchestrates the implementation.

## Handoff behavior

Base `handoff` on Matt Pocock's
[`handoff` skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md):

- save the document in the operating system's temporary directory, outside the repository;
- include suggested skills for the next agent;
- point to existing issues, specs, ADRs, commits, and diffs instead of copying their contents;
- redact secrets and personal information;
- tailor the document to any focus Leo supplies with the command; and
- after writing the file, immediately tell Leo its exact temporary path so he can copy it into
  a new session.

The temporary handoff is not a session log, issue record, or lasting project instruction.

## Proposed replacement for rules and hooks

The repository currently has 22 files under `.claude/rules/` and 12 shared hook scripts.
Together they contain about 3,600 lines. Much of their content remains useful, but the current
delivery mechanism repeats instructions, injects them after ordinary tool calls, and runs
reminder scripts whether or not the current task needs them.

Use four layers with distinct jobs:

| Layer | Job | Proposed contents |
|---|---|---|
| `AGENTS.md` | A few obligations needed in every task | Leo owns substantive decisions; issues track work he wants tracked; small direct edits and exploration need no issue/spec; lasting instructions require his deliberate authorship; pointers to the skills. |
| Skills and their references | Instructions needed for one named task | Coding standards, paper and slide standards, PDF reading, replication, review rubrics, and verification steps. A skill reads only the relevant material. |
| Make commands and CI | Checks a machine can actually run | Tests, compilation, bibliography checks, file naming where it matters, and conformance of the small remaining agent setup. |
| Hooks | Prevent immediate damage before a command runs | One narrow guard against changing existing files in `data/raw/`. Desktop notification may remain as an optional convenience. |

Skills do not replace mechanical checks or safeguards. They replace conditional prose and
procedures. Make and CI replace reminders about commands that can be tested. A hook remains
appropriate only when it is deterministic, cheap, and must act before damage occurs. It must
not infer research intent, estimate context use, or decide what the agent should remember.

Removing `.claude/rules/` as an auto-loaded layer also removes the need for Codex's
`rule-injector.py`. Retained material should move to one canonical reference reached from the
skill that needs it. For example, `write-slides` and `review-slides` can both point to one
shared slide-writing reference. Claude and Codex then receive the same content by following
the same pointer rather than through two different loading systems.

### Disposition of the current rule files

| Current rule | Proposed action | Destination or reason |
|---|---|---|
| `agents.md` | Remove | The separate implementer and reviewer skills define their own roles. |
| `beamer-integrity.md` | Combine | `write-slides` and `review-slides`; keep the paper and generated results as sources. |
| `content-invariants.md` | Split and remove | Put code, paper, and slide requirements in their corresponding skills; discard repeated statements. |
| `content-standards.md` | Split and remove | Paper/table/figure standards go to `write-paper`, `review-paper`, `write-slides`, or `review-slides`. |
| `exploration-fast-track.md` | Simplify | Exploratory plots and diagnostics need no issue/spec, stay under `code/99_explorations/`, and do not change canonical outputs; drop scores, logs, and archive steps. |
| `exploration-folder-protocol.md` | Simplify | Keep only the boundary that exploratory work stays in `code/99_explorations/` and outside canonical outputs; remove nested folder, scoring, logging, and archive ceremony. |
| `knowledge-base-template.md` | Remove | Its empty registries are state documentation that will drift. Use code, the paper, `CONTEXT.md`, and deliberate ADRs. |
| `no-pause-beamer.md` | Combine | One paragraph in the shared slide-writing reference. |
| `orchestrator-research.md` | Remove | Replaced by the issue, spec, implementation, review, shipping, and closure lifecycle. |
| `pdf-processing.md` | Shorten and move | A conditional reference for `discover` and paper-reading tasks; retain text extraction plus visual inspection when layout matters. |
| `plan-first-workflow.md` | Remove | Tracked work uses its issue and `to-spec`; exact small edits and exploration need no formal plan. |
| `proofreading-protocol.md` | Combine | Focused modes of `review-paper` and `review-slides`. |
| `provenance-ledger.md` | Retire after replacement | Replaced by input registration and generated run records. |
| `quality-gates.md` | Remove | Specs state concrete acceptance checks; review skills retain relevant substantive rubrics without universal numerical scores. |
| `r-code-conventions.md` | Move | Becomes the reference owned by `coding-r`, pruned to the standards Leo selects. |
| `replication-protocol.md` | Move conditionally | `implement` and `code-review` read a replication reference only when Leo has requested a replication task. |
| `revision.md` | Remove | Discuss and choose the response first, then use `to-spec` for the agreed changes. |
| `single-source-of-truth.md` | Reduce and split | Keep a thin repository map in `CONTEXT.md`; move operational requirements to the relevant skills and keep raw-data protection in the hook. |
| `slide-writing-principles.md` | Retain as a reference | Move it out of the auto-loaded rules directory; `write-slides` and `review-slides` point to the same file. |
| `tikz-visual-quality.md` | Retain conditionally | Slide or paper skills read it only when creating or reviewing TikZ. |
| `verification-protocol.md` | Split and remove | Each implementation or writing skill runs the relevant Make command; CI checks stable repository-wide requirements. |
| `working-paper-format.md` | Shorten and move | Reference for `write-paper` and `review-paper`. |

### Disposition of the current hook scripts

| Current hook | Proposed action | Reason |
|---|---|---|
| `context-monitor.py` | Remove | It converts tool-call count into a false context percentage and prompts automatic skill creation. |
| `log-reminder.py` | Remove | It blocks stopping to force session-log updates. Keep factual logs for `sitrep`, but write them through the agreed lifecycle rather than a Stop-hook interruption. |
| `pdf-read-guard.py` | Remove | PDF handling belongs to the task skill; blocking every direct source-PDF read is unnecessary. |
| `plan-name-check.py` | Remove | `to-spec` creates the correct name; a simple Make check can catch malformed names without steering every session. |
| `pre-compact.py` | Remove | It guesses the active plan, scrapes recent bullets as decisions, and modifies the latest session log. |
| `post-compact-restore.py` | Remove | Both harnesses already perform conversation compaction; this hook adds a second recovery system based on guessed plan state. Use an explicit handoff for another session, and add a small resume pointer later only if testing shows a real loss. |
| `provenance-reminder.py` | Retire with the Asset Graph | It runs graph validation after tools, on prompts, and when stopping. |
| `rule-injector.py` | Remove | No path-scoped rules remain to inject into Codex. |
| `verify-reminder.py` | Remove | `implement`, review skills, Make, and CI supply and run the relevant checks. |
| `lock-raw-data.sh` | Remove as a separate hook | Fold the useful protection into one pre-command raw-data guard; do not chmod or apply immutable flags after ordinary tool calls. |
| `protect-files.sh` | Replace | Write a much smaller cross-harness hook that protects only existing `data/raw/` files. Do not block ordinary edits to settings, bibliography, style references, or meeting notes. |
| `notify.sh` | Keep only if desired | It is a desktop convenience and does not affect the agent's reasoning or repository correctness. |

The recommended end state therefore has one required hook script and, if useful, one
notification script. Both Claude and Codex point to the same files. Removing the other hooks
also requires simplifying `.claude/settings.json`, `.codex/hooks.json`, the conformance checker,
tests, README, and the cross-agent guide so they do not preserve the old architecture indirectly.

## Disposition of all 27 current skills

These are recommendations based on overlap and the agreed workflow, not claims about usage.
Remove an entry only after its retained capability has a working destination.

| Current skill | Proposed action | Destination or reason |
|---|---|---|
| `analyze` | Combine | `implement`; preserve narrow regeneration and reporting affected paper claims. |
| `data-analysis` | Combine | `implement` plus language preferences; remove duplicated workflow. |
| `interview-me` | Retire as an entry point | Research-design discussion happens in the main conversation. It is not part of `to-spec`. |
| `strategize` | Retire as an entry point | Leo and the main agent can discuss estimands, identification, and threats before invoking `to-spec`. |
| `research-ideation` | Retire as an entry point | Idea generation remains ordinary user-requested discussion; it does not belong in the handoff writer. |
| `revise` | Retire as a general entry point | Discuss the response and choose changes first; use `to-spec` only after those changes are agreed. |
| `discover` | Retain provisionally | Rewrite around explicit invocation and the new authority rules. |
| `lit-review` | Combine provisionally | `discover`; preserve synthesis, disagreements, verified BibTeX, and publication status. |
| `write` | Rename provisionally | `write-paper`; rewrite around settled claims and deliberately loaded preferences. |
| `talk` | Rename and narrow | `write-slides`; use `.claude/rules/slide-writing-principles.md` and keep review outside the writing skill. |
| `review` | Split, then remove | Replace the general dispatcher with `code-review`, `review-paper`, and `review-slides`. |
| `review-paper` | Rewrite | Preserve canonical-paper and external-paper review. |
| `review-r` | Combine | `code-review` plus `coding-r`; preserve file/stage/all scope where useful. |
| `proofread` | Convert to selectively read guidance | Paper proofreading belongs to `review-paper`; slide proofreading belongs to `review-slides`. Include appendices when reviewing the paper. |
| `devils-advocate` | Convert to selectively read guidance | `review-paper` or `review-slides` reads the questions only when Leo requests that lens. |
| `pedagogy-review` | Combine | `review-slides`; preserve narrative and audience checks. |
| `visual-audit` | Combine | `review-slides`; preserve rendered-layout inspection. |
| `slide-excellence` | Combine | `review-slides`; preserve separate paper-consistency, pedagogy, prose, and layout findings. |
| `checkpoint` | Rename/rewrite | `handoff`; task facts, not general preferences. |
| `context-status` | Remove | Tool-call counts are not measured context occupancy. |
| `learn` | Remove | Automatic promotion of experience conflicts with Leo's instruction. |
| `provenance-ledger` | Retire after replacement | Shared helpers and generated run records replace universal manual records. |
| `inspect-asset-graph` | Retire after replacement | Ordinary inspection reads the generated record and named script. |
| `compile-latex` | Move guidance, then remove entry | Existing Make commands plus relevant compile/log checks. |
| `validate-bib` | Replace procedure, then remove entry | A small command covering paper, appendices, and talks; it does not yet exist. |
| `tools` | Remove after replacements | `make help` and ordinary command use; retire the extra command catalogue. |
| `commit` | Retire its automatic sequence | `ship` handles local incorporation; `close-issue` commits the issue's files, pushes, and closes it after Leo invokes the skill. |

`fisher-modelling` was not found in the checked locations. Its removal is not part of this
repository plan unless its actual location is identified and brought into scope.

## Order of work

### 1. Settle and draft the skills

Review the shortlist with Leo. Write `unslop` first so the remaining discussions and drafts
use his chosen style. Put its universal natural-language trigger in the model-facing
description and verify that ordinary chat, Markdown, issue text, commit messages, and code
comments all reach it.

Then draft `open-issue`, `to-spec`, `grill-to-spec`, `implement`, `code-review`, `ship`,
`close-issue`, and `sitrep` around the tracked-work and direct-edit routes above. Draft `teach`, `handoff`, the
language preferences, and the selected paper/literature/slide skills after their entry points
are confirmed.

Load `writing-for-agents` and its mechanics reference while drafting or revising every skill.
For `to-spec`, use the linked AI Hero skill only as a structural reference: the repository
version must require an existing issue and state that the discussion and decisions are already
complete. For `implement`, preserve the strict instruction to execute decided work without
reopening the plan and use the active harness default: Luna at extra-high effort in Codex or
Sonnet at extra effort in Claude Code. Leo may override both by explicitly naming a model and
effort. For `code-review`, preserve the
separate spec-adherence and standards axes and require a fixed comparison between the accepted
repository and the pending candidate. Do not add the software workflow's ticket stage. Write
`grill-to-spec` as the deeper, explicitly invoked path: it uses an iterative interview to find
decisions and knowledge gaps, teaches only what Leo needs to make those choices, presents
options with tradeoffs and a reasoned recommendation, and waits for Leo's decisions before
writing the same issue-linked delta contract. It must not create a ready spec while a required
substantive choice remains open, and it creates no extra design documents by default.

For each skill, agree on a realistic request, what information it reads, what it may do,
what it returns, and when it must return a choice to Leo. Include examples of a no-issue
working-copy edit and a no-issue exploratory session. Write the narrow path first;
put other branches behind explicit references. Keep one canonical copy of shared content.

Decide here: how and when factual session logs are written without the blocking hook; the
requested teaching style; and whether
`review-slides`, `discover`, and `write-paper` justify separate entry points. The workflow keeps
code review separately invoked and lets the implementation agent work while the main
conversation remains available to Leo.

### 2. Replace conflicting instructions and automatic learning

Shorten `AGENTS.md` around decision ownership, GitHub issues as work roots, the approved-change
workflow, deliberately supplied preferences, and navigation. Keep `CLAUDE.md` as a thin import. Remove mandatory
LEARN/memory promotion from root instructions, rules, hooks, and templates. Retire the
current `MEMORY.md` as a source of instructions; preserve intentionally authored guidance
only in the places Leo chooses.

Review every rule and hook for a concrete remaining purpose. Keep raw-data protection.
Remove fake context-percentage reporting and forced skill creation. Propose replacing
parallel plans and checkpoints with issue-rooted change contracts, pending-approval artifacts,
and explicit handoffs. Derive current component progress from the files named by each contract
instead of maintaining a second status record. Retain concise factual session
logs because `sitrep` reads them, but remove the hook that blocks completion to demand an
update. Settle the log-writing trigger before changing recovery hooks. Update stale guides
rather than leaving conflicting copies.

### 3. Build the shared helpers and prove the basic recording behavior

Proposed location: `code/lib/project_io.R`, `code/lib/project_io.py`, and
`code/lib/project_io.jl`. Use one agreed behavior and record format, with ordinary language
readers left intact. Document the interfaces in the modules themselves.

Include input registration for paths written in the script, local modification times recorded
before reading, explicit handling of multi-file inputs, and successful-run reports. For a
multi-file dataset, one helper call expands a fixed directory or file-pattern declaration into
the matched file paths and records their modification times; it must not require a separate
registration call per file, read file contents, hash them, or scan unrelated directories. Scripts
must also write to paths declared in their source code; do not require CLI arguments for input
or output paths. In a pending candidate, output paths point inside that issue's folder. The
spec names the corresponding production paths, and `ship` updates the source paths when it
incorporates the selected files. Records say what was registered, not that every possible read
was detected. Keep network acquisition distinct from local-file modification dates. Do not add
universal IDs, a historical graph, automatic method selection, or unrelated convenience features.

Add the module usage to each language's coding preference skill and `code-review` guidance.
Verify the same examples in all three languages before relying on the helpers. Agree
on how ordinary script launches produce a clear run record without requiring a separate
Make target for every figure.

### 4. Implement pending approval, shipping, and issue closure

For one approved issue contract, create `pending-approval/issue-<number>-<slug>/` with the
candidate code and outputs at fixed paths declared in the scripts. Read approved canonical
inputs without copying them into every candidate. Ensure subsequent candidate scripts use
newly generated candidate data where applicable. The spec also names the production path for
each output. Provide Leo with the code diff, inspectable outputs, and actual verification
results. Then run `code-review` in a separate context against the accepted repository, the
contract, and the candidate; keep its two finding sections separate.

Before implementing `ship`, define how it handles existing-file edits, deletions, changed
base files or inputs, and conflicts. It must never overwrite unrelated work, silently change
a substantive choice, or infer which subset Leo meant. Shipping applies only the named reviewed
components. For those components, it changes the hard-coded paths from the candidate folder to
the production paths already named in the spec, including input references to files produced
by other candidate scripts. Decide whether `ship` reruns the scripts at their production paths
or moves the reviewed outputs there. Keep the candidate run record with the issue. If `ship`
reruns a script, record a new run; if it moves a reviewed output, preserve the original run
record and add its production location. Archive the change contract unchanged after every
component is shipped and the issue closes.
Settle where run records live and how their script and input paths remain understandable after
the candidate files move into their production locations.

Implement `close-issue` after component ownership is reliable. It stages only the issue's
files, checks that the worktree contains no conflicting claims from other open issues, commits,
pushes the current branch, and closes the issue. `ship` never performs these steps.

Use the active harness default (Luna at extra-high effort in Codex or Sonnet at extra effort in
Claude Code) in a separate agent context with bounded file scope and deliberately selected
preferences. Use another model and effort only when Leo explicitly names both. A separate
context alone does not isolate files; the candidate directory and execution setup must enforce
the agreed locations.

### 5. Remove replaced skills, graph infrastructure, and stale callers

Apply the approved disposition table. Remove obsolete Claude skill symlinks alongside
their canonical directories. Update surviving agents and regenerate Codex definitions.
Revise the agent generator and conformance checks for current invocation/model settings.

Retire the graph library, ledger scaffold, graph tests, mandatory provenance hooks, and
Make/CI calls only after the replacement examples pass. Update `.github/workflows/quality.yml`,
README, quick guides, templates, and rule references in the same change. Preserve source
documents and substantive definitions; remove repeated bookkeeping requirements.

Keep specialized review knowledge as selectively read references under `review-paper` or
`review-slides`. Do not make every implementation summon all existing agents. Keep
bibliography and LaTeX checks working before removing their standalone skills. Fix Make's
stage ordering and support Julia entry scripts while updating the runner.

### 6. Exercise the workflow on small examples

Run the tracked workflow in R, Python, and Julia: `open-issue` when Leo wants the work tracked,
settled conversation, `to-spec`, implementation using the active harness default, candidate
code and generated output, independent `code-review`, partial `ship`, final `ship`,
`close-issue`, and archived contract. Make a user-directed refinement to the pending candidate
and confirm it needs no new issue or spec and leaves the original spec unchanged.

Run a post-ship small-edit example with no issue, spec, or candidate folder. Confirm the exact
request goes directly to the working copy, the implementer returns the diff and relevant check,
and nothing is committed or pushed. Run an exploratory session with several plots and diagnostic
regressions in `code/99_explorations/`; confirm it creates no issue/spec and changes no canonical
pipeline or paper output. Then promote one explicitly selected result through a tracked issue
and spec.

Run a no-spec issue example, close it without an empty commit, and verify it appears among the
latest closed issues. Run `sitrep` with components in all three states and three dated session
logs. Run `handoff` and verify that the file is outside the repository and that the response
immediately exposes its exact path.

Use independent agents for behavioral checks, giving each a realistic request and only
the new instructions. Review the observed actions, not self-assigned quality scores.
Run relevant Make/CI and document compilation checks for any retained tooling changed.

## Proposed acceptance checks

- A reply, issue, spec, review, Markdown document, commit message, and code comment each use `unslop`; executable code is unchanged by it.
- `open-issue` creates one short issue for an atomic request when Leo wants work tracked, and creates nothing when it recommends a split until Leo answers. A direct edit or exploration creates no issue by default.
- Every spec names one existing issue; a second spec for the same issue is rejected, while a no-code tracking issue can remain spec-free.
- A regression request with incompatible geographic levels exposes the matching choice before implementation.
- `to-spec` given an unresolved conversation reports the missing decision and does not invent it, interview Leo, or write a ready contract.
- `grill-to-spec` on a difficult numerical-model request asks about applicable choices such as analytic versus numerical integration, quadrature, and the dynamic-programming solution approach. It explains unfamiliar concepts, presents options and tradeoffs, gives an opinionated recommendation, and waits for Leo to decide; only then may it write the issue's one delta spec. An unresolved choice prevents a ready spec, and the skill creates no extra ADR or glossary by default.
- A localized correction produces no new memory entry, skill, or lasting instruction.
- An ordinary request does not activate an explicit-only workflow; approved implementation receives its named coding preferences.
- `implement` defaults to Luna at extra-high effort in Codex and Sonnet at extra effort in Claude Code; an override requires Leo to name both a model and effort. The main conversation remains available while implementation runs.
- A small refinement to an open pending candidate uses the existing issue and spec; code review considers the initial spec and Leo's later explicit instructions, and the spec remains unchanged.
- A small, exact post-ship edit goes directly to the working copy with no issue, spec, or candidate folder; the response includes the diff and relevant check, and the agent does not commit or push unless Leo asks.
- Repeated exploratory plots and diagnostic regressions run under `code/99_explorations/` without issue/spec overhead and do not touch canonical outputs. A result enters the canonical workflow only after Leo selects it.
- A requested lesson teaches; a routine correlation receives no competence check or unnecessary nudge.
- A candidate reads the canonical panel instead of an unmerged duplicate; candidate-built data are used by later candidate steps.
- Scripts declare input and output paths in their source code and run without CLI path arguments. Candidate outputs point into the issue's `pending-approval/` folder; the spec records each production path.
- Input records contain the registered paths and observed modification times; a failed run cannot masquerade as a successful new run.
- One fixed directory or file-pattern declaration registers a multi-file dataset and records each matched file's path and modification time without reading or hashing its contents; hidden reads remain a documented limitation.
- Candidate outputs remain under the issue's `pending-approval/` folder. On `ship`, the named scripts' hard-coded output paths change to the production paths recorded in the spec.
- An ambiguous `ship` request lists the pending subsets and waits for Leo's choice. A partial shipment reports the remaining pending, unwritten, and unclear components without suggesting closure.
- The final shipment suggests `close-issue` but does not commit, push, or close the issue itself.
- `close-issue` refuses incomplete or unclear work, stages only the issue's files, pushes the resulting commit, and closes the issue. A completed no-repository-change issue closes without an empty commit.
- `code-review` reports spec adherence separately from standards/research-correctness findings and makes no edits.
- Changes to accepted code and input changes detectable from the recorded metadata are surfaced before incorporation or re-verification; matching input timestamps do not prove unchanged contents.
- A later substantial tracked change gets its own issue/spec; the earlier archived spec remains byte-for-byte unchanged. A small explicit tweak needs no new spec and is visible in the code diff/history.
- The default or explicitly selected implementer returns its changes and unresolved questions while the parent conversation remains available to Leo.
- `sitrep` derives spec component progress from the candidate and production paths, checks diffs or history when existing files make presence ambiguous, and reports uncertainty rather than guessing. It flags no-spec issues with no repository artifacts as unassessable from files, names the latest three closed issues, and summarizes the latest three dated session logs.
- `handoff` writes outside the repository, references existing artifacts instead of duplicating them, redacts sensitive values, and immediately reports its exact temporary path.
- `make check`, replacement helper/workflow checks, bibliography checks, and relevant LaTeX targets pass; retired commands have no live callers.

## Files expected to change

- `.agents/skills/`, `.claude/skills/`, and selectively read supporting references.
- `AGENTS.md`, `CLAUDE.md`, `README.md`, `MEMORY.md`, `.claude/WORKFLOW_QUICK_REF.md`, and `docs/sources/USER-GUIDE.md`.
- `.claude/rules/`, `.claude/references/`, `.claude/agents/`, generated `.codex/agents/`.
- `.agents/hooks/`, `.claude/settings.json`, `.codex/hooks.json`, `.codex/README.md`.
- `code/lib/` (new), relevant `code/03_quality/` commands/checks, `Makefile`, `.github/workflows/quality.yml`.
- `pending-approval/` (new), change-contract templates, archived specs, session-log routing, and `.gitignore` as required by the agreed storage policy.
- `docs/data/provenance-ledger/` and its callers when replaced; keep source-grounded domain/data information that remains useful.

## Verification of this plan

- [x] Inventory all 27 current skills and identify their proposed destinations.
- [x] Obtain an independent read-only check of capabilities and callers at risk during consolidation.
- [x] Check the finished plan against all user decisions and review for missing implementation dependencies; clarify metadata limits and run-record paths after acceptance.
- [x] Correct the proposed workflow so `to-spec` only records an already agreed conversation; separate code, paper, and slide review; replace `talk` with `write-slides`.
- [x] Add issue tracking for work Leo wants tracked, atomic issue creation, one-spec-per-tracked-issue, direct small edits, issue-free exploration, partial shipping, explicit closure, sitrep, harness-specific implementation defaults, universal `unslop`, and temporary handoffs.
- [x] Derive issue-component progress from spec-listed candidate and production paths; do not add a separate mutable status file. No-spec work without repository artifacts remains unassessable by `sitrep` until Leo closes the issue.
- [x] Write factual session logs at the end of substantial work, without a blocking hook.
- [x] Leo authorized the proposed shortlist and removals by asking for this plan to be implemented.

## Implementation and verification

The replacement skills, language helpers, shared references, raw-data guard, Make and CI
checks, and short navigation guides are in place. The old path-scoped rules, automatic
learning instructions, redundant agents and skills, Asset Graph, and ledger scaffold have
been retired. ADR 0005 records the fixed-path and run-record choices made after this plan.

`make check` passes, including helper examples in R, Python, and Julia on this host.
`make all` runs the empty template pipeline in order and passes its checks. `make articles`
and `make slides` compile the template documents. An independent agent audited the
workflow instructions; its findings about missing/stale output markers, exact reviewed
file identity, deletions, partial-shipment dependencies, and stale guides were fixed.

The live GitHub issue lifecycle was not exercised with disposable issues or commits.
The first real issue should test creation, spec uniqueness, candidate review, a partial
shipment, issue closure, and `sitrep` against actual repository and GitHub state.

## Approval

Leo requested this roadmap and approved the input-helper direction, issue tracking for work
he wants tracked, one-spec-per-tracked-issue lifecycle, issue-free direct edits and exploration,
Luna extra-high implementation in Codex, Sonnet extra
implementation in Claude Code, partial shipping, separate issue closure, sitrep, universal
natural-language `unslop`, and temporary handoffs. Leo's 2026-10-05 instruction to
implement the plan approved the skill shortlist and pruning. He chose moving the
reviewed output on `ship` and writing factual session logs at the end of substantial work.

See the [audit and interview record](2026-09-05_astra-refactor.md) and ADRs 0001–0005 for
the decisions and evidence behind this refactor.
