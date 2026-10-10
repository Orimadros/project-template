# Astra template refactor: audit and design interview

**Date:** 2026-09-05
**Status:** COMPLETED — initial audit and design interview

The proposed next steps are in [the implementation roadmap](2026-09-05_astra-refactor-implementation.md).
This record preserves the initial audit and the decisions reached before that roadmap.

## Objective

Agree with Leo on a simpler research template that improves agent productivity,
research quality, and reproducibility across new and existing projects.

## Clarity Status

| Aspect | Status | Notes |
|---|---|---|
| Branch and initial audit | CLEAR | User requested `astra-refactor`, repository inspection, and an interview with suggestions. |
| Interview method | CLEAR | Apply `grill-with-docs`: question rounds, glossary as terms settle, sparse ADRs. |
| Target architecture | CLEAR | Core direction settled through the interview; the implementation roadmap proposes the skill shortlist and remaining mechanics. |
| Existing projects | CLEAR | Migration is deferred. Optimize for future greenfield projects. |
| Decision ownership | CLEAR | Leo owns substantive choices. Agents translate them into code under prewritten standards with discretion that changes neither meaning nor behavior. |
| Traceability | CLEAR | Register direct inputs and modification times through shared helpers; rely on coding standards and review for coverage. No exhaustive historical reconstruction. |
| Supported tools | CLEAR | Claude Code and Codex; R for data/spatial work and most regressions, Julia for some regressions, Python for scraping and model solving. |

## Requirements

### MUST

- [x] Create `astra-refactor`, preserving the pre-existing uncommitted `AGENTS.md` changes.
- [x] Inspect instructions, skills, agents, hooks, Make, context recovery, and provenance infrastructure.
- [x] Resolve the core design with Leo, separating observed facts, proposals, and accepted decisions; carry detailed skill/mechanism choices into the requested roadmap.
- [x] Record settled vocabulary and consequential decisions as they arise.
- [x] Propose observable acceptance checks in the implementation roadmap; final agreement precedes each implementation contract.

### SHOULD

- [ ] Reduce duplicate instructions and manual records reconstructible from executable sources.
- [ ] Preserve research rationale, source-grounded variable meanings, and output traceability.
- [ ] Keep the template easy to maintain; defer migration of existing projects.

### MAY

- [ ] Compare old and proposed workflows on representative research tasks once those tasks are selected.

## Approach

1. Establish the branch and inspect the current architecture and linked primary guidance.
2. Ask independent questions in rounds, with recommendations and concrete research scenarios.
3. Update this plan as answers resolve prerequisites. Put only agreed terminology in `CONTEXT.md`.
4. Record an ADR only for a consequential, non-obvious choice involving a real tradeoff.
5. Once shared understanding is confirmed, specify and execute bounded refactor slices with appropriate checks and independent review.

## Initial observations (2026-09-05 snapshot)

- Root `AGENTS.md`: 198 lines / approximately 1,900 whitespace-delimited words.
  Repository: 27 skill definitions, 22 rule files, 24 source agent definitions,
  and 12 shared hook scripts. These are inventory counts, not token usage or proof of poor performance.
- Existing consolidation is valuable: `CLAUDE.md` imports `AGENTS.md`, Claude skills
  link to `.agents/skills/`, hooks live in `.agents/hooks/`, and Codex agent definitions are generated.
- `MEMORY.md` retains an obsolete paper path and a superseded instruction to mirror skill copies.
  `AGENTS.md` and `.codex/README.md` still describe hook directories that no longer exist.
- Make discovers numbered scripts and runs stages; it contains no project-specific output prerequisites
  at this empty template baseline. The separately authored graph declares dependency relationships.
- `.agents/hooks/context-monitor.py` computes its percentage as tool calls divided by 150;
  this is not measured context occupancy. Context recovery chooses plans/logs using modification times.
- `analyze` and `data-analysis` have substantially overlapping entry conditions and deliverables.
- The exploration fast track removes planning but still requires file identity and graph maintenance.
- `quality_score.py` labels itself a heuristic blocker check; its numeric result does not establish
  substantive paper quality. The separate weighted rubric also needs judgment.
- `make check` passes. It checks structural conformance, not the truth of all documentation or runtime hook delivery.

Independent traceability review confirmed that the graph checks reviewed hashes,
declared producer contracts, and recoverable historical Git blobs, but does not
require evidence binding output bytes to an observed successful execution
(`code/03_quality/asset_graph_lib/validation.py:479`, `:731`, `:1247`;
`docs/data/provenance-ledger/templates/activity.toml:17`). Its `rebuildability()`
classification detects structural blockers in the declared graph; it is not a rerun test.
Removing UUID/history records would lose explicit identity and path-reuse distinctions;
Git alone cannot replace those guarantees for ignored/generated files.

The reviewer also found that `all` lists stages as sibling Make prerequisites,
so the advertised ordering is not enforced under parallel Make. This is a future
implementation concern, not a reason to choose a pipeline engine before the interview.

## Interview design tree

### Settled in round 1

- Leo owns all research and logic decisions; agents are mentats and implementers.
  See `docs/adr/0001-human-ownership-of-research-decisions.md`.
- Both Claude Code and Codex must be supported, with the language division above.
- The immediate target is future greenfield projects; existing-project migration is deferred.
- Traceability should balance simplicity and usefulness, without exhaustive pipeline snapshots for every historical asset.
- Local instructions must not become general memory or skills without deliberate scope control.
- Conversational writing should consistently follow a style guide inspired by the supplied unslop skill.
- Leo wants teaching to keep understanding ahead of implementation and visibility into choices hidden inside broad requests.

### Concrete failure cases supplied by Leo

- A localized correction is promoted through LEARN/memory and incorrectly applied elsewhere.
- An unwanted skill such as `fisher-modelling` is invoked without being requested.
- A numerical solver is implemented before Leo understands quadrature and the method choice.
- A regression silently aggregates or spatially matches variables measured at different levels.
- Related data become scattered, forcing repeated rediscovery and confusing downstream analysis.

### Settled in round 2

- Agents have full discretion in expressing approved substantive choices as code under prewritten
  standards, provided meaning and behavior are preserved. ADR 0001 now includes that boundary.
- Specifications describe changes, never current repository state. One contract may cover several
  scripts. Archive it unchanged after acceptance; write a new contract for later changes. See ADR 0002.
- The script itself must explain current behavior and the reasons for its substantive choices.
  No separately maintained manual is required for each script.
- Assemble relevant data at the same agreed observation level into canonical datasets. Later
  analyses read those datasets, including when they need only one series, rather than bypassing
  them for unmerged intermediate sources. Dataset choices and combinations remain Leo's decisions.
- Candidate scripts and their outputs must be inspectable together before acceptance.
  Round 3 settled the folder name and output destination mechanism below.
- Teaching is user-invoked only. Agents nudge Leo to consider his understanding, but never proactively
  teach or refuse execution because he has not demonstrated understanding.
- Agents never promote task experience into lasting preferences, memory, or skills. Durable instructions
  are deliberately authored with Leo, including an explicit agreement about when agents receive them.
- Leo rejected the abstract wording of the traceability proposal because it did not show concrete
  files or actions. The future conversation-style skill should use that supplied failure example.
  Keep this example in the refactor's working notes until the style document is deliberately authored.

### Settled in round 3

- Name the candidate folder `pending-approval/`. Its per-change folder contains the spec, scripts,
  outputs, and verification results together. See ADR 0003.
- Supply output destinations when scripts run, so acceptance does not rewrite reviewed code.
- Read existing inputs from approved canonical datasets. Newly produced candidate datasets stay
  in the pending folder and are the inputs for later scripts in the same candidate change.
- Offer understanding nudges at spec approval or newly discovered substantive choices only when
  Leo reasonably might not understand the method. Routine correlation calculations need no nudge.
- Leo accepts the simpler figure/script/run-record direction, conditional on a clear explanation
  of how inputs are identified, and requests each input's last-modified date in the saved record.

### Input-recording mechanism agreed after round 3

The current Makefile does not observe file reads. A list declared to a runner cannot prove that
the script uses no other files. Leo approved a small `input_file(path)` helper used where a script
reads a data or configuration file; it records the resolved file path and filesystem modification
time immediately before returning that path to the normal reader. It is agreed, not implemented.
Provide matching R, Python, and Julia modules and supply their use through the corresponding
coding preference skills. See ADR 0004.

Example: `panel <- readRDS(input_file("data/clean/municipality_year.rds"))`.
The ordinary reader still loads the file. A loop would register each filename actually passed
to it. Multi-file datasets require their component files to be registered together. Network
requests need separate source/download treatment, not invented local modification times.

This records direct inputs that the script registers. It does not automatically discover hidden
reads inside third-party code or reconstruct all upstream raw inputs used to build a panel.
Completeness depends on coding standards and review unless stronger tracing is deliberately added.
Filesystem modification times are useful run metadata, not proof of file contents or provider
release dates. Leo accepted this scope and the use of coding standards and review for coverage.

Independent read-only review confirmed these limits: the proposed helper records registration,
not an observed successful read; ordinary readers may open additional files internally; matching
modification times do not prove matching contents. Label records accordingly. R's `file.info()`
already exposes `mtime`, so recording the requested local timestamps requires no file-content scan.

### Further audit evidence

- Memory promotion is encouraged by `AGENTS.md`, `MEMORY.md`, `/learn`, and the context hook.
- `fisher-modelling` was not found in this repository, user skill directories, or installed Codex plugin
  skill directories. Claude's user skill/plugin-cache directories are absent. Nothing was removed.
- The conformance checker rejects `disable-model-invocation`; the agent generator assumes Codex lacks
  per-agent models. Those assumptions conflict with current host features relevant to the proposed workflow.

### Remaining design questions

- Pending-folder details: handle modifications to existing files, input lookup between accepted and
  candidate files, and changes to accepted files or inputs while a candidate awaits approval.
- Traceability: implement the agreed direct-input helper and record format under a bounded contract.
- Conversation style and skill invocation: choose deliberately which instructions are always read,
  which workflows are explicitly requested, and which coding references an implementer receives.
- Teaching: define the requested skill's teaching style; timing and scope of brief nudges are settled.
- Instruction placement; data navigation; parent/implementer model choices; acceptance semantics;
  task recovery; paper/design/evidence authority; behavioral checks; implementation sequence.

The proposed smaller-model implementer remains a proposal. Luna is available in this session;
no implementation has been dispatched. Migration of existing projects remains out of scope.

## Sources and interpretation

- [Writing for agents](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md): separate always-loaded pointers from selectively read guidance; prune duplicate and recoverable information.
- [Skill mechanics](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL-MECHANICS.md): distinguish human and model invocation; verify mechanics separately for each host.
- [Official Codex skills documentation](https://learn.chatgpt.com/docs/build-skills): metadata-first loading and Codex invocation policy in `agents/openai.yaml`.
- [Official AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md): instruction discovery depends on directory scope.
- [Unslop reference](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md): requested inspiration for conversational style; its invocation declaration needs adaptation for an always-read rule.
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [Claude Code subagents](https://code.claude.com/docs/en/sub-agents): separate context and model configuration are available; shared-file versus worktree isolation needs deliberate setup.
- [Claude Code skills](https://code.claude.com/docs/en/skills): explicit-only invocation differs from Codex policy configuration.
- [R file information](https://stat.ethz.ch/R-manual/R-devel/library/base/html/file.info.html): local file modification times are available as `mtime`.
- [Grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) and [domain modeling](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md): recovered from upstream because the installed router lacks these local dependencies; read directly, without installing them.
- The supplied video summary is user-provided context; YouTube retrieval was throttled.
  Treat the quoted 150–200-instruction claim as a heuristic, not an established model-independent limit.

## Files Expected To Change

During the interview: this plan, its session log, `CONTEXT.md`, and selective ADRs if warranted.
Implementation files will be named after scope decisions settle.

## Verification

- [x] Confirm the requested branch and preserve the user's existing diff.
- [x] Baseline `make check` passes.
- [x] Independent read-only review: `make provenance` passes; all 24 Asset Graph tests pass;
  fetch/build/analysis targets complete with no scripts, as expected for the empty scaffold.
- [ ] Recheck document references and whitespace after interview updates.
- [ ] Define behavioral checks from Leo's actual failure cases before selecting the final design.

## Provenance Ledger Impact

N/A: audit and work documents are outside graph coverage; no governed assets are changed.

## Approval

The user authorized branch creation, audit, and the design interview on 2026-09-05,
then confirmed readiness to develop a concrete plan. The new roadmap carries the
remaining proposals; implementation has not been approved by completing this audit.
