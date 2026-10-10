---
name: implement
description: Delegate an approved specification, pending-candidate refinement, exact small edit, or exploration and return the changes and relevant checks.
disable-model-invocation: true
---

# Implement

Delegate implementation to the named `implementer` agent in the active harness by default. Keep the main conversation available to Leo. In Codex, that role uses Luna at `xhigh` reasoning effort. In Claude Code, it uses Sonnet at `xhigh` effort. Override that pair only when Leo explicitly names both a model and an effort; apply the pair to this invocation or use a generic agent that can honor it. If the selected pair is unavailable, report that and ask how to proceed; do not substitute silently. Add more implementers only when the specification defines non-overlapping file ownership.

**Input:** one of (1) an issue's completed spec, (2) a specific refinement to its active candidate, (3) an exact post-ship small edit, or (4) an exploratory request.

## Choose the work path

- **Spec implementation:** verify the issue and its one `pending-approval/issue-<number>-<slug>/spec.md`. Read the spec, issue, accepted base, and relevant source files. Work only in the issue's pending-approval folder. Keep the spec unchanged.
- **Candidate refinement:** keep the same issue and spec; apply Leo's explicit refinement inside that candidate. Do not create another issue or spec. The later review will consider both the original spec and Leo's follow-up instructions.
- **Exact small edit:** use Leo's exact request as the brief and edit the working copy directly. Create no issue, spec, or candidate folder. Return the diff and relevant check; do not commit or push. If the request leaves a research or logic choice open, ask Leo before dependent edits. If it materially changes the research design or a durable deliverable, recommend the tracked route and let Leo decide.
- **Exploration:** put scripts under `code/99_explorations/` and outputs in a temporary location. Iterate without an issue, spec, or formal plan. Keep canonical pipeline and paper outputs untouched; promote a result only through a tracked change Leo chooses.

For example, “change the post-ship figure label to ‘Employment’” is a direct edit. “Try three placebo regressions and plot the residuals” is exploration; put the code in `code/99_explorations/` and the trial outputs in a temporary location.

## Prepare the implementer

For a spec change, record the issue folder and accepted base commit, inspect the current worktree for unrelated edits or path conflicts, and give the implementer bounded ownership. Candidate scripts use fixed input and output paths declared in source, without CLI path arguments. Read approved canonical inputs directly; keep newly built candidate data and generated outputs in the issue folder. Follow the spec's component paths and dependencies.

Load only the coding preference and helper material relevant to the languages and files being changed, plus the universal `unslop` standard for text Leo will read. Because the coding skills are user-invoked, read their files and pass the necessary content to the implementer in the task prompt; do not assume a Skill tool or automatic invocation will make that content available. Include the applicable shared helper interface and tell the implementer to register direct local inputs as specified by the project helper. Treat those records as registered paths and observed modification times, not complete read discovery or historical proof.

State the accepted decisions as fixed. The implementer may choose equivalent code details within those decisions and the supplied standards. If implementation reveals a new substantive choice, pause dependent work and return the choice, options, and evidence to Leo.

## Finish

Run the checks named in the spec and other directly relevant checks. For candidate work, keep generated files, outputs, and verification evidence in the issue folder. Do not perform code review, ship files, close the issue, commit, or push as part of implementation. Return changed paths, a concise diff summary, inspectable outputs, checks with actual results, and unresolved decisions. For direct edits and exploration, return the diff and relevant checks without changing canonical results.

**Done:** the selected work path has been implemented within its boundary, relevant checks have actual reported results, and any newly discovered substantive choice is returned to Leo.
