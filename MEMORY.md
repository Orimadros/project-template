# Project Memory

Corrections and learned facts that persist across sessions.
When a mistake is corrected, append a `[LEARN:category]` entry below so future
sessions don't repeat it. Keep entries transferable (conventions, pitfalls,
design decisions) — not ephemeral task state, which belongs in session logs.

Format: `[LEARN:category] wrong -> right` (one line; add the *why* if non-obvious).

---

<!-- Append new entries below. Most recent at bottom. -->
[LEARN:workflow] Slide-first source of truth -> paper-first source of truth at docs/deliverables/articles/main.tex; Beamer slides derive from the paper.
[LEARN:workflow] Editing only .claude/skills -> mirror every skill edit into the byte-identical .agents/skills (Codex) copy so the two harness trees stay in sync; likewise mirror .claude/agents/*.md <-> .codex/agents/*.toml (content-equivalent, with `\\` backslash escaping in TOML).
