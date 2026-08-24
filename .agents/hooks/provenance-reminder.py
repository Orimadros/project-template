#!/usr/bin/env python3
"""Asset Graph freshness reminder for shared agent hooks.

The graph itself is maintained manually. This hook never changes graph records;
the validator may update only the ignored local digest cache. It reports stale,
missing, moved, deleted, or structurally invalid governed records and steers the
agent to the provenance-ledger skill.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


GOVERNED_PREFIXES = (
    "code/00_fetch/",
    "code/01_build/",
    "code/02_analyze/",
    "code/99_explorations/",
    "data/",
    "results/",
)
PIPELINE_MAKE_RE = re.compile(r"\bmake\s+(?:fetch|build|analysis|all)\b")
MOVE_CODES = {
    "candidate-move",
    "candidate_move",
    "possible-move",
    "possible_move",
    "moved-path",
    "moved_path",
    "path-moved",
    "path_moved",
}
MAX_FINDINGS = 8


def read_hook_input() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def project_dir_from(hook_input: dict[str, Any]) -> Path:
    candidates = [
        hook_input.get("cwd"),
        os.environ.get("CLAUDE_PROJECT_DIR"),
        os.environ.get("CODEX_PROJECT_DIR"),
        os.environ.get("PWD"),
    ]
    for value in candidates:
        if not isinstance(value, str) or not value:
            continue
        start = Path(value).resolve()
        for candidate in (start, *start.parents):
            if (candidate / ".git").exists() or (candidate / "AGENTS.md").exists():
                return candidate
    return Path.cwd().resolve()


def extract_patch_paths(command: str) -> list[str]:
    paths: list[str] = []
    for line in command.splitlines():
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def normalize_path(raw_path: str, project_dir: Path, working_dir: Path) -> str:
    path = Path(raw_path)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(project_dir.resolve()).as_posix()
        except (OSError, ValueError):
            return path.as_posix()
    literal = path.as_posix().lstrip("./")
    if literal.startswith(GOVERNED_PREFIXES):
        return literal
    try:
        return (working_dir / path).resolve().relative_to(project_dir.resolve()).as_posix()
    except (OSError, ValueError):
        return literal


def touched_governed_surface(hook_input: dict[str, Any], project_dir: Path) -> bool:
    tool_input = hook_input.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return False

    paths: list[str] = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            paths.append(value)
    for key in ("file_paths", "paths"):
        value = tool_input.get(key)
        if isinstance(value, list):
            paths.extend(item for item in value if isinstance(item, str))

    workdir_value = tool_input.get("workdir") or hook_input.get("cwd")
    if isinstance(workdir_value, str) and workdir_value:
        raw_workdir = Path(workdir_value)
        working_dir = raw_workdir.resolve() if raw_workdir.is_absolute() else (project_dir / raw_workdir).resolve()
    else:
        working_dir = project_dir

    commands = [
        value
        for key in ("command", "cmd", "patch")
        if isinstance((value := tool_input.get(key)), str)
    ]
    try:
        relative_workdir = working_dir.relative_to(project_dir.resolve()).as_posix().rstrip("/") + "/"
    except ValueError:
        relative_workdir = ""
    if commands and relative_workdir.startswith(GOVERNED_PREFIXES):
        return True
    for command in commands:
        paths.extend(extract_patch_paths(command))
        if PIPELINE_MAKE_RE.search(command):
            return True
        normalized_command = command.replace("\\", "/")
        if any(prefix in normalized_command for prefix in GOVERNED_PREFIXES):
            return True

    return any(normalize_path(path, project_dir, working_dir).startswith(GOVERNED_PREFIXES) for path in paths)


def flatten_findings(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    findings = payload.get("findings")
    if isinstance(findings, list):
        return [item for item in findings if isinstance(item, dict)]
    combined: list[dict[str, Any]] = []
    for key in ("errors", "warnings"):
        values = payload.get(key)
        if isinstance(values, list):
            combined.extend(item for item in values if isinstance(item, dict))
    return combined


def stale_findings(payload: Any) -> list[dict[str, Any]]:
    return [finding for finding in flatten_findings(payload) if finding.get("stale") is True]


def actionable_findings(payload: Any) -> list[dict[str, Any]]:
    return [
        finding for finding in flatten_findings(payload)
        if finding.get("stale") is True or finding.get("severity") == "error"
    ]


def run_graph_check(project_dir: Path) -> tuple[list[dict[str, Any]], str | None]:
    cli = project_dir / "code/03_quality/asset_graph.py"
    if not cli.is_file():
        return [], "Asset Graph CLI is not available yet"

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(cli),
                "validate",
                "--format",
                "json",
                "--hook",
            ],
            cwd=project_dir,
            check=False,
            capture_output=True,
            text=True,
            timeout=25,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [], f"Asset Graph validation could not run: {exc}"

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        detail = (result.stderr or result.stdout).strip().splitlines()
        suffix = f": {detail[-1]}" if detail else ""
        return [], f"Asset Graph validation returned unreadable output{suffix}"

    return actionable_findings(payload), None


def describe_finding(finding: dict[str, Any]) -> str:
    code = str(finding.get("code") or "stale-record")
    path = finding.get("path")
    node_id = finding.get("node_id")
    message = str(finding.get("message") or code)

    identity = ""
    if isinstance(path, str) and path:
        identity = path
    if isinstance(node_id, str) and node_id:
        identity = f"{identity} [{node_id}]" if identity else node_id
    prefix = f"{identity}: " if identity else ""

    if code in MOVE_CODES or "move" in code:
        message += " Confirm identity before preserving the immutable ID."
    return f"{prefix}{message} ({code})"


def maintenance_message(findings: list[dict[str, Any]]) -> str:
    lines = [
        "ASSET GRAPH MAINTENANCE REQUIRED: use $provenance-ledger before relying on lineage. "
        "The graph covers only data code, data, and results; maintain identities "
        "and dependencies manually."
    ]
    codes = {str(item.get("code") or "") for item in findings}
    if "coverage_missing" in codes and "active_path_missing" in codes:
        lines.append(
            "- Possible move/rename: an old registered path is missing while a new "
            "governed path is uncovered. Compare content and Git history, then confirm "
            "identity before preserving the immutable ID."
        )
    lines.extend(f"- {describe_finding(item)}" for item in findings[:MAX_FINDINGS])
    if len(findings) > MAX_FINDINGS:
        lines.append(f"- ... and {len(findings) - MAX_FINDINGS} more stale finding(s)")
    lines.append("After review, run make provenance. Do not auto-discover or auto-write dependencies.")
    return "\n".join(lines)


def post_context(event: str, message: str) -> int:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": event,
                "additionalContext": message,
            },
            "systemMessage": "Asset Graph maintenance is required for governed data paths.",
        },
        sys.stdout,
    )
    return 0


def stop_directive(message: str) -> int:
    json.dump({"decision": "block", "reason": message}, sys.stdout)
    return 0


def main() -> int:
    hook_input = read_hook_input()
    event = str(hook_input.get("hook_event_name") or "PostToolUse")
    project_dir = project_dir_from(hook_input)

    if event == "PostToolUse" and not touched_governed_surface(hook_input, project_dir):
        return 0

    findings, error = run_graph_check(project_dir)
    if not findings:
        if error:
            message = (
                f"Asset Graph validation failure: {error}. Use $provenance-ledger and "
                "run make provenance before completion."
            )
            if event == "Stop":
                if hook_input.get("stop_hook_active", False):
                    return 0
                return stop_directive(message)
            return post_context(event, message)
        return 0

    message = maintenance_message(findings)
    if event == "Stop":
        if hook_input.get("stop_hook_active", False):
            return 0
        return stop_directive(message)
    return post_context(event, message)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Hooks must never damage or block the underlying tool operation.
        raise SystemExit(0)
