# Cross-Harness Parity: Make the Template Bind Equally in Claude Code and Codex

**Date:** 2026-08-14
**Status:** DRAFT

---

## Context

This template is maintained for two harnesses at once. Today it behaves differently in each, and the divergence is structural, not cosmetic:

- **Codex sees none of the 25 rule files.** Claude auto-loads `.claude/rules/*.md`; Codex has no equivalent mechanism and never reads `.claude/`. `AGENTS.md` claims these are a "shared source of truth" — that is aspirational, not mechanical. This is the single largest cause of "Claude does what I want, Codex doesn't."
- **Every shared artifact exists twice and has drifted.** All 10 hook scripts differ; 4 skills differ; `CLAUDE.md`/`AGENTS.md` are near-duplicates (AGENTS.md is a strict superset — Claude currently never sees its "scripts should be readable" bullet). One drift is a real correctness bug: `protect-files.sh` protects `settings.json` *by basename* on the Claude side but only by literal path on the Codex side, so **protection guarantees depend on which harness you opened**.
- **Some rules cannot be satisfied by the harness they target.** Claude Code's plan mode has the *harness* name the plan file; `plansDirectory` sets location only and naming is unimplemented ([issue #12619](https://github.com/anthropics/claude-code/issues/12619)). This very plan file is the proof.
- **No enforcement layer exists for any of it.** 118 textual references to `.claude/rules/` across 74 files, and not one hook or script reads the directory. Conventions are asserted in prose and verified by nothing.

**Intended outcome:** one canonical copy of every shared artifact, a mechanism that gives Codex path-scoped rules, and a `make check` target that turns "keep them in sync" from a discipline into a build failure.

⚠️ **Local `main` has zero commits.** `HEAD` is an unknown revision with 235 paths staged; `origin/main` is at `04508ab`. There is no local rollback point until Step 0.

---

## Locked Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Rule bodies | **Stay at `.claude/rules/`** | Consumer is code we own (the injector), so no symlink needed. Moving = 118 edits across 74 files with zero behavioral gain, and wouldn't achieve neutrality anyway while `.claude/references/` (56 refs) stays put. |
| Codex rules | **PostToolUse injector hook** | Only mechanism Codex offers. `additionalContext` is already proven working in this repo's `.codex/hooks/provenance-reminder.py`. |
| Skills | **Symlinks**, canonical at `.agents/skills/` | User choice. Drift becomes structurally impossible. Relative targets survive clone on macOS/Linux; `make check` C1 fails loudly on a Windows-corrupted clone. |
| Agents | **Generated, committed** | 23/24 bodies are byte-identical; only the wrapper differs. Committed so a fresh clone works with no build step. |
| Hooks | **One script set at `.agents/hooks/`** | Both configs point at it. Real files, not symlinks — Codex trusts hooks by path+hash. |
| Plan filenames | **Warn-and-rename hook** | Keeps the naming contract; surfaces violations automatically instead of leaving an unmeetable rule on the books. |

---

## Target Architecture

```text
AGENTS.md                    # CANONICAL instructions (+ folded "Standing Rules")
CLAUDE.md                    # stub: "@AGENTS.md" + Claude-only notes
.agents/
  skills/<name>/SKILL.md     # CANONICAL skills, spec-only frontmatter
  hooks/*.{py,sh}            # CANONICAL hook scripts, harness-agnostic
.claude/
  skills/<name> →symlink→ ../../.agents/skills/<name>
  rules/*.md                 # CANONICAL rules (shared; name is historical)
  references/*.md            # CANONICAL calibration (shared)
  agents/*.md                # CANONICAL subagent sources
  settings.json              # hooks → .agents/hooks/*
.codex/
  agents/*.toml              # GENERATED from .claude/agents/*.md
  hooks.json                 # hooks → .agents/hooks/* (+ rule-injector)
code/03_quality/
  check_conformance.py       # make check
  gen_codex_agents.py        # make agents
```

---

## Steps

Each step is one commit. Risk noted; all are `git revert`-able except where flagged.

### Step 0 — Commit the current tree · risk: critical if skipped
`git add -A && git commit`. Creates the first local rollback point. **Do this before touching one byte.** Review `git status` output for anything unintended before staging.

### Step 1 — Conformance checker + `make check` · risk: very low
New `code/03_quality/check_conformance.py`, imitating the `Finding`/severity/`--root`/exit-2 pattern of the existing [check_provenance_ledger.py](code/03_quality/check_provenance_ledger.py). Wire as `check: @python3 code/03_quality/check_conformance.py`. Add `check`, `agents`, **and the currently-missing `all`** to `.PHONY`.

Invariants (ERROR unless noted):

| # | Check |
|---|---|
| C1 | Every `.claude/skills/<n>` is a symlink with a **relative** target resolving to `.agents/skills/<n>`; name sets equal both ways; `SKILL.md` exists |
| C2 | `CLAUDE.md` contains a line matching `^@AGENTS\.md\s*$`; WARN if > 20 lines |
| C3 | Every `command` in both hook configs resolves under `.agents/hooks/` and exists; `.claude/hooks/` and `.codex/hooks/` no longer exist |
| C4 | Skill frontmatter keys ⊆ {name, description, license, compatibility, metadata, allowed-tools}; `name` == dirname |
| C5 | `gen_codex_agents.py --check` passes; every TOML parses under `tomllib`; name sets equal |
| C6 | Every `.claude/rules/*.md` has `paths:` frontmatter with ≥1 glob |
| C7 | (WARN) Globs naming `.claude/skills` have an `.agents/skills` twin; `.claude/agents` ↔ `.codex/agents` |
| C8 | No dangling `.claude/(rules\|references)/*.md` reference in any tracked text file — **insurance for the 118 references we are deliberately not moving** |
| C9 | (WARN) Hook event names outside the portable intersection, minus an allowlist (`Notification`) |
| C10 | (WARN) `.agents/**` contains no lone `CLAUDE_PROJECT_DIR`/`CODEX_PROJECT_DIR` or brand strings |
| C11 | (WARN) `AGENTS.md` ≤ 250 lines |
| C12 | `rule-injector.py`, if present, is registered in `.codex/hooks.json` and **absent** from `.claude/settings.json` |
| C13 | The AGENTS.md "Rules Index" lists every file in `.claude/rules/` and names no file that doesn't exist |

Expect ~40 failures on first run. That is the baseline, not a bug — build the checker first so every later step is verified rather than asserted.

### Step 2 — Fix `pedagogy-reviewer.toml` by hand · risk: very low
It uses `'''` (literal string) while containing doubled backslashes, so it renders `\\sectiontransition` instead of `\sectiontransition`. Standalone bug fix, shipped before the generator so the two aren't entangled.

### Step 3 — Agent generator · risk: low
New `code/03_quality/gen_codex_agents.py` + `make agents`; regenerate all 24 TOMLs.

- Parse YAML frontmatter → `name`, `description`, `tools`, `model`; body is the rest.
- **Always emit `"""`**, escaping `\`→`\\` and `"""`. Never `'''` — makes Step 2's defect structurally unrepeatable.
- Fixed key order; header comment `# GENERATED — do not edit. Source: … Run: make agents` (stripped by the comparator).
- **Synthesize a tool-boundary paragraph** from the MD `tools:` field. Codex has no `tools` equivalent, so per-agent restrictions are *silently* lost today — 3 read-only reviewers (`domain-reviewer`, `pedagogy-reviewer`, `tikz-reviewer`) can currently write under Codex. Soft textual enforcement beats silence.
- `--check` mode: regenerate in memory, byte-compare, exit 2, never write.

### Step 4 — Collapse instruction files · risk: low–medium
- `CLAUDE.md` → `@AGENTS.md` + a short Claude-only section.
- Fold the 3 no-frontmatter rules (`meta-governance.md`, `orchestrator-protocol.md`, `session-logging.md` — 102 lines) into an AGENTS.md **"Standing Rules"** section, then delete those files. Claude gets them via the import; Codex gets them natively; and `.claude/rules/` becomes 100% path-scoped, which makes C6 checkable.
- Add a **"Rules Index"** section to AGENTS.md: one line per rule file — path, one-line scope, and when it applies. This is a deliberate **Tier-1 fallback layer**, not the mechanism: it costs ~25 lines, is always in context for both harnesses, and covers the window before the injector fires (and any path the globs miss). Checked current by C13.
- Pay for the added lines by trimming the folder-structure ASCII tree and the placeholder `Current Project State` table.
- Verify `@AGENTS.md` actually imports (`/context` → Memory files) before proceeding.

### Step 5 — Neutralize skills · risk: medium — **must precede Step 6**
Symlinking first would destroy the Codex-side text. Rewrite the 4 drifted skills harness-neutral:

| Skill | Drift | Resolution |
|---|---|---|
| `context-status` | `~/.claude/sessions/*` vs `$CODEX_HOME/sessions` | dissolves once Step 7 lands the shared state path |
| `learn` | writes to `.claude/skills/` vs `.agents/skills/` | `.agents/skills/` (canonical) |
| `provenance-ledger` | "whenever Claude…" vs "whenever Codex…" | "whenever the agent…" |
| `commit` | `.claude/settings.local.json` vs `.codex/config.toml`; brand trailer | list both; genericize trailer |

Also strip the 27 non-spec frontmatter keys across all 26 skills (`argument-hint`×24, `author`×2, `version`×2, `context`×1), relocating `argument-hint` content to an `## Arguments` line in the body.

### Step 6 — Skills → symlinks · risk: medium–high, **partially irreversible**
Make `.agents/skills/` canonical; replace each `.claude/skills/<n>` with a **relative** symlink.

**Smoke-test in Claude Code before committing:** confirm a skill loads through the symlink *in this Google Drive working copy*. If it doesn't, fall back to generated copies verified by C1. `git revert` restores correctly on macOS/Linux, but a Windows or `core.symlinks=false` clone will already have corrupted them into text files — C1 is what makes that failure loud instead of silent. Document the Windows caveat in `README.md`.

### Step 7 — Consolidate hooks → `.agents/hooks/` · risk: high
Delete `.claude/hooks/` and `.codex/hooks/`; repoint both configs. **One commit only** — editing hooks changes their hashes and forces a one-time Codex trust re-review.

Shared abstractions that dissolve the essential differences without harness branching:
- `project_root()`: `payload["cwd"]` → `git rev-parse --show-toplevel` → `$CLAUDE_PROJECT_DIR` → `$CODEX_PROJECT_DIR` → `$PWD`.
- Neutral state dir `${XDG_STATE_HOME:-$HOME/.local/state}/agent-hooks/<project>/<session>/`.
- Always parse **both** `file_path`/`path` and `*** (Add|Update|Delete) File:` patch headers (harmless no-op under Claude).
- Always emit `{"hookSpecificOutput": {…}, "systemMessage": …}`. **This likely fixes a live Claude bug**: `.claude/hooks/provenance-reminder.py` currently uses a bare `print()`, which Claude shows in transcript but does not inject as context — the Codex copy does it correctly. Smoke-test before/after.

Two drifts need deliberate resolution, not mechanical merging:
- **`protect-files.sh`** — take the **Codex** semantics (literal paths), extended to `.claude/settings.json`, `.claude/settings.local.json`, `.codex/config.toml`. Basename matching would block unrelated project files.
- **`notify.sh`** — probe the payload shape (`message`/`title` if present, else synthesize from `tool_name`) rather than sniffing the harness.

Verify `exit 2` still blocks a protected-file write **under both harnesses** before committing.

### Step 8 — Codex rule injector + plan-name checker · risk: medium
New `.agents/hooks/rule-injector.py`, registered in **`.codex/hooks.json` only** (Claude auto-loads rules natively; registering both sides double-loads everything — C12 guards this).

PostToolUse, matcher `Read|Bash|Edit|Write|^apply_patch$`, `timeout: 10`:
1. Build a cached index of `.claude/rules/*.md` `paths:` globs at `<state>/rules-index.json`, invalidated by `(file count, max mtime_ns)`.
2. Match the touched path against globs — against **both** the raw relative path and the symlink-resolved path (Step 6 makes `.claude/skills/**` globs fire as `.agents/skills/**`).
3. Rank matches by specificity (literal path segments before first wildcard, desc). **Always inject rank-1 in full**; fill remaining ranks until a **6,000-char per-event budget** is spent; spill the rest to one-line pointers using each file's `# ` heading. Session-cumulative cap 30,000 chars.
4. Dedupe with **atomic marker files** — `os.open(…, O_CREAT|O_EXCL)` at `<state>/rules/<rule>.mark`. No JSON read-modify-write (races and loses updates under parallel tool calls); no project-keyed state (would go permanently silent after session 1).
5. `session_id` resolution: `session_id` → `conversation_id` → `$CODEX_SESSION_ID` → `md5(transcript_path)` → else **disable dedup and fall back to a 10-minute throttle**.
6. On `SessionStart` with source `compact`/`resume`, delete the session's marker dir — compaction discards injected context, and stale markers would suppress re-injection forever. Three lines inside the existing `post-compact-restore.py`; no new hook registration, no second trust review.
7. Wrap in `except Exception: sys.exit(0)` so a slow Google Drive stat degrades to "no injection", never a blocked tool call.

**Ship log-only first** (suppress `additionalContext`) for one session to confirm payload shapes and `session_id` presence, then enable.

Sizing measured: 25 rules ≈ 15.2k tokens total; worst single-file co-match is a slides `.tex` at 11 rules ≈ 7.6k tokens — which is exactly why the burst budget exists.

**Plan-name checker** (same step): PostToolUse on `Write|Edit|^apply_patch$` warns immediately when a file lands in `docs/work/plans/` not matching `YYYY-MM-DD_slug.md`, **plus** a `Stop`-hook sweep of the directory as the safety net — Claude's plan file is created by the harness and may never pass through the `Write` tool, so the PostToolUse path alone would miss it. Both emit a rename suggestion derived from the file's `# ` heading; neither blocks.

---

## Verification

Run after each step:

```bash
make check
```

End-to-end, after Step 8:

1. `make check` — clean (warnings acceptable, zero errors).
2. `make agents` — produces no diff (`git diff --exit-code .codex/agents/`).
3. **Claude:** start a session, `/context` → confirm `CLAUDE.md` under Memory files and that `@AGENTS.md` content is present. Invoke a symlinked skill (e.g. `/checkpoint`) and confirm it loads.
4. **Codex:** start a session, open `docs/deliverables/slides/*/*.tex`, confirm the slide-writing rules arrive as injected context. Open a `code/**/*.R` file, confirm R conventions arrive and the slides rules are *not* re-injected.
5. **Both:** attempt to edit an existing file in `data/raw/` — confirm `exit 2` blocks it with the same message in each harness.
6. **Both:** write a file to `docs/work/plans/bad-name.md` — confirm the warning fires with a rename suggestion.
7. `make provenance`, `make articles`, `make slides` — confirm nothing regressed.

---

## Alternatives Considered and Rejected

Two native-looking Codex mechanisms were evaluated as replacements for the injector hook. Both fail for this repo; recording the evidence so it isn't re-litigated.

**Nested `AGENTS.md` per directory — rejected: scoped by the wrong thing.** Codex walks from the git root *down to the current working directory*, reading each `AGENTS.md` on that path, and "builds its instruction chain once per run." Scope is keyed to **where the session was launched**, not to which file the agent touches. A `docs/deliverables/slides/AGENTS.md` would load only if you ran `cd docs/deliverables/slides && codex`; launched at repo root — the normal case — it never loads, because it sits *below* the cwd rather than between root and cwd. (Related known limitation: [codex#13288](https://github.com/openai/codex/issues/13288).)

Still worth adding opportunistically later: a small `AGENTS.md` in `code/` and `docs/deliverables/slides/` costs nothing and helps sessions actually launched there. It is a complement, not a mechanism.

**`@file.md` imports in `AGENTS.md` — rejected: does not exist in Codex.** [codex#17401](https://github.com/openai/codex/issues/17401) (April 2026) requests exactly this — "*Add an `@path/to/file.md` directive to AGENTS.md that the CLI resolves at instruction-assembly time*" — and is **open and unimplemented**, framed explicitly as a gap versus Claude Code, which does support it. In Codex an `@path` line is inert text; the model may or may not choose to read the file. That is Tier 1, which is what the Rules Index in Step 4 already provides honestly, without implying a resolver that isn't there.

**Corollary — a common bridge suggestion that cannot work:** "point `.claude/rules/` at a shared folder using YAML `paths:` frontmatter." `paths:` controls *when a rule activates*, not *where its content lives*. Sharing a directory requires symlinks or generated copies; frontmatter cannot redirect it.

**Net:** the PostToolUse injector is the only mechanism that gives Codex *per-file* rule scoping. The Rules Index is its Tier-1 safety net.

---

## Notes

- **`.claude/rules/` and `.claude/references/` are shared, harness-neutral calibration.** The directory name is historical. Add one sentence saying so to AGENTS.md rather than moving 118 references.
- **Do not** unify `.claude/settings.json` with `.codex/hooks.json` — different schemas, and Claude's also carries `permissions`/`plansDirectory`. Two thin configs over one script set is the correct factoring.
- **Do not** generate agents via a hook — it would fight `protect-files.sh`, inject surprise diffs, and break the clean-clone guarantee.
- Steps 1–3 are order-independent and could land immediately. Steps 6 and 7 warrant manual smoke tests in both harnesses before their commits.

## Provenance Ledger Impact

- **Affected assets:** none — infrastructure only, no data or results
- **Nested records required:** N/A
- **Expected status:** N/A

---

## Approval

[ ] User approved:
