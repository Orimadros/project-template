# Session Log: 2026-05-25 -- Add \smallcitation Beamer command + propagate guidance

**Status:** COMPLETED

## Objective
Add a `\smallcitation{}` command to the shared Beamer preamble that renders citations small and muted grey, intended for trailing parenthetical references at the end of a bullet (so the claim leads and the citation recedes). Propagate the convention to the slide-writing guidance, skills, and agents.

## Changes Made

| File | Change | Reason | Quality Score |
|------|--------|--------|---|
| `docs/deliverables/preambles/beamer-preamble.tex` | Added `\newcommand{\smallcitation}[1]{{\footnotesize\color{slidemuted}#1}}` with a usage comment | The command itself | 92/100 |
| `.claude/rules/slide-writing-principles.md` | Added a "Citations" section + an audit question | Single source of truth for slide writing | 92/100 |
| `.claude/skills/talk/SKILL.md` + `.agents/skills/talk/SKILL.md` | Slide Standard bullet on `\smallcitation` | Skill that drafts decks (+ Codex mirror) | 90/100 |
| `.claude/agents/storyteller.md` + `.codex/agents/storyteller.toml` | Slide Standard bullet | Worker that drafts decks (+ Codex mirror) | 90/100 |
| `.claude/agents/slide-auditor.md` + `.codex/agents/slide-auditor.toml` | Audit checklist item | Visual auditor (+ Codex mirror) | 90/100 |
| `.claude/skills/visual-audit/SKILL.md` + `.agents/skills/visual-audit/SKILL.md` | Audit checklist item | Visual-audit skill (+ Codex mirror) | 90/100 |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Command styles its argument only (no auto-parens) | Auto-wrap argument in parentheses | Composes with `\citep{...}` and natbib without producing double parens |
| Reused existing `slidemuted` (RGB 95,99,104) + `\footnotesize` | New grey color; `\small` | Matches the preamble's existing muted-grey convention; `\footnotesize` gives stronger de-emphasis |
| Did not edit `slide-excellence` skill | Add macro mention there too | It orchestrates reviewers and reads the rule/preamble dynamically; it does not enumerate macros |

## Incremental Work Log

- Added the command to the preamble and a "Citations" section to the single-source-of-truth rule.
- Propagated to the two slide skills (both Claude + Codex `.agents` mirrors) and the storyteller/slide-auditor agents (Claude `.md` + Codex `.toml`).
- User reminder: every `.claude/skills` skill has a Codex equivalent in `.agents/skills`; mirror edits there too. Confirmed both touched skills were already mirrored and in sync.

## Learnings & Corrections

- [LEARN:workflow] Mirror every `.claude/skills` edit into `.agents/skills` (byte-identical Codex copy); also mirror `.claude/agents/*.md` <-> `.codex/agents/*.toml`. Recorded in `MEMORY.md`.

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| Throwaway deck inputting the preamble compiled with XeLaTeX (use + skip cases) | exit 0, PDF produced, no errors / undefined control sequences / overfull boxes | PASS |
| Test artifacts removed | No stray files in `git status` | PASS |
| `.agents/skills` mirrors in sync with `.claude/skills` | `diff` identical for talk + visual-audit | PASS |

## Open Questions / Blockers

- None.

## Next Steps

- [ ] None required. The macro is unused until a deck adopts it; no migration of existing decks needed (slides scaffold is empty).


---
**Codex context compaction (manual) at 14:46**
Check git status and docs/work/plans/ for current state.

---
**Session update at 2026-05-25**

## Recent Progress

- Audited Codex project customization against the real Codex conventions and committed the portable project setup:
  - Codex instructions remain in `AGENTS.md`.
  - Codex project agents live in `.codex/agents/*.toml`.
  - Codex hooks live in `.codex/hooks.json` plus `.codex/hooks/`, with portable git-root script resolution.
  - Codex repo skills live in `.agents/skills/*/SKILL.md`; `.codex/skills/` is intentionally not used.
- Reworked the LaTeX deliverable layout so root article and slide documents live one per folder, with the canonical article now at `docs/deliverables/articles/main/main.tex`.
- Added Makefile support for `make articles`, `make slides`, and `make latex`, compiling root `.tex` documents under article/slide folders.
- Added and refined the shared Beamer preamble:
  - `\smallcitation{...}` for muted trailing references.
  - `\sectiontransition[optional subtitle]{Title}` for quiet transition slides.
  - `siunitx` support plus slide-table column helpers.
- Created slide-writing source reports from the 8 resources in `docs/sources/slide-writing/SLIDE-REFERENCES.md`.
- Created `docs/sources/slide-writing/FINAL-SUGGESTIONS.md` and incorporated the approved recommendations into the framework.
- Refactored `.claude/rules/slide-writing-principles.md` as the central rule for:
  - Big 5 / first-five-minutes opening.
  - substantive frame titles.
  - intuition bridge before technical density.
  - empirical credibility and threat framing.
  - data-graphics integrity.
  - table legibility and `siunitx`.
  - non-hue accessibility.
  - final belief-change takeaway.
  - delivery robustness.
- Propagated the updated slide standard through mirrored Claude/Codex skills and agents, including `talk`, `slide-excellence`, `visual-audit`, `pedagogy-review`, `devils-advocate`, `storyteller`, `storyteller-critic`, `slide-auditor`, `pedagogy-reviewer`, `proofreader`, `verifier`, `tikz-reviewer`, and `orchestrator`.
- Updated user-facing docs (`AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/sources/USER-GUIDE.md`) so users know to provide audience, duration, talk type/status, and goal for Beamer requests.

## Decisions

- The central slide-writing source of truth is `.claude/rules/slide-writing-principles.md`; agents and skills should read that rule rather than `FINAL-SUGGESTIONS.md` during normal work.
- `FINAL-SUGGESTIONS.md` remains as provenance for the source-backed synthesis.
- Big 5 is a standard for opening clarity, not a requirement for exactly five separate slides.
- Talk-length budgeting is an upper-bound/planning heuristic, not a rigid one-slide-per-minute rule.
- Beamer links and backup navigation are allowed, but the main talk should not depend on mouse access or live interaction.
- `.codex/config.toml` remains untracked/out of the template; committed `.codex/` content contains agents, hooks, and docs only.

## Verification Status

- `git diff --check`: PASS.
- Codex agent TOML parse over 24 `.codex/agents/*.toml`: PASS.
- `.codex/hooks.json` JSON parse: PASS.
- Hook Python compile and shell syntax checks: PASS.
- `make articles`: PASS.
- `make slides`: PASS, with no root slide decks currently present.
- `make latex`: PASS.
- Temporary Beamer smoke deck using `siunitx`, `\smallcitation`, and `\sectiontransition`: PASS.
- Mirrored updated `.agents/skills/*` and `.claude/skills/*` skill pairs: PASS for the edited pairs.

## Git Status

- Created branch `codex/slide-framework-template-updates`.
- Committed as `32044c5 Update Codex template and Beamer slide framework`.
- Pushed branch to `origin/codex/slide-framework-template-updates`.
- GitHub PR URL offered by remote: `https://github.com/Orimadros/project-template/pull/new/codex/slide-framework-template-updates`.
