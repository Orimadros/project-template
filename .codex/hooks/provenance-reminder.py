#!/usr/bin/env python3
"""
Non-blocking Provenance Ledger reminder for Codex.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


WATCH_PREFIXES = ("code/00_fetch/", "code/01_build/", "code/02_analyze/", "data/", "results/")
MAKE_STAGE_RE = re.compile(r"\bmake\s+(fetch|build|analysis|all)\b")


def read_hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}


def extract_patch_paths(command: str) -> list[str]:
    paths: list[str] = []
    for line in command.splitlines():
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def normalize(path: str, cwd: str) -> str:
    path_obj = Path(path)
    if path_obj.is_absolute() and cwd:
        try:
            return path_obj.relative_to(cwd).as_posix()
        except ValueError:
            return path_obj.as_posix()
    return path_obj.as_posix()


def touched_data_surface(hook_input: dict) -> bool:
    cwd = str(hook_input.get("cwd") or "")
    tool_input = hook_input.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return False

    candidates: list[str] = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            candidates.append(value)

    command = tool_input.get("command")
    if isinstance(command, str):
        candidates.extend(extract_patch_paths(command))
        if MAKE_STAGE_RE.search(command) or any(prefix in command for prefix in WATCH_PREFIXES):
            return True

    for candidate in candidates:
        rel_path = normalize(candidate, cwd)
        if rel_path.startswith(WATCH_PREFIXES):
            return True

    return False


def post_tool_context(message: str) -> int:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": message,
            },
            "systemMessage": message,
        },
        sys.stdout,
    )
    return 0


def main() -> int:
    hook_input = read_hook_input()
    if not touched_data_surface(hook_input):
        return 0

    return post_tool_context(
        "Provenance Ledger reminder: data pipeline or asset paths were touched. "
        "Before completion, update docs/data/provenance-ledger/ with asset and variable-level provenance, "
        "then run make provenance."
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        raise SystemExit(0)
