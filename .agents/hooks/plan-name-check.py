#!/usr/bin/env python3
"""
Instruct the agent to rename any file in docs/work/plans/ that doesn't
match the YYYY-MM-DD_slug.md naming convention -- automatically, without
needing the human to notice a message and ask for it.

Registered on BOTH harnesses. Two entry points, dispatched by
hook_event_name, each using the mechanism that actually reaches the model
for that event (a plain "systemMessage" is display-only and is never fed
back as something to act on):
  - PostToolUse (Write|Edit|apply_patch): checks paths touched by this
    tool call and returns hookSpecificOutput.additionalContext -- the same
    mechanism context-monitor.py/provenance-reminder.py/verify-reminder.py
    use, confirmed live in this repo to actually reach the model. Catches
    Codex immediately, since Codex writes its own plan file through a
    normal tool call.
  - Stop: sweeps the whole docs/work/plans/ directory and returns
    {"decision": "block", "reason": ...} -- the same mechanism
    log-reminder.py already uses to force the agent to continue instead of
    stopping. Needed because Claude Code's plan-mode file is created by the
    harness itself and may never pass through a Write/Edit tool call this
    hook can see, so the PostToolUse path alone would silently miss it.
    Guarded by stop_hook_active exactly like log-reminder.py, so a second
    consecutive Stop is allowed through rather than looping forever if the
    agent doesn't (or can't) act on the first one.

Doesn't use exit 2 / PreToolUse-style hard blocking -- the write itself
always succeeds; only the conversation's continuation is steered.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLANS_DIR = Path("docs/work/plans")
VALID_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
IGNORED_NAMES = {".gitkeep"}


def read_hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}


def project_dir_from(hook_input: dict) -> Path:
    import os

    cwd = hook_input.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd)
    value = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CODEX_PROJECT_DIR") or os.environ.get("PWD")
    return Path(value) if value else Path.cwd()


def extract_patch_paths(command: str) -> list[str]:
    paths = []
    for line in command.splitlines():
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def touched_paths(hook_input: dict) -> list[str]:
    tool_input = hook_input.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return []
    raw = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            raw.append(value)
    command = tool_input.get("command")
    if isinstance(command, str):
        raw.extend(extract_patch_paths(command))
    return raw


def suggest_slug(path: Path) -> str:
    """Derive a suggested slug from the file's first `# ` heading, if readable."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "description"
    for line in text.splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            return slug or "description"
    return "description"


def rename_targets(bad_paths: list[Path]) -> list[tuple[Path, str]]:
    from datetime import date

    today = date.today().isoformat()
    targets = []
    for path in bad_paths:
        slug = suggest_slug(path)
        targets.append((path, f"{today}_{slug}.md"))
    return targets


def violation_message(bad_paths: list[Path]) -> str:
    targets = rename_targets(bad_paths)
    lines = [
        "PLAN FILENAME VIOLATION: rename the following file(s) under docs/work/plans/ "
        "now, using your file tools, before doing anything else. Use the suggested name "
        "as a starting point, but prefer a date matching when the plan was actually "
        "written if you know it, and shorten an overly long slug if the heading was verbose."
    ]
    for path, suggested in targets:
        lines.append(f"  - Rename {path.name} -> {suggested}")
    return "\n".join(lines)


def short_summary(bad_paths: list[Path]) -> str:
    names = ", ".join(p.name for p in bad_paths[:3])
    return f"Plan filename convention violation: renaming {names} now."


def check_paths(candidates: list[str], project_dir: Path) -> list[Path]:
    bad = []
    for raw in candidates:
        p = Path(raw)
        if not p.is_absolute():
            p = project_dir / p
        try:
            rel = p.resolve().relative_to(project_dir.resolve())
        except (ValueError, OSError):
            continue
        if len(rel.parts) == 4 and rel.parts[:3] == ("docs", "work", "plans"):
            if rel.name not in IGNORED_NAMES and not VALID_NAME.match(rel.name):
                bad.append(p)
    return bad


def sweep_plans_dir(project_dir: Path) -> list[Path]:
    plans_dir = project_dir / PLANS_DIR
    if not plans_dir.is_dir():
        return []
    bad = []
    for path in plans_dir.glob("*.md"):
        if path.name in IGNORED_NAMES:
            continue
        if not VALID_NAME.match(path.name):
            bad.append(path)
    return bad


def emit_stop_directive(message: str) -> int:
    """Stop hooks reach the model by forcing continuation, not by display
    text -- a bare systemMessage is shown to the human only."""
    json.dump({"decision": "block", "reason": message}, sys.stdout)
    return 0


def emit_posttool_directive(message: str, summary: str) -> int:
    """PostToolUse hooks reach the model via additionalContext; systemMessage
    alone is display-only. Kept alongside for human-visible confirmation."""
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": message,
            },
            "systemMessage": summary,
        },
        sys.stdout,
    )
    return 0


def main() -> int:
    hook_input = read_hook_input()
    project_dir = project_dir_from(hook_input)
    event = hook_input.get("hook_event_name", "")

    if event == "Stop":
        if hook_input.get("stop_hook_active", False):
            return 0
        bad = sweep_plans_dir(project_dir)
        if not bad:
            return 0
        return emit_stop_directive(violation_message(bad))

    bad = check_paths(touched_paths(hook_input), project_dir)
    if not bad:
        return 0
    return emit_posttool_directive(violation_message(bad), short_summary(bad))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
