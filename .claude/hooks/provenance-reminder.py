#!/usr/bin/env python3
"""
Non-blocking Provenance Ledger reminder for Claude Code.
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
        if MAKE_STAGE_RE.search(command) or any(prefix in command for prefix in WATCH_PREFIXES):
            return True

    return any(normalize(candidate, cwd).startswith(WATCH_PREFIXES) for candidate in candidates)


def main() -> int:
    hook_input = read_hook_input()
    if touched_data_surface(hook_input):
        print(
            "Provenance Ledger reminder: update docs/data/provenance-ledger/ "
            "with asset and variable-level provenance, then run make provenance."
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        raise SystemExit(0)
