#!/usr/bin/env python3
"""
Generate .codex/agents/*.toml from .claude/agents/*.md.

Claude subagents are the canonical source: YAML frontmatter (name,
description, optional tools/model/effort) plus a markdown body. Codex model
and effort defaults are set for the implementer. A tool-boundary paragraph
carries the Claude tool restriction into Codex as guidance.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CLAUDE_AGENTS = Path(".claude/agents")
CODEX_AGENTS = Path(".codex/agents")
GENERATED_HEADER = "# GENERATED — do not edit. Source: .claude/agents/{name}.md. Run: make agents\n"
CODEX_DEFAULTS = {"implementer": ("gpt-6-luna", "xhigh")}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        raise ValueError("missing frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("malformed frontmatter")
    fm: dict[str, str] = {}
    for line in parts[1].splitlines():
        m = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    body = parts[2].lstrip("\n").rstrip() + "\n"
    return fm, body


def tool_boundary_paragraph(tools_raw: str) -> str:
    tools = [t.strip() for t in tools_raw.split(",") if t.strip()]
    if not tools:
        return ""
    lines = [f"This role is scoped to: {', '.join(tools)}."]
    if "Write" not in tools and "Edit" not in tools:
        lines.append("Do not create, edit, or delete files.")
    if "Bash" not in tools:
        lines.append("Do not run shell commands.")
    if "Task" not in tools:
        lines.append("Do not delegate to other agents or subagents.")
    return "## Tool Boundary (generated)\n\n" + " ".join(lines) + "\n"


def escape_toml_basic_multiline(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace('"""', '\\"""')
    return text


def generate_toml(md_path: Path) -> str:
    fm, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
    name = fm.get("name", md_path.stem)
    description = fm.get("description", "")
    tools = fm.get("tools", "")

    boundary = tool_boundary_paragraph(tools)
    full_body = body.rstrip()
    if boundary:
        full_body = full_body + "\n\n" + boundary.rstrip()

    escaped_description = escape_toml_basic_multiline(description).replace('"', '\\"')
    escaped_body = escape_toml_basic_multiline(full_body)

    header = GENERATED_HEADER.format(name=name)
    model_lines = ""
    if name in CODEX_DEFAULTS:
        model, effort = CODEX_DEFAULTS[name]
        model_lines = f'model = "{model}"\nmodel_reasoning_effort = "{effort}"\n'
    return (
        f"{header}"
        f'description = "{escaped_description}"\n'
        f'developer_instructions = """\n{escaped_body}"""\n'
        f"{model_lines}"
        f'name = "{name}"\n'
    )


def strip_header(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if lines and lines[0].startswith("# GENERATED"):
        return "".join(lines[1:])
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate .codex/agents/*.toml from .claude/agents/*.md")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root")
    parser.add_argument("--check", action="store_true", help="Verify freshness without writing")
    args = parser.parse_args()
    root = args.root.resolve()

    claude_dir = root / CLAUDE_AGENTS
    codex_dir = root / CODEX_AGENTS
    if not claude_dir.is_dir():
        print(f"[ERROR] {CLAUDE_AGENTS} not found", file=sys.stderr)
        return 2

    codex_dir.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    written = 0

    for md_path in sorted(claude_dir.glob("*.md")):
        generated = generate_toml(md_path)
        toml_path = codex_dir / f"{md_path.stem}.toml"

        if args.check:
            if not toml_path.is_file() or strip_header(toml_path.read_text(encoding="utf-8")) != strip_header(generated):
                stale.append(md_path.stem)
            continue

        toml_path.write_text(generated, encoding="utf-8")
        written += 1

    expected = {path.stem for path in claude_dir.glob("*.md")}
    for toml_path in codex_dir.glob("*.toml"):
        if toml_path.stem in expected:
            continue
        if not toml_path.read_text(encoding="utf-8").startswith("# GENERATED"):
            continue
        if args.check:
            stale.append(toml_path.stem)
        else:
            toml_path.unlink()

    if args.check:
        if stale:
            for name in stale:
                print(f"[ERROR] .codex/agents/{name}.toml is stale relative to .claude/agents/{name}.md")
            print(f"Agent generation: {len(stale)} stale file(s). Run 'make agents' to regenerate.")
            return 2
        print("Agent generation: PASS (all .codex/agents/*.toml up to date)")
        return 0

    print(f"Generated {written} file(s) in {CODEX_AGENTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
