# Codex and Claude Code setup

Both apps read `AGENTS.md`. Claude Code imports it through `CLAUDE.md`. Canonical
skill files live in `.agents/skills/`; `.claude/skills/` contains symlinks to
them. The named `implementer` and `code-reviewer` agents live in
`.claude/agents/`, and `make agents` generates the corresponding Codex TOML
files. `make check` checks that these shared entry points stay aligned.

The only project hook in either app is the shared pre-tool guard for existing
files under `data/raw/`. It protects against direct agent file edits and
ordinary commands that name those files; it is not a filesystem sandbox for
scripts. Task procedures belong to skills, and checks belong to Make or the
specific script.

When routing `/implement`, use Luna at `xhigh` effort in Codex or Sonnet at
`xhigh` effort in Claude Code. Override both settings only when Leo supplies a
different model and effort. Pass the relevant language preference file and
issue spec to the implementer explicitly. The main conversation remains
available while the agent works.
