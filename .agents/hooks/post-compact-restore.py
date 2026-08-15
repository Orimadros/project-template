#!/usr/bin/env python3
"""
Post-Compact Context Restoration Hook

Fires after compaction/resume (SessionStart, matcher "compact|resume") to
restore context. Reads state saved by pre-compact.py and reports it back
via {"hookSpecificOutput": {"hookEventName": "SessionStart",
"additionalContext": ...}} -- valid JSON should satisfy a "parse as JSON,
fall back to plain text" SessionStart handler on either harness, whereas a
plain-text-only payload is not guaranteed to reach the model.

Hook Event: SessionStart (matcher: "compact|resume")
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


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


def read_pre_compact_state(state_dir: Path) -> dict | None:
    state_file = state_dir / "pre-compact-state.json"
    if not state_file.exists():
        return None

    try:
        state = json.loads(state_file.read_text())
        state_file.unlink()  # Clean up after restore
        return state
    except (json.JSONDecodeError, OSError):
        return None


def find_active_plan(project_dir: str) -> dict | None:
    plans_dir = Path(project_dir) / "docs/work" / "plans"
    if not plans_dir.exists():
        return None

    plan_files = sorted(plans_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not plan_files:
        return None

    latest_plan = plan_files[0]
    content = latest_plan.read_text(errors="replace")

    status = "unknown"
    if "COMPLETED" in content.upper():
        status = "completed"
    elif "APPROVED" in content.upper():
        status = "in_progress"
    elif "DRAFT" in content.upper():
        status = "draft"

    current_task = None
    for line in content.splitlines():
        if "- [ ]" in line:
            current_task = line.replace("- [ ]", "").strip()
            break

    return {
        "plan_path": str(latest_plan),
        "plan_name": latest_plan.name,
        "status": status,
        "current_task": current_task,
    }


def find_recent_session_log(project_dir: str) -> dict | None:
    logs_dir = Path(project_dir) / "docs/work" / "session_logs"
    if not logs_dir.exists():
        return None

    log_files = sorted(logs_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not log_files:
        return None

    return {"log_path": str(log_files[0]), "log_name": log_files[0].name}


def restoration_message(
    pre_compact_state: dict | None,
    plan_info: dict | None,
    session_log: dict | None,
) -> str:
    lines = ["Context restored after compaction:"]

    if pre_compact_state:
        lines.append("Pre-compaction state:")
        if pre_compact_state.get("plan_path"):
            lines.append(f"- Plan: {pre_compact_state['plan_path']}")
        if pre_compact_state.get("current_task"):
            lines.append(f"- Task: {pre_compact_state['current_task']}")
        if pre_compact_state.get("decisions"):
            decisions = "; ".join(pre_compact_state["decisions"][-3:])
            lines.append(f"- Recent decisions: {decisions}")

    if plan_info:
        lines.append(f"Active plan: {plan_info['plan_name']} ({plan_info['status']}).")
        if plan_info.get("current_task"):
            lines.append(f"Next unchecked task: {plan_info['current_task']}.")

    if session_log:
        lines.append(f"Recent session log: {session_log['log_name']}.")

    lines.append("Recovery actions: read the active plan, check git status/diff, and continue from the saved task.")
    return "\n".join(lines)


def emit_session_context(message: str) -> int:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message,
            },
            "systemMessage": message,
        },
        sys.stdout,
    )
    return 0


def main() -> int:
    hook_input = read_hook_input()
    if hook_input.get("source") not in ("compact", "resume"):
        return 0

    project_dir = project_dir_from(hook_input)
    if not project_dir:
        return 0

    state_dir = get_state_dir(project_dir)
    pre_compact_state = read_pre_compact_state(state_dir)
    plan_info = find_active_plan(project_dir)
    session_log = find_recent_session_log(project_dir)

    if pre_compact_state or plan_info or session_log:
        return emit_session_context(restoration_message(pre_compact_state, plan_info, session_log))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
