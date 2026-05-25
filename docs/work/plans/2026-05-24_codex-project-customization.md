# Codex Project Customization Cleanup

Status: IN_PROGRESS
Date: 2026-05-24

## Goal

Align the project template with current Codex conventions instead of mirroring Claude Code by guesswork.

## Source of Truth Checked

- OpenAI Codex docs for hooks, custom agents/subagents, skills, and `AGENTS.md`.
- Local Codex CLI/Desktop behavior:
  - Project custom agents appear from `.codex/agents/*.toml`.
  - Project skills appear from `.agents/skills/*/SKILL.md`.

## Decisions

- Keep `.codex/agents/*.toml`; this is the Codex project-scoped custom agent location.
- Keep `.codex/hooks.json` plus scripts in `.codex/hooks/`; this is a valid project-local hook source once the project `.codex/` layer is trusted.
- Keep Codex project skills in `.agents/skills/`; do not create `.codex/skills/`.
- Keep shared rules/references in `.claude/rules/` and `.claude/references/`, but route Codex to them explicitly from `AGENTS.md`.
- Replace hardcoded hook paths with git-root-resolved commands.
- Replace Claude-only hook assumptions:
  - No Codex `Notification` event.
  - Use Codex `PermissionRequest` for approval/attention notifications.
  - Use `apply_patch`/`Edit`/`Write` matchers for Codex file edits.

## Tasks

- [x] Patch `.codex/hooks.json` to use Codex events and portable commands.
- [x] Adapt `.codex/hooks/*` scripts from Claude env/state paths to Codex hook input and `CODEX_HOME`.
- [x] Update `AGENTS.md`, `README.md`, and `docs/sources/USER-GUIDE.md` with Codex-native layout.
- [x] Update Codex skill docs that still point at Claude session state.
- [x] Validate JSON/TOML/Python/shell path hygiene.
