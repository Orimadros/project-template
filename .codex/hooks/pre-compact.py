#!/usr/bin/env python3
"""
Pre-compact state capture for Codex.

Runs before conversation compaction. It saves a small project state snapshot
under CODEX_HOME so the SessionStart compact/resume hook can restore useful
context after compaction.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime
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
    return os.environ.get("CODEX_PROJECT_DIR") or os.environ.get("PWD") or ""


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()


def get_session_dir(project_dir: str) -> Path:
    if project_dir:
        project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:8]
    else:
        project_hash = "default"
    session_dir = codex_home() / "sessions" / project_hash
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


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
        r"->\s*(.+)",
        r"-\s*(.+)",
    ]

    for line in content.splitlines()[-50:]:
        for pattern in patterns:
            match = re.search(pattern, line.strip())
            if match and len(match.group(1)) > 10:
                decisions.append(match.group(1)[:100])
                if len(decisions) >= limit:
                    return decisions

    return decisions


def save_state(session_dir: Path, state: dict) -> None:
    state_file = session_dir / "pre-compact-state.json"
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
            handle.write(f"**Codex context compaction ({trigger}) at {datetime.now().strftime('%H:%M')}**\n")
            handle.write("Check git status and docs/work/plans/ for current state.\n")
    except OSError:
        pass


def summarize(plan_info: dict | None, decisions: list[str]) -> str:
    lines = ["Codex pre-compact state saved."]
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

    session_dir = get_session_dir(project_dir)
    save_state(session_dir, state)
    append_to_session_log(project_dir, str(trigger))

    json.dump({"systemMessage": summarize(plan_info, decisions)}, sys.stdout)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
