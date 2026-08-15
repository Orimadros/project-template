# Cross-Agent Configuration Guide: Claude Code + Codex

**What this is:** how to build one project template that both Claude Code and Codex actually respect — what each harness loads, what can be shared, what must be duplicated, and which mechanisms are enforcement versus suggestion.

_Researched against official docs, August 2026. Every claim is sourced; uncertain items are flagged._

---

## 1. The Central Principle: Three Tiers of Bindingness

Most cross-agent frustration comes from expecting Tier 1 to behave like Tier 2.

| Tier | Mechanism | Binding? | Claude Code | Codex |
|------|-----------|----------|-------------|-------|
| **1. Context** | Instruction files, rules, skills | **No** — a strong suggestion the model may not follow | `CLAUDE.md`, `.claude/rules/`, `.claude/skills/` | `AGENTS.md`, `.agents/skills/` |
| **2. Hooks** | Shell scripts at lifecycle events | **Yes** — runs regardless of what the model decides | `.claude/settings.json` → `hooks` | `.codex/hooks.json` |
| **3. Permissions** | Allow/deny config | **Yes** — hard client-side enforcement | `settings.json` → `permissions` | `config.toml` |

Claude Code's own documentation is explicit about this:

> "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead."
> — [Claude Code memory docs](https://code.claude.com/docs/en/memory)

And again, on why instructions get ignored:

> "If the instruction is something that must run at a specific point, such as before every commit or after each file edit, write it as a hook instead. Hooks execute as shell commands at fixed lifecycle events and apply regardless of what Claude decides."

**The operating rule:** if you would be annoyed when it doesn't happen, it is a hook. If it is guidance the agent should weigh, it is context. Writing "always do X" in an instruction file and expecting determinism is the single most common design error.

---

## 2. Feature Compatibility Matrix

| Capability | Claude Code | Codex | Shareable? |
|---|---|---|---|
| **Project instructions** | `CLAUDE.md` or `.claude/CLAUDE.md` | `AGENTS.md` (+ nested dirs, `AGENTS.override.md`) | **Yes** — `@AGENTS.md` import or symlink |
| **Modular rules** | `.claude/rules/*.md`, optional `paths:` frontmatter | *(none — no equivalent)* | **No** — Claude-only auto-load |
| **Skills** | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | **Yes** — via symlink |
| **Subagents** | `.claude/agents/*.md` (markdown + YAML frontmatter) | `.codex/agents/*.toml` (TOML) | **No** — different formats |
| **Hook wiring** | `.claude/settings.json` → `hooks` | `.codex/hooks.json` or `.codex/config.toml` | **No** — but both point at the same scripts |
| **Hook scripts** | Any executable; JSON on stdin | Any executable; JSON on stdin | **Yes** — one script, both harnesses |
| **Settings** | `.claude/settings.json` | `.codex/config.toml` | **No** |
| **Plan files** | `plansDirectory`, harness-generated random names | Agent writes the file itself | **Asymmetric** — see §6 |

### Instruction files

Claude Code reads `CLAUDE.md`, **not** `AGENTS.md`. The documented fix is an import rather than a duplicate:

```markdown
@AGENTS.md

## Claude Code
Claude-specific instructions go below the import.
```

A symlink (`ln -s AGENTS.md CLAUDE.md`) also works when you need no Claude-specific additions. ([source](https://code.claude.com/docs/en/memory))

Codex loads `~/.codex/AGENTS.md`, then project and nested-directory `AGENTS.md` files as it walks toward the working directory; `AGENTS.override.md` lets a narrower directory replace broader guidance. ([source](https://developers.openai.com/codex/))

### Skills — the good news

Both harnesses implement the **[Agent Skills open standard](https://agentskills.io)** (originally developed by Anthropic, released as an open format, now adopted by Cursor, Gemini CLI, Copilot, OpenCode, Codex and many others). A skill is a folder with a `SKILL.md` containing at minimum `name` and `description`.

Only the directory differs: `.claude/skills/` vs `.agents/skills/`. Claude Code explicitly supports symlinked skill directories:

> "A `<skill-name>` entry in the enterprise, personal, or project locations can be a symlink to a directory elsewhere on disk. Claude Code follows the symlink and reads `SKILL.md` from the target directory."
> — [Claude Code skills docs](https://code.claude.com/docs/en/skills)

**Frontmatter portability warning.** The open spec allows exactly six fields: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Claude Code accepts more (`argument-hint`, `model`, `arguments`, …), but those are **Claude Code extensions**. Packaging or uploading a skill with a non-spec field fails with a hard error. Keeping to the six spec fields guarantees portability.

### Hooks — events differ

**Claude Code** exposes a very large event set, including `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStart/Stop`, `SessionStart/End`, `PreCompact/PostCompact`, `Notification`, `FileChanged`, `ConfigChange`, `InstructionsLoaded`, `TaskCreated/Completed`, and more. ([source](https://code.claude.com/docs/en/hooks))

**Codex** supports: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, `Stop`, `SessionStart`, `SessionEnd`, `SubagentStart`. ([source](https://learn.chatgpt.com/docs/hooks))

**The portable intersection** — safe to rely on in both: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `Stop`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, `PermissionRequest`.

Claude-only (do not expect in Codex): `Notification`, `FileChanged`, `InstructionsLoaded`, `ConfigChange`, `PostToolBatch`, `PostToolUseFailure`, `TaskCreated/Completed`, `WorktreeCreate/Remove`.

**Blocking contract is compatible.** In both harnesses, a `PreToolUse` hook blocks by exiting `2` with a message on stderr. Both also accept the richer JSON form `{"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "..."}}`. **Writing hooks with `exit 2` + stderr makes them work unchanged on both.**

**Tool-name matchers differ.** Codex file edits typically arrive as `apply_patch`; Claude's arrive as `Edit`/`Write`. A portable matcher is `Bash|Edit|Write|^apply_patch$`, and portable scripts must parse both `tool_input.file_path` and `apply_patch` command text.

**Codex hook trust.** Non-managed Codex hooks require explicit user review before running, and trust is tracked against a hash of the hook definition — *editing a hook triggers re-review*. If a Codex hook silently stops firing after you change it, this is why.

### Subagents — genuinely incompatible

Claude Code uses `.claude/agents/*.md` (markdown body + YAML frontmatter). Codex uses `.codex/agents/*.toml` with fields like `name`, `description`, `developer_instructions`, `model`, `sandbox_mode`. There is no shared format; these must be maintained separately. Keep the *prose* in a shared file that both definitions reference, so only the wrapper is duplicated.

---

## 3. Diagnosis of This Repository

Concrete problems found in the current template:

### 3.1 `.claude/rules/` is invisible to Codex — the big one

There are **25 rule files** in `.claude/rules/`, 22 of them with `paths:` frontmatter. Claude Code auto-loads all of them. **Codex loads none of them**, ever, automatically — it has no equivalent mechanism and does not read `.claude/`.

`AGENTS.md` currently asserts:

> "Shared calibration remains in `.claude/rules/` and `.claude/references/` so Claude and Codex use the same source of truth."

That is aspirational, not mechanical. Codex only sees those files if it happens to open them. **This alone explains most of the "Claude does what I want, Codex doesn't" asymmetry** — Claude is operating with 25 rule files in context and Codex with none.

### 3.2 `CLAUDE.md` and `AGENTS.md` are ~90% duplicated

160 and 185 lines respectively, differing only in a folder-tree block, one style bullet, and a Codex section. This will drift. The documented fix is the `@AGENTS.md` import.

### 3.3 Hook scripts have already drifted

**All 10 hook scripts differ** between `.claude/hooks/` and `.codex/hooks/`. Some differences are *essential* (`CLAUDE_PROJECT_DIR` vs `CODEX_PROJECT_DIR`, `apply_patch` parsing, JSON output shape). Others are pure drift:

- `protect-files.sh` protects `settings.json` **by basename** in the Claude copy, but only the literal paths `.claude/settings.json` and `.codex/config.toml` in the Codex copy.
- The Claude copy has `BASENAME` matching; the Codex copy dropped it.
- Error messages diverge.

So the *protection guarantees themselves* differ by harness — a real correctness bug, not cosmetic.

### 3.4 Five skills have drifted

`commit`, `context-status`, `learn`, `provenance-ledger` and one other differ between `.claude/skills/` and `.agents/skills/`, despite being conceptually the same skill.

---

## 4. Target Architecture: One Source, Thin Adapters

The principle: **exactly one canonical copy of every artifact; each harness gets a thin adapter pointing at it.**

```text
project/
├── AGENTS.md                  # CANONICAL instructions (Codex reads natively)
├── CLAUDE.md                  # 3 lines: "@AGENTS.md" + Claude-only notes
├── .agents/skills/            # CANONICAL skills (Agent Skills standard)
│   └── <skill>/SKILL.md       #   spec-only frontmatter: name, description, allowed-tools
├── automation/                # CANONICAL hook scripts (harness-agnostic)
│   ├── lib/harness.py         #   detects harness, normalizes tool_input
│   └── protect-files.sh
├── .claude/
│   ├── skills/<skill>  →symlink→ ../../.agents/skills/<skill>
│   ├── rules/*.md             # Claude-only: path-scoped progressive loading
│   ├── agents/*.md            # Claude subagent wrappers (prose in shared file)
│   └── settings.json          # hooks → automation/*
└── .codex/
    ├── agents/*.toml          # Codex subagent wrappers (same shared prose)
    └── hooks.json             # hooks → automation/*
```

### Step 1: Collapse the instruction files

`CLAUDE.md` becomes:

```markdown
@AGENTS.md

## Claude Code specifics
- Modular rules in `.claude/rules/` load automatically here (Codex has no equivalent).
```

Move all shared content into `AGENTS.md`. Single source, zero drift.

### Step 2: Symlink the skills

```bash
cd .claude/skills
for d in ../../.agents/skills/*/; do ln -s "$d" "$(basename "$d")"; done
```

Delete the duplicated copies first. Then reduce every `SKILL.md` frontmatter to the six spec fields so both harnesses (and any future tool) accept them.

### Step 3: One hook script, harness-agnostic

Instead of two drifting copies, write one script that normalizes the difference:

```bash
# automation/lib/detect.sh
ROOT="$(git rev-parse --show-toplevel 2>/dev/null \
  || printf '%s' "${CLAUDE_PROJECT_DIR:-${CODEX_PROJECT_DIR:-$PWD}}")"
```

and parse both shapes of file path (`tool_input.file_path` **and** `apply_patch` patch text) unconditionally. Both `settings.json` and `hooks.json` then point at `automation/protect-files.sh`. One script, one set of guarantees.

### Step 4: Solve the rules-parity gap

This is the hard one, and there are three honest options:

| Option | How | Trade-off |
|---|---|---|
| **A. Inline into AGENTS.md** | Move load-bearing rules into `AGENTS.md` itself | Both harnesses see them; costs context every session; Claude docs advise <200 lines |
| **B. Explicit read instruction** | `AGENTS.md` tells Codex to read specific rule files when doing matching work | Cheap, but Tier 1 — Codex may not comply |
| **C. `SessionStart` hook injection** | A hook prints the rules index into context at session start | Tier 2, fires deterministically in both harnesses |

**Recommended: A for the small set of non-negotiables** (raw-data policy, naming contracts, verification requirement), **B or C for the rest.** Do not try to make all 25 rules load in Codex — most are path-scoped precisely because they aren't always relevant.

> ⚠️ **Verify before relying on C:** the exact field for injecting context at `SessionStart` (`hookSpecificOutput.additionalContext` vs plain stdout) is documented inconsistently across the two harnesses. Test with a trivial hook that injects a sentinel string and confirm the agent can see it, before building on this.

---

## 5. The Enforcement Playbook

Choose the mechanism by the guarantee you need:

| You want… | Use | Why |
|---|---|---|
| An action **blocked**, always | `PreToolUse` hook, `exit 2` + stderr | Only true block; identical contract in both harnesses |
| A convention **validated** (filenames, paths) | `PreToolUse` hook matching path regex | Already proven here: `docs/work/meetings/` naming |
| A **reminder** after an action | `PostToolUse` hook, non-blocking | Nudges without breaking flow |
| A **checklist at session end** | `Stop` hook | Fires regardless of model intent |
| Context **when working on X files** | `.claude/rules/` with `paths:` (Claude); `AGENTS.md` (Codex) | Progressive loading saves context |
| A **repeatable procedure** | Skill in `.agents/skills/` | Loads on demand; portable |
| **Background knowledge** | `AGENTS.md` | Always in context |

**Anti-pattern to retire:** writing a procedural "always do X at step N" instruction into a rules file and treating the job as done. This template already contains a worked example of that failure (the abandoned `task_requirements` step). Rules describe; hooks enforce.

---

## 6. Case Study: The Plan Filename Problem

Your example — "only Codex respects the plan filename pattern" — is the perfect illustration, because **it is not a compliance failure at all.**

**Claude Code owns the plan file, not the agent.** In plan mode, the harness creates the plan file itself and assigns a random name (`idle-fishy-mazerunner.md`, `dreamy-orbiting-quokka.md`). The `plansDirectory` setting controls **only the location** — relative paths resolve from the workspace root, which is why yours land in `docs/work/plans/`. The naming scheme is not configurable: [claude-code issue #12619](https://github.com/anthropics/claude-code/issues/12619), which requests exactly per-repo plan naming, is **open and unimplemented**, labeled `enhancement`.

**Codex has no harness-owned plan file**, so the agent writes the file itself and follows your instruction — hence Codex "respects" the convention while Claude cannot.

**No amount of instruction tuning will fix the Claude side.** The available fixes:

1. **Post-hoc rename (recommended).** A `Stop` hook scans `docs/work/plans/` for files not matching `YYYY-MM-DD_*.md` and renames them, deriving the slug from the file's `# Title` heading. Deterministic, works in both harnesses, needs no harness support.
2. **Separate the artifacts.** Treat the harness plan file as disposable scratch, and have the archival plan be a normal file the agent writes (as in this repo's existing plans). Point `plansDirectory` at a gitignored scratch location so it never pollutes `docs/work/plans/`.
3. **Accept it** and let the random names sit in the folder.

Option 2 is architecturally cleanest — it stops conflating "the harness's plan-mode scratch buffer" with "the project's archived plan record." Option 1 is the smallest change.

**The generalizable lesson:** before writing a rule, ask *who owns this artifact*. If the harness owns it, only a hook (or a config setting, where one exists) can change the outcome — instructions are addressed to the wrong party entirely.

---

## 7. Verification: Proving a Rule Actually Binds

Never assume a convention holds. Test it:

| Check | Claude Code | Codex |
|---|---|---|
| Which instruction files loaded | `/context` → **Memory files** | Inspect session start output |
| Why a rule loaded/didn't | `InstructionsLoaded` hook logs it | *(no equivalent)* |
| Hook actually fires | Add a `logger`/`echo` line, watch for it | Same; check trust was granted |
| Skill discoverable | `/skills` or type `/` | `$skill-name` autocomplete |
| Config diagnosis | `/doctor` | `codex --version`, restart after config edits |

**Two failure modes specific to Codex:** hooks require trust approval before first run, and *editing a hook invalidates that trust* (tracked by hash), so a silently-dead hook after an edit usually means pending re-review. Also restart Codex after changing `config.toml`.

**A conformance test worth adding to `make`:** a script asserting that (a) every `.claude/skills/*` is a symlink into `.agents/skills/`, (b) `CLAUDE.md` contains the `@AGENTS.md` import, (c) both hook configs reference only scripts under `automation/`, (d) no skill frontmatter uses a non-spec field. That converts "keep them in sync" from a discipline into a check.

---

## 8. Migration Order

Do these in sequence; each is independently valuable:

1. **Collapse `CLAUDE.md` → `@AGENTS.md` import.** Removes the largest duplication immediately.
2. **De-duplicate hook scripts into `automation/`**, harness-agnostic, both configs pointing there. Fixes the real protection-divergence bug in `protect-files.sh`.
3. **Symlink skills** from `.claude/skills/` into `.agents/skills/`; trim frontmatter to the six spec fields.
4. **Decide the rules-parity policy** (§4 step 4) — promote non-negotiables into `AGENTS.md`, leave path-scoped detail Claude-only, and document that Codex won't see it.
5. **Fix the plan-file conflation** (§6 option 2), then add the conformance check from §7.

---

## Sources

- [Claude Code — memory & CLAUDE.md](https://code.claude.com/docs/en/memory)
- [Claude Code — skills](https://code.claude.com/docs/en/skills)
- [Claude Code — hooks reference](https://code.claude.com/docs/en/hooks)
- [claude-code issue #12619 — per-repo plan naming (open)](https://github.com/anthropics/claude-code/issues/12619)
- [claude-code issue #45728 — plan mode directory behavior](https://github.com/anthropics/claude-code/issues/45728)
- [Agent Skills open standard](https://agentskills.io)
- [Codex — build skills](https://learn.chatgpt.com/docs/build-skills.md)
- [Codex — hooks](https://learn.chatgpt.com/docs/hooks.md)
- [Codex — configuration](https://github.com/openai/codex/blob/main/docs/config.md)
- [Codex — subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
