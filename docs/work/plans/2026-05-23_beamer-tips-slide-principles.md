# Plan: Adopt Beamer Tips As Slide-Writing Principles

## Source

- Paul Goldsmith-Pinkham, `beamer-tips/slides.tex`: https://github.com/paulgp/beamer-tips/blob/master/slides.tex

## Principles To Codify

- Keep slides simple: one main point, generous spacing, 45-75 characters per line, and no font shrinking to rescue overcrowded frames.
- Prefer 16:9 Beamer decks with clear section transitions, sparse roadmaps, and visual rhythm.
- Use two or three color-blind-conscious accent colors consistently; avoid red/blue-only contrasts.
- Make figures central when possible, with graph labels large enough for a seminar room.
- Translate dense paper tables into talk-appropriate tables, highlights, or takeaways.
- Use overlays or builds sparingly and only when they clarify a same-axis figure/table reveal; do not use casual `\pause`.
- Move dense proofs, robustness, and full tables to backup slides with links.
- Use speaker notes for delivery detail rather than putting script text on slides.

## Files To Update

- Add shared rule: `.claude/rules/slide-writing-principles.md`
- Add shared Beamer defaults: `docs/deliverables/preambles/beamer-preamble.tex`
- Update top-level docs: `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/sources/USER-GUIDE.md`, `.claude/WORKFLOW_QUICK_REF.md`
- Update style references: `.claude/references/personal-style-guide.md`
- Update Beamer/content rules: `.claude/rules/beamer-integrity.md`, `.claude/rules/content-invariants.md`, `.claude/rules/content-standards.md`, `.claude/rules/no-pause-beamer.md`, `.claude/rules/tikz-visual-quality.md`, `.claude/rules/verification-protocol.md`
- Update skills in both `.agents/skills/` and `.claude/skills/`: `talk`, `slide-excellence`, `visual-audit`, `pedagogy-review`, `devils-advocate`, `review`, `proofread`
- Update slide-facing agents in `.claude/agents/` and `.codex/agents/`: `storyteller`, `storyteller-critic`, `slide-auditor`, `pedagogy-reviewer`, `tikz-reviewer`, `orchestrator`

## Verification

- Search for stale no-overlay/no-pause wording.
- Search for all references to the new rule and preamble.
- Check `git diff` for scope and syntax-sensitive TOML/Markdown edits.
