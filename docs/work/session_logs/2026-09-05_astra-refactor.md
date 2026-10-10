# Session Log: 2026-09-05 — Astra template refactor

**Status:** IN PROGRESS

## Objective

Audit the research template and interview Leo about simplifying it while preserving
research quality, reproducibility, and useful continuity across sessions.

## Changes Made

- Created `astra-refactor` from `main` at `dbe8d61`; preserved the user's uncommitted opt-in provenance-skill instructions in `AGENTS.md`.
- Saved the audit/interview plan and began the glossary with the template/project distinction supplied by Leo.

## Design Decisions

Accepted: Leo owns all research and logic decisions; agents advise, teach, and
implement his choices. Recorded in ADR 0001. Future greenfield projects are the
target; existing-project migration is deferred. Implementation mechanics remain open.

Round 2 settled that specs are change contracts archived unchanged after acceptance;
scripts explain their own current behavior; downstream analysis uses approved canonical
datasets; code and outputs are reviewed together; teaching is explicitly requested;
and task experience is never automatically promoted into lasting instructions.

## Incremental Work Log

- Initial request authorizes branch creation, inspection, and an interview with recommendations.
- Repository inspection found existing consolidation alongside stale memory, overlapping skills, and heuristic context reporting.
- Located missing `grilling` and `domain-modeling` dependencies in Matt Pocock's public repository; applied the source instructions directly without installing skills.
- Delegated a read-only traceability fact check as required by the grilling workflow while inspecting context recovery locally.
- Independent review confirmed declared lineage and hash/history checks, but no enforced execution-to-output binding. Retiring historical identities would be a real capability tradeoff.
- Recorded the distinction between structural conformance and empirical reproduction; retained all proposed changes as interview topics.
- Round 1: Leo rejected autonomous logic decisions and described failures involving generalized memory, unwanted skill invocation, premature implementation, scattered data, and undisclosed spatial matching.
- Recorded the mentat definition and decision-ownership ADR immediately. Updated language/tool requirements and deferred migration.
- Began checking the unslop reference and delegation mechanics; specification/review layouts remain proposals.
- Found the hook and /learn prompts that encourage agent-selected promotion into persistent project skills. Proposed explicit approval and scope for durable rules.
- Read-only lookup found no Fisher skill in the permitted repository/user/plugin locations. No removal attempted.
- Confirmed Codex supports per-agent models; the existing generator's contrary assumption is stale. Proposed Luna implementation with bounded context and explicit worktree isolation.
- Prepared proposals for change-level specifications, code acceptance, teaching checkpoints, and simpler traceability. No workflow implementation selected or dispatched.
- Round 2: Leo clarified that archived specs are immutable records of changes, not living script documentation. Recorded ADR 0002 and the change-contract glossary entry.
- Leo approved coding discretion that preserves settled meaning/behavior, clarified canonical dataset use, and required a folder containing candidate scripts and their outputs for review.
- Leo rejected competence gates and proactive teaching. He also rejected automatic preservation of preferences entirely; lasting instructions require deliberate joint authorship and routing.
- Leo identified the traceability proposal's abstract wording as the exact writing failure to address. Preparing a named-file example instead; no traceability implementation selected.
- Round 3: Leo selected `pending-approval`, accepted run-time output destinations that preserve reviewed code, and agreed to reading existing canonical inputs while keeping candidate outputs together. Recorded ADR 0003.
- Leo limited understanding nudges to methods he reasonably might not understand; routine correlations need no nudge. Updated ADR 0001.
- Leo accepted simple figure/run records subject to explaining input discovery and requested input modification dates. Preparing a small input-registration proposal with explicit limits; no helper implemented.
- Independent fact check confirmed that explicit input registration is not automatic detection or proof of successful reads, and that multi-file datasets need component handling. R supplies filesystem modification dates directly; no content scan is needed for that field.
- Leo approved shared input-file helpers and requested their inclusion in R, Python, Julia, and future language coding preferences. Recorded ADR 0004.
- Leo requested a concrete refactor plan, starting with the skill set and removal of unused skills. Preparing a proposed disposition for all 27 current skills; actual usage is not inferred from the inventory.
- Independent review identified capabilities to retain during consolidation: external-paper review, narrow proofreading, literature synthesis, appendices in bibliography checks, and selectable review modes. Bibliography validation currently has no Make target, so a replacement must precede retiring that skill.
- Saved the proposed implementation roadmap with a disposition for all 27 existing skills, staged file changes, and behavioral acceptance checks. Shortlist and deletions remain proposals.
- Closed the initial audit/interview record and linked it to the roadmap. Existing instructions, skills, code, and data remain unchanged by the planning work.
- Independent roadmap review confirmed all 27 skills are accounted for and the agreed decisions are preserved. Clarified that metadata cannot detect every input change and that run-record paths must remain interpretable after acceptance.
- Leo corrected the skill boundaries: `to-spec` only turns an already agreed conversation into a delta-based handoff; research design and referee-response planning stay outside it. The workflow now passes that spec directly to `implement`, with no ticket-conversion step.
- Read `writing-for-agents` and its mechanics reference as required for every skill we draft. Compared the referenced AI Hero `to-spec`, `implement`, and `code-review` workflows and adapted their separation of responsibilities to the pending-approval design.
- Replaced the proposed general review entry point with separate `code-review`, `paper-review`, and `review-slides` skills. Replaced `talk` with `write-slides`, which points to `.claude/rules/slide-writing-principles.md`.
- Audited all 22 path-scoped rule files and 12 shared hook scripts. Most rules contain reusable standards but deliver them too broadly; most hooks inject reminders or enforce the outgoing planning, logging, and provenance systems.
- Added a proposed four-layer replacement to the roadmap: a very small `AGENTS.md`, explicitly invoked skills with selectively read references, executable Make/CI checks, and one narrow raw-data protection hook. Desktop notification remains optional.
- Recommended removing the context estimate, forced session log, PDF guard, plan naming, compaction recovery, provenance reminder, rule injector, and verification reminder hooks. Recommended moving retained rule content to the skill that needs it rather than auto-loading `.claude/rules/`.

## Verification Results

- `git branch --show-current`: `astra-refactor`.
- Baseline `make check`: PASS. This establishes structural conformance only.
- Roadmap verification: `make check` and document whitespace/link checks PASS; independent review completed and its two clarifications incorporated.
- Independent reviewer: `make provenance` PASS; `make asset-graph-test` PASS (24 tests); `make fetch build analysis` completed with no scripts at the empty scaffold baseline.
- No paper, analysis, raw data, generated results, or executable infrastructure changed.
- Quality score: N/A for an ongoing requirements interview; no research-quality score inferred from lint checks.

## Open Questions / Next Steps

Review the proposed implementation roadmap with Leo, settle the skill shortlist,
then write the first bounded change contract. The shared input-helper direction is
approved; specific removals, acceptance semantics, teaching style, and task recovery
details remain to be settled while authoring the relevant skills.

## Provenance Ledger

N/A: no governed asset or graph record changed.


---
**Context compaction (auto) at 15:49**
Check git status/log and docs/work/plans/ for current state.


---
**Context compaction (auto) at 18:16**
Check git status/log and docs/work/plans/ for current state.


---
**Context compaction (auto) at 18:51**
Check git status/log and docs/work/plans/ for current state.
