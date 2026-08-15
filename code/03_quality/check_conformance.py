#!/usr/bin/env python3
"""
Validate cross-harness parity between Claude Code and Codex configuration.

The checker is intentionally conservative: it verifies structural invariants
(symlinks resolve, frontmatter is spec-compliant, generated files are fresh,
references aren't dangling) rather than judging content quality.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CLAUDE_SKILLS = Path(".claude/skills")
AGENTS_SKILLS = Path(".agents/skills")
CLAUDE_RULES = Path(".claude/rules")
CLAUDE_AGENTS = Path(".claude/agents")
CODEX_AGENTS = Path(".codex/agents")
SHARED_HOOKS = Path(".agents/hooks")
CLAUDE_HOOKS = Path(".claude/hooks")
CODEX_HOOKS = Path(".codex/hooks")
CLAUDE_SETTINGS = Path(".claude/settings.json")
CODEX_HOOKS_JSON = Path(".codex/hooks.json")
CLAUDE_MD = Path("CLAUDE.md")
AGENTS_MD = Path("AGENTS.md")

SPEC_SKILL_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
PORTABLE_HOOK_EVENTS = {
    "PreToolUse", "PostToolUse", "UserPromptSubmit", "SessionStart", "SessionEnd",
    "Stop", "PreCompact", "PostCompact", "SubagentStart", "SubagentStop",
    "PermissionRequest",
}
HOOK_EVENT_ALLOWLIST = {"Notification"}
DOC_REF_PATTERN = re.compile(r"\.claude/(rules|references)/([\w-]+\.md)")
IGNORED_NAMES = {".gitkeep", ".DS_Store", "__pycache__"}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".toml", ".json", ".tex", ".txt", ""}


@dataclass
class Finding:
    severity: str
    message: str


def parse_frontmatter_scalar(raw: str) -> str:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def parse_frontmatter(body: str) -> dict[str, Any]:
    """Minimal parser for the flat key: value / key: [list] / key:\\n  - item /
    key: | block-scalar shapes actually used in this repo's frontmatter. Not a
    general YAML parser -- sufficient for validating keys and simple values."""
    fm: dict[str, Any] = {}
    lines = body.splitlines()
    i = 0
    current_key: str | None = None
    while i < len(lines):
        line = lines[i]
        top_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", line)
        if top_match:
            key, rest = top_match.group(1), top_match.group(2)
            current_key = key
            if rest in ("|", ">", "|-", ">-", ""):
                # Block scalar or empty-then-list; collect indented continuation lines.
                collected: list[str] = []
                items: list[str] = []
                j = i + 1
                while j < len(lines) and (lines[j].startswith(" ") or lines[j].strip() == ""):
                    stripped = lines[j].strip()
                    if stripped.startswith("- "):
                        items.append(parse_frontmatter_scalar(stripped[2:]))
                    elif stripped:
                        collected.append(stripped)
                    j += 1
                if items:
                    fm[key] = items
                elif collected:
                    fm[key] = " ".join(collected)
                else:
                    fm[key] = None
                i = j
                continue
            if rest.startswith("["):
                inner = rest.strip("[]")
                fm[key] = [parse_frontmatter_scalar(v) for v in inner.split(",") if v.strip()]
            else:
                fm[key] = parse_frontmatter_scalar(rest)
            i += 1
            continue
        i += 1
    return fm


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return parse_frontmatter(parts[1]), parts[2]


def check_skills_symlinked(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    claude_dir = root / CLAUDE_SKILLS
    agents_dir = root / AGENTS_SKILLS

    if not agents_dir.is_dir():
        findings.append(Finding("error", f"{AGENTS_SKILLS} does not exist (canonical skills location missing)"))
        return findings
    if not claude_dir.is_dir():
        findings.append(Finding("error", f"{CLAUDE_SKILLS} does not exist"))
        return findings

    claude_names = {p.name for p in claude_dir.iterdir() if p.is_dir() or p.is_symlink()}
    agents_names = {p.name for p in agents_dir.iterdir() if p.is_dir()}

    for missing in sorted(agents_names - claude_names):
        findings.append(Finding("error", f"{AGENTS_SKILLS}/{missing} has no corresponding {CLAUDE_SKILLS}/{missing}"))
    for extra in sorted(claude_names - agents_names):
        findings.append(Finding("error", f"{CLAUDE_SKILLS}/{extra} has no corresponding {AGENTS_SKILLS}/{extra}"))

    for name in sorted(claude_names & agents_names):
        link = claude_dir / name
        if not link.is_symlink():
            findings.append(Finding("error", f"{CLAUDE_SKILLS}/{name} is not a symlink"))
            continue
        target = Path(link.readlink()) if hasattr(link, "readlink") else Path(link.resolve())
        if target.is_absolute():
            findings.append(Finding("warning", f"{CLAUDE_SKILLS}/{name} symlink target is absolute (should be relative for portability)"))
        resolved = (link.parent / target).resolve()
        expected = (agents_dir / name).resolve()
        if resolved != expected:
            findings.append(Finding("error", f"{CLAUDE_SKILLS}/{name} symlink resolves to {resolved}, expected {expected}"))
        if not (link / "SKILL.md").is_file():
            findings.append(Finding("error", f"{CLAUDE_SKILLS}/{name}/SKILL.md not found through symlink"))

    return findings


def check_claude_md_stub(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    path = root / CLAUDE_MD
    if not path.is_file():
        findings.append(Finding("error", f"{CLAUDE_MD} does not exist"))
        return findings
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^@AGENTS\.md\s*$", text, re.MULTILINE):
        findings.append(Finding("error", f"{CLAUDE_MD} does not import @AGENTS.md"))
    line_count = len(text.splitlines())
    if line_count > 20:
        findings.append(Finding("warning", f"{CLAUDE_MD} is {line_count} lines; expected a thin stub (<=20 lines)"))
    return findings


def check_hooks_consolidated(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for legacy in (CLAUDE_HOOKS, CODEX_HOOKS):
        if (root / legacy).exists():
            findings.append(Finding("error", f"{legacy} still exists; hooks should live only in {SHARED_HOOKS}"))

    import json

    for config_path, key in ((CLAUDE_SETTINGS, "hooks"), (CODEX_HOOKS_JSON, "hooks")):
        full = root / config_path
        if not full.is_file():
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(Finding("error", f"{config_path} is not valid JSON: {exc}"))
            continue
        hooks = data.get(key, {})
        for event_name, entries in hooks.items():
            if event_name not in PORTABLE_HOOK_EVENTS and event_name not in HOOK_EVENT_ALLOWLIST:
                findings.append(Finding("warning", f"{config_path}: hook event '{event_name}' is not in the portable intersection"))
            for entry in entries:
                for hook in entry.get("hooks", []):
                    command = hook.get("command", "")
                    if str(SHARED_HOOKS) not in command:
                        findings.append(Finding("error", f"{config_path}: hook command does not reference {SHARED_HOOKS}: {command!r}"))
    return findings


def check_skill_frontmatter(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents_dir = root / AGENTS_SKILLS
    if not agents_dir.is_dir():
        return findings
    for skill_dir in sorted(agents_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm, _ = split_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm is None:
            findings.append(Finding("error", f"{skill_md.relative_to(root)}: missing or unparsable frontmatter"))
            continue
        extra = set(fm.keys()) - SPEC_SKILL_FIELDS
        if extra:
            findings.append(Finding("error", f"{skill_md.relative_to(root)}: non-spec frontmatter field(s) {sorted(extra)}"))
        if fm.get("name") != skill_dir.name:
            findings.append(Finding("warning", f"{skill_md.relative_to(root)}: name '{fm.get('name')}' != directory '{skill_dir.name}'"))
        if not fm.get("description"):
            findings.append(Finding("error", f"{skill_md.relative_to(root)}: description is empty"))
    return findings


def check_agents_generated(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    gen_script = root / "code/03_quality/gen_codex_agents.py"
    if not gen_script.is_file():
        findings.append(Finding("warning", "gen_codex_agents.py not found; skipping agent freshness check"))
        return findings

    import subprocess

    result = subprocess.run(
        [sys.executable, str(gen_script), "--check", "--root", str(root)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        for line in result.stdout.splitlines() + result.stderr.splitlines():
            if line.strip():
                findings.append(Finding("error", f"gen_codex_agents.py --check: {line.strip()}"))
        if not findings:
            findings.append(Finding("error", "gen_codex_agents.py --check failed with no output"))

    claude_names = {p.stem for p in (root / CLAUDE_AGENTS).glob("*.md")} if (root / CLAUDE_AGENTS).is_dir() else set()
    codex_names = {p.stem for p in (root / CODEX_AGENTS).glob("*.toml")} if (root / CODEX_AGENTS).is_dir() else set()
    for missing in sorted(claude_names - codex_names):
        findings.append(Finding("error", f"{CODEX_AGENTS}/{missing}.toml missing (source: {CLAUDE_AGENTS}/{missing}.md)"))
    for extra in sorted(codex_names - claude_names):
        findings.append(Finding("error", f"{CODEX_AGENTS}/{extra}.toml has no corresponding {CLAUDE_AGENTS}/{extra}.md"))
    for name in codex_names:
        toml_path = root / CODEX_AGENTS / f"{name}.toml"
        try:
            tomllib.loads(toml_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            findings.append(Finding("error", f"{toml_path.relative_to(root)}: invalid TOML: {exc}"))

    return findings


def check_rules_path_scoped(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    rules_dir = root / CLAUDE_RULES
    if not rules_dir.is_dir():
        return findings
    for rule in sorted(rules_dir.glob("*.md")):
        fm, _ = split_frontmatter(rule.read_text(encoding="utf-8"))
        if not fm or "paths" not in fm:
            findings.append(Finding("error", f"{rule.relative_to(root)}: no 'paths:' frontmatter (every rule should be path-scoped)"))
        elif not fm.get("paths"):
            findings.append(Finding("error", f"{rule.relative_to(root)}: 'paths:' frontmatter is empty"))
    return findings


def check_dangling_references(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    rules_dir = root / CLAUDE_RULES
    existing_rules = {p.name for p in rules_dir.glob("*.md")} if rules_dir.is_dir() else set()
    references_dir = root / ".claude/references"
    existing_references = {p.name for p in references_dir.glob("*.md")} if references_dir.is_dir() else set()

    skip_dirs = {".git", "__pycache__", ".venv", "node_modules"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for match in DOC_REF_PATTERN.finditer(text):
            kind, name = match.group(1), match.group(2)
            pool = existing_rules if kind == "rules" else existing_references
            if name not in pool:
                rel = path.relative_to(root)
                findings.append(Finding("error", f"{rel}: references .claude/{kind}/{name}, which does not exist"))
    return findings


def check_rules_index_current(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents_md = root / AGENTS_MD
    rules_dir = root / CLAUDE_RULES
    if not agents_md.is_file() or not rules_dir.is_dir():
        return findings
    text = agents_md.read_text(encoding="utf-8")
    existing_rules = {p.name for p in rules_dir.glob("*.md")}
    for rule_name in sorted(existing_rules):
        if rule_name not in text:
            findings.append(Finding("warning", f"{AGENTS_MD}: Rules Index does not mention {rule_name}"))
    return findings


def check_rule_injector_registration(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    injector = root / SHARED_HOOKS / "rule-injector.py"
    if not injector.is_file():
        return findings

    import json

    codex_path = root / CODEX_HOOKS_JSON
    claude_path = root / CLAUDE_SETTINGS

    def references_injector(config_path: Path) -> bool:
        if not config_path.is_file():
            return False
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False
        hooks = data.get("hooks", {})
        for entries in hooks.values():
            for entry in entries:
                for hook in entry.get("hooks", []):
                    if "rule-injector.py" in hook.get("command", ""):
                        return True
        return False

    if not references_injector(codex_path):
        findings.append(Finding("error", f"rule-injector.py exists but is not registered in {CODEX_HOOKS_JSON}"))
    if references_injector(claude_path):
        findings.append(Finding("error", f"rule-injector.py must not be registered in {CLAUDE_SETTINGS} (Claude already auto-loads rules; this would double-inject)"))
    return findings


def print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("Conformance: PASS")
        return
    for finding in findings:
        print(f"[{finding.severity.upper()}] {finding.message}")
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warning")
    print(f"Conformance: {errors} error(s), {warnings} warning(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate cross-harness (Claude Code / Codex) parity.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root")
    args = parser.parse_args()
    root = args.root.resolve()

    findings: list[Finding] = []
    findings.extend(check_skills_symlinked(root))
    findings.extend(check_skill_frontmatter(root))
    findings.extend(check_claude_md_stub(root))
    findings.extend(check_hooks_consolidated(root))
    findings.extend(check_agents_generated(root))
    findings.extend(check_rules_path_scoped(root))
    findings.extend(check_dangling_references(root))
    findings.extend(check_rules_index_current(root))
    findings.extend(check_rule_injector_registration(root))

    print_findings(findings)
    return 2 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
