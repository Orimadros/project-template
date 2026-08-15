#!/usr/bin/env python3
"""
Warn (never block) when a file in docs/work/plans/ doesn't match the
YYYY-MM-DD_slug.md naming convention.

Registered on BOTH harnesses. Two entry points, dispatched by
hook_event_name:
  - PostToolUse (Write|Edit|apply_patch): checks paths touched by this
    tool call. Catches Codex immediately, since Codex writes its own plan
    file through a normal tool call.
  - Stop: sweeps the whole docs/work/plans/ directory. Needed because
    Claude Code's plan-mode file is created by the harness itself and may
    never pass through a Write/Edit tool call this hook can see -- the
    PostToolUse path alone would silently miss it.

Both paths emit the same non-blocking notice; neither uses exit 2 or a
"decision": "block" response.
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


def violation_message(bad_paths: list[Path]) -> str:
    from datetime import date

    today = date.today().isoformat()
    lines = ["Plan filename convention check: the following file(s) under docs/work/plans/ don't match YYYY-MM-DD_slug.md:"]
    for path in bad_paths:
        slug = suggest_slug(path)
        lines.append(f"  - {path.name} -> suggest renaming to {today}_{slug}.md (or a date matching when the plan was actually written)")
    lines.append("This is a non-blocking notice. Rename at your convenience; it will not stop or fail the current action.")
    return "\n".join(lines)


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


def emit_notice(message: str) -> int:
    json.dump({"systemMessage": message}, sys.stdout)
    return 0


def main() -> int:
    hook_input = read_hook_input()
    project_dir = project_dir_from(hook_input)
    event = hook_input.get("hook_event_name", "")

    if event == "Stop":
        if hook_input.get("stop_hook_active", False):
            return 0
        bad = sweep_plans_dir(project_dir)
    else:
        bad = check_paths(touched_paths(hook_input), project_dir)

    if not bad:
        return 0

    return emit_notice(violation_message(bad))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
