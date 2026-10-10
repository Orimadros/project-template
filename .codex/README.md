# Codex Project Customization

This directory contains Codex project-scoped customization that is safe to ship with the template:

- `agents/*.toml`: custom subagent roles for Codex.
- `hooks.json`: one pre-tool guard for direct changes to existing `data/raw/` files, loaded after Codex trusts this project layer. The shared script lives at `.agents/hooks/guard_raw_data.py`.

Codex repo skills do not live here. Put project skills in `.agents/skills/*/SKILL.md`.

Do not add local auth, access tokens, or personal runtime config here. User/global Codex config belongs in `~/.codex/`; repo-specific `config.toml` should be committed only when it contains portable, non-secret project defaults.
