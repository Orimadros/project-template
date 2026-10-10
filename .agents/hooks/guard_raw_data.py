#!/usr/bin/env python3
"""Block direct edits to existing data/raw files in Claude Code and Codex hooks."""

from __future__ import annotations

import glob
import json
import re
import shlex
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EDIT_TOOLS = {"Edit", "Write", "apply_patch"}
SHELL_TOOLS = {"Bash", "exec_command"}
READ_COMMANDS = {"cat", "du", "file", "find", "head", "ls", "rg", "shasum", "stat", "tail", "wc"}
MUTATORS = re.compile(
    r"(?<![\w-])(rm|mv|cp|rsync|install|truncate|chmod|chown|chflags|touch|tee|"
    r"sed|perl|git\s+(?:checkout|restore|clean))\b|(?<!<)>|(?<!\w)-(?:delete|exec)\b"
)
PATCH_HEADER = re.compile(r"^\*\*\* (Add File|Update File|Delete File|Move to): (.+)$", re.MULTILINE)


def resolve_path(value: str, root: Path, cwd: Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else cwd / path).resolve()


def is_raw(path: Path, root: Path) -> bool:
    return path == root / "data/raw" or (root / "data/raw") in path.parents


def existing_raw_path(value: str, root: Path, cwd: Path) -> bool:
    path = resolve_path(value, root, cwd)
    if glob.has_magic(str(path)):
        return any(is_raw(Path(item).resolve(), root) for item in glob.glob(str(path)))
    return is_raw(path, root) and path.exists()


def check(payload: dict, root: Path = ROOT) -> str | None:
    root = root.resolve()
    name = payload.get("tool_name", "")
    data = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or root).resolve()

    if name in EDIT_TOOLS:
        for key in ("file_path", "path"):
            value = data.get(key)
            if isinstance(value, str) and existing_raw_path(value, root, cwd):
                return f"Existing raw file is append-only: {value}"
        patch = data.get("command") or data.get("patch") or data.get("input") or ""
        if isinstance(patch, str):
            for action, value in PATCH_HEADER.findall(patch):
                path = resolve_path(value, root, cwd)
                if is_raw(path, root) and (action != "Add File" or path.exists()):
                    return f"Existing raw file is append-only: {value}"
        return None

    if name in SHELL_TOOLS:
        command = data.get("command") or data.get("cmd") or ""
        if not isinstance(command, str) or "data/raw" not in command:
            return None
        try:
            tokens = shlex.split(command)
        except ValueError:
            tokens = command.split()
        refs = [token.strip(";|&<>\"'(),") for token in tokens if "data/raw" in token]
        refs.extend(re.findall(r"data/raw(?:/[A-Za-z0-9_./*?\[\]-]+)?", command))
        existing = any(existing_raw_path(token, root, cwd) for token in refs)
        if not existing and "data/raw" in command and MUTATORS.search(command):
            # The command might conceal a path behind a shell expression.
            existing = not refs
        if not existing:
            return None
        program = Path(tokens[0]).name if tokens else ""
        if program in READ_COMMANDS and not MUTATORS.search(command):
            return None
        return "Existing data/raw files are append-only; this command could change one."

    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    reason = check(payload)
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
