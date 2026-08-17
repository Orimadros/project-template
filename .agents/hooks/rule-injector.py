#!/usr/bin/env python3
"""
Codex-only PostToolUse hook that gives Codex the path-scoped rule loading
Claude Code gets natively from .claude/rules/*.md `paths:` frontmatter.
Codex has no equivalent mechanism, so this hook reads the same frontmatter,
matches it against the file the agent just touched, and injects the
matching rule body via additionalContext.

Registered in .codex/hooks.json ONLY -- Claude Code already auto-loads
.claude/rules/, so registering this on the Claude side would double-inject
every rule (see check_conformance.py C12).

Fail-safe by design: any unexpected error results in no injection, never a
blocked tool call. Set INJECT_CONTEXT = False below to run in observe-only
mode (matches are computed and logged, nothing is surfaced to the agent) --
useful for a first cautious run in a real Codex session before trusting
this fully.

Must be registered in the SAME PostToolUse block as every other hook that
shares its matcher (see .codex/hooks.json). Confirmed live 2026-08-17: when
this script had its own block with a matcher overlapping an earlier block's
(both matching Edit/Write/apply_patch), it never executed once across a
full Codex session -- state evidence (no rules-index.json ever written)
showed the sibling block's hooks ran normally while this one silently did
not. Codex's rule for resolving overlapping matchers across blocks on one
event is unverified; collapsing to one block per event is the fix, and
check_conformance.py's check_codex_matchers_non_overlapping guards against
this regressing.
"""

from __future__ import annotations

import fnmatch  # noqa: F401  (not used for matching; kept off the hot path intentionally -- see glob_to_regex)
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

INJECT_CONTEXT = True

RULES_DIR = Path(".claude/rules")
BUDGET_PER_EVENT = 6000
SESSION_CAP = 30000
DEDUP_THROTTLE_SECONDS = 600  # fallback when session_id can't be resolved


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


def state_root() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state")) / "agent-hooks"


def get_project_state_dir(project_dir: str) -> Path:
    project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:8] if project_dir else "default"
    state_dir = state_root() / project_hash
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def session_id_from(hook_input: dict) -> str | None:
    for key in ("session_id", "conversation_id"):
        value = hook_input.get(key)
        if isinstance(value, str) and value:
            return value
    env_value = os.environ.get("CODEX_SESSION_ID")
    if env_value:
        return env_value
    transcript = hook_input.get("transcript_path")
    if isinstance(transcript, str) and transcript:
        return hashlib.md5(transcript.encode()).hexdigest()[:12]
    return None


def get_session_dir(project_state_dir: Path, session_id: str) -> Path:
    session_dir = project_state_dir / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


# --- Glob matching -----------------------------------------------------
# Purpose-built, not a general glob engine: scoped to the shapes actually
# used in .claude/rules/*.md (no character classes, no "?"). "**" matches
# zero or more path segments, including zero -- stdlib fnmatch does not
# support this (it requires a literal separator around "**" to still be
# present in the path), which would silently miss e.g. "code/**/*.R"
# matching "code/foo.R" with no intermediate directory.

def glob_to_regex(glob: str) -> re.Pattern:
    regex = ""
    i = 0
    while i < len(glob):
        if glob[i : i + 3] == "**/":
            regex += r"(?:.*/)?"
            i += 3
        elif glob[i : i + 2] == "**":
            regex += r".*"
            i += 2
        elif glob[i] == "*":
            regex += r"[^/]*"
            i += 1
        else:
            regex += re.escape(glob[i])
            i += 1
    return re.compile("^" + regex + "$")


def specificity(glob: str) -> tuple[int, int]:
    """(literal path segments before first wildcard, glob length) -- both descending."""
    parts = glob.split("/")
    literal_count = 0
    for part in parts:
        if "*" in part:
            break
        literal_count += 1
    return (literal_count, len(glob))


# --- Rules index ---------------------------------------------------------

def parse_frontmatter_paths(text: str) -> tuple[list[str], str]:
    """Return (globs, heading). Minimal parser scoped to this repo's rule
    frontmatter shape: `paths:` followed by `  - "glob"` list items."""
    if not text.startswith("---"):
        return [], ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return [], ""
    globs: list[str] = []
    in_paths = False
    for line in parts[1].splitlines():
        if re.match(r"^paths:\s*$", line):
            in_paths = True
            continue
        if in_paths:
            m = re.match(r'^\s*-\s*"?([^"]+)"?\s*$', line)
            if m:
                globs.append(m.group(1))
                continue
            if line.strip() and not line.startswith(" "):
                in_paths = False
    heading = ""
    for line in parts[2].splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            break
    return globs, heading


def build_index(root: Path) -> list[dict]:
    rules_dir = root / RULES_DIR
    index = []
    if not rules_dir.is_dir():
        return index
    for rule_path in sorted(rules_dir.glob("*.md")):
        text = rule_path.read_text(encoding="utf-8", errors="replace")
        globs, heading = parse_frontmatter_paths(text)
        if not globs:
            continue
        body = text.split("---", 2)[2].lstrip("\n") if text.startswith("---") else text
        index.append(
            {
                "name": rule_path.name,
                "globs": globs,
                "heading": heading or rule_path.stem,
                "body": body,
                "size": len(body),
            }
        )
    return index


def index_fingerprint(root: Path) -> tuple[int, int]:
    rules_dir = root / RULES_DIR
    if not rules_dir.is_dir():
        return (0, 0)
    files = list(rules_dir.glob("*.md"))
    if not files:
        return (0, 0)
    return (len(files), max(f.stat().st_mtime_ns for f in files))


def load_cached_index(project_state_dir: Path, root: Path) -> list[dict]:
    cache_path = project_state_dir / "rules-index.json"
    fingerprint = index_fingerprint(root)
    try:
        cached = json.loads(cache_path.read_text())
        if tuple(cached.get("fingerprint", [])) == fingerprint:
            return cached["rules"]
    except (json.JSONDecodeError, OSError, KeyError):
        pass

    rules = build_index(root)
    try:
        cache_path.write_text(json.dumps({"fingerprint": list(fingerprint), "rules": rules}))
    except OSError:
        pass
    return rules


# --- Touched-path extraction ---------------------------------------------

def extract_patch_paths(command: str) -> list[str]:
    paths = []
    for line in command.splitlines():
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def extract_bash_read_paths(command: str, project_dir: Path) -> list[str]:
    """Codex reads files through a shell tool, not a distinct file-read tool.
    Fuzzy: tokenize and keep tokens that resolve to an existing project file.
    False positives just cost one budgeted injection; false negatives are
    the failure mode this exists to reduce."""
    try:
        import shlex

        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    found = []
    for token in tokens:
        if token.startswith("-") or "/" not in token and "." not in token:
            continue
        candidate = (project_dir / token).resolve()
        try:
            candidate.relative_to(project_dir.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            found.append(token)
    return found


def touched_paths(hook_input: dict, project_dir: Path) -> list[str]:
    tool_input = hook_input.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return []

    raw: list[str] = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            raw.append(value)

    command = tool_input.get("command")
    if isinstance(command, str):
        raw.extend(extract_patch_paths(command))
        raw.extend(extract_bash_read_paths(command, project_dir))

    normalized = []
    for path in raw:
        p = Path(path)
        if p.is_absolute():
            try:
                p = p.resolve().relative_to(project_dir.resolve())
            except ValueError:
                continue
        normalized.append(p.as_posix())

    # Also add both symlink directions: some rules glob ".claude/skills/**"
    # only (the symlink path), others may see Codex report the already-
    # resolved ".agents/skills/..." real path directly. Forward-resolve via
    # the filesystem; reverse-map ".agents/skills/" -> ".claude/skills/" by
    # simple prefix substitution, since Step 6 fixed that exact mapping and
    # a real reverse-symlink lookup would mean scanning every skill symlink.
    resolved_variants = []
    for rel in normalized:
        full = project_dir / rel
        if full.is_symlink() or full.exists():
            try:
                resolved = full.resolve().relative_to(project_dir.resolve()).as_posix()
                if resolved != rel:
                    resolved_variants.append(resolved)
            except (ValueError, OSError):
                pass
        if rel.startswith(".agents/skills/"):
            resolved_variants.append(".claude/skills/" + rel[len(".agents/skills/") :])

    return list(dict.fromkeys(normalized + resolved_variants))


# --- Matching, ranking, budgeting -----------------------------------------

def matching_rules(index: list[dict], paths: list[str]) -> list[tuple[dict, tuple[int, int]]]:
    matched = []
    for rule in index:
        best = None
        for glob in rule["globs"]:
            pattern = glob_to_regex(glob)
            if any(pattern.match(p) for p in paths):
                spec = specificity(glob)
                if best is None or spec > best:
                    best = spec
        if best is not None:
            matched.append((rule, best))
    matched.sort(key=lambda item: (-item[1][0], -item[1][1], item[0]["name"]))
    return matched


def claim(session_dir: Path, rule_name: str) -> bool:
    mark_dir = session_dir / "rules"
    mark_dir.mkdir(parents=True, exist_ok=True)
    mark_path = mark_dir / f"{rule_name}.mark"
    try:
        fd = os.open(str(mark_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False


def read_session_total(session_dir: Path) -> int:
    try:
        return json.loads((session_dir / "injected-total.json").read_text()).get("total", 0)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return 0


def write_session_total(session_dir: Path, total: int) -> None:
    try:
        (session_dir / "injected-total.json").write_text(json.dumps({"total": total}))
    except OSError:
        pass


def throttled(project_state_dir: Path) -> bool:
    """Fallback path when session_id can't be resolved: time-based throttle
    instead of per-session dedup, since there is no session to key on."""
    marker = project_state_dir / "last-injection-no-session.json"
    now = time.time()
    try:
        last = json.loads(marker.read_text()).get("time", 0)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        last = 0
    if now - last < DEDUP_THROTTLE_SECONDS:
        return True
    try:
        marker.write_text(json.dumps({"time": now}))
    except OSError:
        pass
    return False


def compose(selected_full: list[dict], selected_pointer: list[dict]) -> str:
    parts = []
    for rule in selected_full:
        parts.append(f"# Rule: {rule['name']}\n\n{rule['body'].strip()}")
    if selected_pointer:
        pointer_lines = [f"- `.claude/rules/{r['name']}` — {r['heading']} (read before proceeding)" for r in selected_pointer]
        parts.append("Also applicable (read if relevant):\n" + "\n".join(pointer_lines))
    return "\n\n---\n\n".join(parts)


def post_tool_context(additional_context: str, summary: str) -> int:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": additional_context,
            },
            "systemMessage": summary,
        },
        sys.stdout,
    )
    return 0


def run() -> int:
    hook_input = read_hook_input()
    project_dir = Path(project_dir_from(hook_input) or ".").resolve()
    project_state_dir = get_project_state_dir(str(project_dir))

    index = load_cached_index(project_state_dir, project_dir)
    if not index:
        return 0

    paths = touched_paths(hook_input, project_dir)
    if not paths:
        return 0

    matches = matching_rules(index, paths)
    if not matches:
        return 0

    session_id = session_id_from(hook_input)
    if session_id is None:
        if throttled(project_state_dir):
            return 0
        session_dir = None
        session_total = 0
    else:
        session_dir = get_session_dir(project_state_dir, session_id)
        session_total = read_session_total(session_dir)

    unclaimed = []
    for rule, spec in matches:
        if session_dir is not None and not claim(session_dir, rule["name"]):
            continue  # already injected this session
        unclaimed.append(rule)

    if not unclaimed:
        return 0

    over_cap = session_total >= SESSION_CAP
    selected_full: list[dict] = []
    selected_pointer: list[dict] = []
    budget_used = 0

    for i, rule in enumerate(unclaimed):
        if i == 0 and not over_cap:
            selected_full.append(rule)
            budget_used += rule["size"]
            continue
        if not over_cap and budget_used + rule["size"] <= BUDGET_PER_EVENT:
            selected_full.append(rule)
            budget_used += rule["size"]
        else:
            selected_pointer.append(rule)

    if session_dir is not None:
        write_session_total(session_dir, session_total + budget_used)

    message = compose(selected_full, selected_pointer)
    if not message:
        return 0

    summary = f"Injected {len(selected_full)} rule(s) in full, {len(selected_pointer)} as pointer(s), for {', '.join(paths[:2])}."

    if not INJECT_CONTEXT:
        try:
            (project_state_dir / "rule-injector-debug.log").open("a").write(summary + "\n")
        except OSError:
            pass
        return 0

    return post_tool_context(message, summary)


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception:
        sys.exit(0)
