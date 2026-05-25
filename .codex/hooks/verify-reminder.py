#!/usr/bin/env python3
"""
Verification reminder for Codex file edits.

Runs as a PostToolUse hook for file-edit tools. For Codex, apply_patch reports
edited files through tool_input.command, so this script extracts paths from
patch headers in addition to legacy file_path fields.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

VERIFY_EXTENSIONS = {
    ".tex": "run make articles, make slides, or make latex as appropriate",
    ".R": "run the affected stage script or Make target",
    ".py": "execute the affected script or pipeline target",
    ".ipynb": "execute the notebook via the analysis target",
}

VERIFY_FILENAMES = {
    "Makefile": "run make help and the relevant stage target",
}

SKIP_EXTENSIONS = {
    ".md",
    ".txt",
    ".rst",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".lock",
    ".env",
    ".gitignore",
    ".svg",
    ".png",
    ".jpg",
    ".pdf",
    ".bib",
    ".cls",
    ".sty",
}

SKIP_PARTS = {
    "docs/work/templates",
    "docs/work/reviews",
    ".claude",
    ".codex",
    ".agents/skills",
    "node_modules",
    "build",
    "dist",
}


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


def normalize_path(path: str, project_dir: str) -> str:
    if not path:
        return ""
    path_obj = Path(path)
    if path_obj.is_absolute() and project_dir:
        try:
            return str(path_obj.relative_to(project_dir))
        except ValueError:
            return str(path_obj)
    return str(path_obj)


def extract_patch_paths(command: str) -> list[str]:
    if not command:
        return []
    paths: list[str] = []
    for line in command.splitlines():
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def edited_paths(hook_input: dict) -> list[str]:
    project_dir = project_dir_from(hook_input)
    tool_input = hook_input.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return []

    candidates: list[str] = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            candidates.append(value)

    command = tool_input.get("command")
    if isinstance(command, str):
        candidates.extend(extract_patch_paths(command))

    normalized = [normalize_path(path, project_dir) for path in candidates]
    return list(dict.fromkeys(path for path in normalized if path))


def should_skip(file_path: str) -> bool:
    path = Path(file_path)

    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True

    path_text = str(path)
    if any(part in path_text for part in SKIP_PARTS):
        return True

    name = path.name.lower()
    return name.startswith("test_") or name.endswith("_test.py")


def needs_verification(file_path: str) -> tuple[bool, str]:
    path = Path(file_path)
    suffix = path.suffix

    if suffix in VERIFY_EXTENSIONS:
        return True, VERIFY_EXTENSIONS[suffix]

    if path.name in VERIFY_FILENAMES:
        return True, VERIFY_FILENAMES[path.name]

    return False, ""


def was_recently_reminded(session_dir: Path, file_path: str) -> bool:
    cache_file = session_dir / "verify-reminder-cache.json"

    try:
        cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    except (json.JSONDecodeError, OSError):
        cache = {}

    last_reminder = cache.get(file_path, 0)
    now = time.time()

    cache[file_path] = now
    cache = {k: v for k, v in cache.items() if now - v < 300}

    try:
        cache_file.write_text(json.dumps(cache))
    except OSError:
        pass

    return (now - last_reminder) < 60


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
    project_dir = project_dir_from(hook_input)
    session_dir = get_session_dir(project_dir)

    reminders: list[str] = []
    for file_path in edited_paths(hook_input):
        if should_skip(file_path):
            continue

        needs_verify, action = needs_verification(file_path)
        if not needs_verify or was_recently_reminded(session_dir, file_path):
            continue

        reminders.append(f"{file_path}: {action}")

    if not reminders:
        return 0

    return post_tool_context(
        "Verification reminder after file edit. Before marking the task complete, "
        + "; ".join(reminders[:3])
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
