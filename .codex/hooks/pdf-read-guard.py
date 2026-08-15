#!/usr/bin/env python3
"""
Block direct reads of source PDFs so agents classify and convert them first.

This hook is intentionally narrow: it only blocks Read tool calls for PDFs under
docs/sources/. Compiled PDFs and visual QA artifacts elsewhere remain readable.
"""

from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path


def read_hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}


def project_dir_from(hook_input: dict) -> Path:
    cwd = hook_input.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd).expanduser().resolve()

    for name in ("CODEX_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PWD"):
        value = os.environ.get(name)
        if value:
            return Path(value).expanduser().resolve()

    return Path.cwd().resolve()


def requested_path(hook_input: dict) -> Path | None:
    tool_input = hook_input.get("tool_input")
    if not isinstance(tool_input, dict):
        return None

    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return Path(value).expanduser()

    return None


def relative_to_project(path: Path, project_dir: Path) -> Path:
    absolute = path if path.is_absolute() else project_dir / path
    try:
        return absolute.resolve().relative_to(project_dir)
    except ValueError:
        return absolute.resolve()


def is_source_pdf(relative_path: Path) -> bool:
    parts = relative_path.parts
    return (
        len(parts) >= 3
        and parts[0] == "docs"
        and parts[1] == "sources"
        and relative_path.suffix.lower() == ".pdf"
    )


def block_message(relative_path: Path) -> str:
    md_path = relative_path.with_suffix(".md")
    command = (
        "uv run python code/03_quality/pdf_to_markdown.py "
        f"{shlex.quote(str(relative_path))} --output {shlex.quote(str(md_path))}"
    )
    return (
        "Direct reads of source PDFs are blocked for this project. "
        "Create a Markdown version with Firecrawl pdf-inspector and read that "
        "instead:\n\n"
        f"  {command}\n\n"
        "If visual/layout information is essential, inspect the original PDF or "
        "page images as a supplement and state why Markdown is insufficient."
    )


def main() -> int:
    hook_input = read_hook_input()
    tool_name = hook_input.get("tool_name")
    if tool_name != "Read":
        return 0

    path = requested_path(hook_input)
    if path is None:
        return 0

    project_dir = project_dir_from(hook_input)
    relative_path = relative_to_project(path, project_dir)
    if not is_source_pdf(relative_path):
        return 0

    print(block_message(relative_path), file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
