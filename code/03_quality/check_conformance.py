#!/usr/bin/env python3
"""Check that the small Claude Code and Codex project setup stays aligned."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = {
    "unslop", "open-issue", "to-spec", "grill-to-spec", "implement",
    "code-review", "ship", "close-issue", "sitrep", "teach", "handoff",
    "discover", "write-paper", "review-paper", "write-slides",
    "review-slides", "coding-r", "coding-python", "coding-julia",
}
FRONTMATTER_FIELDS = {
    "name", "description", "disable-model-invocation", "allowed-tools",
    "license", "compatibility", "metadata", "argument-hint",
}


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter marker")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing frontmatter marker") from error
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line or line[0].isspace():
            raise ValueError(f"unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"\'')
    return fields


def check() -> list[str]:
    problems: list[str] = []
    canonical = ROOT / ".agents/skills"
    claude = ROOT / ".claude/skills"
    actual = {p.name for p in canonical.iterdir() if p.is_dir()}
    actual_links = {p.name for p in claude.iterdir() if p.is_symlink() or p.is_dir()}
    for missing in sorted(SKILLS - actual):
        problems.append(f"missing skill: {missing}")
    for extra in sorted(actual - SKILLS):
        problems.append(f"retired skill still present: {extra}")
    for name in sorted(actual):
        file = canonical / name / "SKILL.md"
        if not file.is_file():
            problems.append(f"missing {file.relative_to(ROOT)}")
            continue
        try:
            fields = frontmatter(file)
        except ValueError as error:
            problems.append(f"{file.relative_to(ROOT)}: {error}")
            continue
        if fields.get("name") != name:
            problems.append(f"{file.relative_to(ROOT)}: name does not match directory")
        if not fields.get("description"):
            problems.append(f"{file.relative_to(ROOT)}: missing description")
        extra_fields = fields.keys() - FRONTMATTER_FIELDS
        if extra_fields:
            problems.append(f"{file.relative_to(ROOT)}: unsupported fields {sorted(extra_fields)}")
        disabled = fields.get("disable-model-invocation") == "true"
        if name == "unslop" and disabled:
            problems.append("unslop must remain model-invoked")
        if name != "unslop" and not disabled:
            problems.append(f"{name} must require Leo's invocation")
        link = claude / name
        if not link.is_symlink() or link.resolve() != (canonical / name).resolve():
            problems.append(f"Claude skill link is missing or wrong: {name}")
    for extra in sorted(actual_links - actual):
        problems.append(f"stale Claude skill link: {extra}")

    claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    if "@AGENTS.md" not in claude_md.splitlines() or len(claude_md.splitlines()) > 12:
        problems.append("CLAUDE.md must be a thin @AGENTS.md import")
    if (ROOT / ".claude/rules").exists():
        problems.append("old auto-loaded .claude/rules directory remains")

    implementer = ROOT / ".claude/agents/implementer.md"
    try:
        agent_fields = frontmatter(implementer)
    except (OSError, ValueError) as error:
        problems.append(f"invalid Claude implementer agent: {error}")
    else:
        if agent_fields.get("model") != "sonnet" or agent_fields.get("effort") != "xhigh":
            problems.append("Claude implementer must default to Sonnet at xhigh effort")

    for config in (ROOT / ".claude/settings.json", ROOT / ".codex/hooks.json"):
        try:
            hooks = json.loads(config.read_text(encoding="utf-8")).get("hooks", {})
        except (OSError, json.JSONDecodeError) as error:
            problems.append(f"invalid {config.relative_to(ROOT)}: {error}")
            continue
        if set(hooks) != {"PreToolUse"} or len(hooks["PreToolUse"]) != 1:
            problems.append(f"{config.relative_to(ROOT)} must have only one PreToolUse guard")
            continue
        commands = [h.get("command", "") for h in hooks["PreToolUse"][0].get("hooks", [])]
        if len(commands) != 1 or "guard_raw_data.py" not in commands[0]:
            problems.append(f"{config.relative_to(ROOT)} does not use the shared raw-data guard")

    result = subprocess.run(
        [sys.executable, str(ROOT / "code/03_quality/gen_codex_agents.py"), "--root", str(ROOT), "--check"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        problems.append(result.stdout.strip() or result.stderr.strip() or "Codex agents are stale")
    return problems


def main() -> int:
    problems = check()
    if problems:
        for problem in problems:
            print(f"[ERROR] {problem}")
        return 1
    print("Cross-harness setup: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
