# Codex Project Customization

This directory contains Codex project-scoped customization that is safe to ship with the template:

- `agents/*.toml`: custom subagent roles for Codex.
- `hooks.json`: project hook wiring loaded from the project `.codex` layer after Codex trust review, including Provenance Ledger reminders and append-only `data/raw/` protection.
- `hooks/`: hook scripts called by `hooks.json`.

Codex repo skills do not live here. Put project skills in `.agents/skills/*/SKILL.md`.

Do not add local auth, access tokens, or personal runtime config here. User/global Codex config belongs in `~/.codex/`; repo-specific `config.toml` should be committed only when it contains portable, non-secret project defaults.
