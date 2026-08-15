#!/usr/bin/env python3
"""
Session Log Reminder Hook

A Stop hook that tracks how many responses have passed since the session
log was last updated. After a threshold, it blocks stopping via a JSON
{"decision": "block", "reason": ...} response and reminds the agent to
update the session log.

Adapted from: https://gist.github.com/michaelewens/9a1bc5a97f3f9bbb79453e5b682df462
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

THRESHOLD = 15


def read_hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, OSError):
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


def get_state_path(project_dir: str) -> Path:
    return get_state_dir(project_dir) / "log-reminder-state.json"


def load_state(state_path: Path) -> dict:
    try:
        return json.loads(state_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"counter": 0, "last_mtime": 0.0, "reminded": False, "no_log_reminded": False}


def save_state(state_path: Path, state: dict) -> None:
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state))
    except OSError:
        pass


def find_latest_log(project_dir: str) -> tuple[Path | None, float]:
    log_dir = Path(project_dir) / "docs/work" / "session_logs"
    if not log_dir.is_dir():
        return None, 0.0

    md_files = list(log_dir.glob("*.md"))
    if not md_files:
        return None, 0.0

    latest = max(md_files, key=lambda f: f.stat().st_mtime)
    return latest, latest.stat().st_mtime


def block(reason: str) -> int:
    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    return 0


def main() -> int:
    hook_input = read_hook_input()

    # If a Stop hook already blocked this turn, let it stop now to avoid a
    # continuation loop.
    if hook_input.get("stop_hook_active", False):
        return 0

    project_dir = project_dir_from(hook_input)
    if not project_dir:
        return 0

    state_path = get_state_path(project_dir)
    state = load_state(state_path)

    latest_log, current_mtime = find_latest_log(project_dir)
    today = datetime.now().strftime("%Y-%m-%d")

    if latest_log is None:
        if not state.get("no_log_reminded", False):
            state["no_log_reminded"] = True
            save_state(state_path, state)
            return block(
                f"No session log exists yet. Create one at "
                f"docs/work/session_logs/{today}_description.md before continuing. "
                "Include the current goal and key context."
            )
        return 0

    if current_mtime != state["last_mtime"]:
        save_state(
            state_path,
            {"counter": 0, "last_mtime": current_mtime, "reminded": False, "no_log_reminded": False},
        )
        return 0

    state["counter"] += 1

    if state["counter"] >= THRESHOLD and not state["reminded"]:
        state["reminded"] = True
        save_state(state_path, state)
        return block(
            f"SESSION LOG REMINDER: {state['counter']} responses without updating the session log. "
            f"Append recent progress, decisions, and verification status to {latest_log.name}."
        )

    save_state(state_path, state)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
