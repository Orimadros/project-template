#!/usr/bin/env python3
"""
Context usage monitor for PostToolUse hooks.

Neither harness exposes an exact context percentage to hooks, so this uses a
tool-call counter as a conservative proxy. Warnings are returned as
PostToolUse additionalContext + systemMessage: Codex ignores plain stdout for
PostToolUse, and Claude Code's PostToolUse stdout is shown in the transcript
but is not delivered back to the model -- the JSON shape is what actually
reaches the agent on both.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

LEARN_THRESHOLDS = [40, 55, 65]
THRESHOLD_WARN = 80
THRESHOLD_CRITICAL = 90
THROTTLE_INTERVAL = 60
MAX_TOOL_CALLS = 150


def read_hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}


def project_dir_from(hook_input: dict) -> str:
    cwd = hook_input.get("cwd")
    if isinstance(cwd, str) and cwd:
        return cwd
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CODEX_PROJECT_DIR") or os.environ.get("PWD") or ""


def get_state_dir(project_dir: str) -> Path:
    state_home = Path(os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state"))
    project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:8] if project_dir else "default"
    state_dir = state_home / "agent-hooks" / project_hash
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def read_cache(state_dir: Path) -> dict:
    cache_file = state_dir / "context-monitor-cache.json"
    if not cache_file.exists():
        return {}
    try:
        return json.loads(cache_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(state_dir: Path, data: dict) -> None:
    try:
        (state_dir / "context-monitor-cache.json").write_text(json.dumps(data, indent=2))
    except OSError:
        pass


def estimate_context_percentage(state_dir: Path) -> float:
    cache = read_cache(state_dir)
    tool_calls = cache.get("tool_calls", 0) + 1
    cache["tool_calls"] = tool_calls
    save_cache(state_dir, cache)
    return min((tool_calls / MAX_TOOL_CALLS) * 100, 100)


def is_throttled(state_dir: Path, percentage: float) -> bool:
    cache = read_cache(state_dir)
    last_check = cache.get("last_check_time", 0)
    now = time.time()

    if percentage < THRESHOLD_WARN and (now - last_check) < THROTTLE_INTERVAL:
        return True

    cache["last_check_time"] = now
    save_cache(state_dir, cache)
    return False


def shown_thresholds(state_dir: Path) -> dict:
    cache = read_cache(state_dir)
    return {
        "learn": cache.get("shown_learn", []),
        "warn_80": cache.get("shown_warn_80", False),
        "warn_90": cache.get("shown_warn_90", False),
    }


def mark_threshold_shown(state_dir: Path, threshold_type: str, value: int | bool = True) -> None:
    cache = read_cache(state_dir)
    if threshold_type == "learn":
        shown = cache.get("shown_learn", [])
        if value not in shown:
            shown.append(value)
        cache["shown_learn"] = shown
    else:
        cache[f"shown_{threshold_type}"] = value
    save_cache(state_dir, cache)


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


def run_context_monitor() -> int:
    hook_input = read_hook_input()
    state_dir = get_state_dir(project_dir_from(hook_input))
    percentage = estimate_context_percentage(state_dir)

    if is_throttled(state_dir, percentage):
        return 0

    shown = shown_thresholds(state_dir)

    for threshold in LEARN_THRESHOLDS:
        if percentage >= threshold and threshold not in shown["learn"]:
            mark_threshold_shown(state_dir, "learn", threshold)
            return post_tool_context(
                f"Estimated context use is about {percentage:.0f}%. "
                "If this turn produced a reusable workflow or non-obvious correction, "
                "capture it in a project skill under .agents/skills/ before compaction."
            )

    if percentage >= THRESHOLD_CRITICAL and not shown["warn_90"]:
        mark_threshold_shown(state_dir, "warn_90", True)
        return post_tool_context(
            f"Estimated context use is about {percentage:.0f}%, and compaction may be near. "
            "Finish the current task carefully: update the plan/session log if needed and run verification."
        )

    if percentage >= THRESHOLD_WARN and not shown["warn_80"]:
        mark_threshold_shown(state_dir, "warn_80", True)
        return post_tool_context(
            f"Estimated context use is about {percentage:.0f}%. "
            "Auto-compaction should preserve the important state, but keep plan and log files current."
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_context_monitor())
    except Exception:
        sys.exit(0)
