@AGENTS.md

## Claude Code specifics

- `.claude/rules/*.md` auto-loads in Claude Code sessions: files with `paths:` frontmatter load when you touch a matching file; the rest load every session. Codex has no equivalent, so it gets the same content via a PostToolUse rule-injector hook plus the Rules Index in `AGENTS.md` as a fallback -- see that section for details.
- `.claude/skills/` and `.claude/agents/` are what Claude Code actually reads. `.claude/skills/<name>` is a symlink into the canonical `.agents/skills/<name>`; `.codex/agents/*.toml` is generated from `.claude/agents/*.md` via `make agents`.
