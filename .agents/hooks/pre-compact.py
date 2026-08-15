#!/usr/bin/env python3
"""
Pre-Compact State Capture Hook

Fires before context compaction to capture the current state:
- Active plan path and status
- Current task description
- Recent decisions from session log

This state is read by post-compact-restore.py after compaction.

Hook Event: PreCompact
Prints a human-readable summary to stderr (shown to the user) and also
emits {"systemMessage": ...} on stdout, since it's unclear which channel
each harness actually surfaces for a non-blocking PreCompact hook -- both
are cheap to emit.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
NC = "\033[0m"


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


def find_active_plan(project_dir: str) -> dict | None:
    plans_dir = Path(project_dir) / "docs/work" / "plans"
    if not plans_dir.exists():
        return None

    plan_files = sorted(plans_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    for plan_file in plan_files[:3]:
        content = plan_file.read_text(errors="replace")
        if "COMPLETED" in content.upper():
            continue

        status = "in_progress"
        if "APPROVED" in content.upper():
            status = "approved"
        elif "DRAFT" in content.upper():
            status = "draft"

        current_task = None
        for line in content.splitlines():
            if "- [ ]" in line:
                current_task = line.replace("- [ ]", "").strip()
                break

        return {
            "plan_path": str(plan_file),
            "plan_name": plan_file.name,
            "status": status,
            "current_task": current_task,
        }

    return None


def extract_recent_decisions(project_dir: str, limit: int = 3) -> list[str]:
    logs_dir = Path(project_dir) / "docs/work" / "session_logs"
    if not logs_dir.exists():
        return []

    log_files = sorted(logs_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not log_files:
        return []

    content = log_files[0].read_text(errors="replace")
    decisions: list[str] = []
    patterns = [
        r"Decision:\s*(.+)",
        r"Decided:\s*(.+)",
        r"Chose:\s*(.+)",
        r"(?:→|->)\s*(.+)",
        r"(?:•|-)\s*(.+)",
    ]

    for line in content.splitlines()[-50:]:
        for pattern in patterns:
            match = re.search(pattern, line.strip())
            if match and len(match.group(1)) > 10:
                decisions.append(match.group(1)[:100])
                if len(decisions) >= limit:
                    return decisions

    return decisions


def save_state(state_dir: Path, state: dict) -> None:
    state_file = state_dir / "pre-compact-state.json"
    state["timestamp"] = datetime.now().isoformat()
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except OSError:
        pass


def append_to_session_log(project_dir: str, trigger: str) -> None:
    logs_dir = Path(project_dir) / "docs/work" / "session_logs"
    if not logs_dir.exists():
        return

    log_files = sorted(logs_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not log_files:
        return

    try:
        with open(log_files[0], "a", encoding="utf-8") as handle:
            handle.write("\n\n---\n")
            handle.write(f"**Context compaction ({trigger}) at {datetime.now().strftime('%H:%M')}**\n")
            handle.write("Check git status/log and docs/work/plans/ for current state.\n")
    except OSError:
        pass


def format_compaction_message(plan_info: dict | None, decisions: list[str]) -> str:
    lines = [f"\n{YELLOW}⚡ Context compaction starting{NC}", ""]

    if plan_info:
        lines.append(f"{GREEN}Current state saved:{NC}")
        lines.append(f"  Plan: {plan_info['plan_name']} ({plan_info['status']})")
        if plan_info.get("current_task"):
            lines.append(f"  Next task: {plan_info['current_task']}")

    if decisions:
        lines.append("")
        lines.append(f"{GREEN}Recent decisions captured:{NC}")
        for d in decisions:
            lines.append(f"  • {d[:80]}...")

    lines.append("")
    lines.append(f"{CYAN}State will be restored after compaction.{NC}")
    lines.append("")

    return "\n".join(lines)


def summarize(plan_info: dict | None, decisions: list[str]) -> str:
    lines = ["Pre-compact state saved."]
    if plan_info:
        lines.append(f"Active plan: {plan_info['plan_name']} ({plan_info['status']}).")
        if plan_info.get("current_task"):
            lines.append(f"Next unchecked task: {plan_info['current_task']}.")
    if decisions:
        lines.append("Recent decisions: " + "; ".join(decisions[:3]))
    return " ".join(lines)


def main() -> int:
    hook_input = read_hook_input()
    project_dir = project_dir_from(hook_input)
    if not project_dir:
        return 0

    trigger = hook_input.get("trigger", "auto")
    plan_info = find_active_plan(project_dir)
    decisions = extract_recent_decisions(project_dir)

    state = {
        "trigger": trigger,
        "project_dir": project_dir,
        "plan_path": plan_info["plan_path"] if plan_info else None,
        "plan_status": plan_info["status"] if plan_info else None,
        "current_task": plan_info.get("current_task") if plan_info else None,
        "decisions": decisions,
    }

    state_dir = get_state_dir(project_dir)
    save_state(state_dir, state)
    append_to_session_log(project_dir, str(trigger))

    print(format_compaction_message(plan_info, decisions), file=sys.stderr)
    json.dump({"systemMessage": summarize(plan_info, decisions)}, sys.stdout)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
