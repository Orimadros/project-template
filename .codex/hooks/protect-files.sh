#!/usr/bin/env bash
set -euo pipefail

# Block accidental edits to protected files and existing raw data.
# Codex file edits usually arrive as apply_patch with patch text in
# tool_input.command; legacy file_path/path fields are also supported.

INPUT="$(cat)"
TOOL="$(printf '%s' "$INPUT" | python3 -c 'import json, sys
try:
    print(json.load(sys.stdin).get("tool_name") or "")
except json.JSONDecodeError:
    print("")')"
CWD="$(printf '%s' "$INPUT" | python3 -c 'import json, sys
try:
    print(json.load(sys.stdin).get("cwd") or "")
except json.JSONDecodeError:
    print("")')"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "$CWD")"
export PROJECT_ROOT

extract_paths() {
  printf '%s' "$INPUT" | python3 -c '
import json
import re
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_input = data.get("tool_input") or {}
paths = []
for key in ("file_path", "path"):
    value = tool_input.get(key)
    if isinstance(value, str) and value:
        paths.append(value)

command = tool_input.get("command")
if isinstance(command, str):
    for line in command.splitlines():
        match = re.match(r"\*\*\* (Add|Update|Delete) File: (.+)$", line)
        if match:
            paths.append(f"{match.group(1).strip()}\t{match.group(2).strip()}")

for item in dict.fromkeys(paths):
    print(item)
'
}

PROTECTED_PATTERNS=(
  "docs/sources/references.bib"
  ".claude/references/domain-profile.md"
  ".claude/references/personal-style-guide.md"
  ".claude/references/journal-profiles.md"
  ".claude/settings.json"
  ".codex/config.toml"
)

protect_raw_permissions() {
  local raw_dir="$PROJECT_ROOT/data/raw"
  if [[ -d "$raw_dir" ]]; then
    find "$raw_dir" -type d -exec chmod u+rwx,go+rx {} + 2>/dev/null || true
    find "$raw_dir" -type f -exec chmod a-w {} + 2>/dev/null || true
    if command -v chflags >/dev/null 2>&1; then
      find "$raw_dir" -type f -exec chflags uchg {} + 2>/dev/null || true
    fi
  fi
}

is_raw_path() {
  local path="$1"
  [[ "$path" == "data/raw" || "$path" == data/raw/* ]]
}

is_meeting_path() {
  local path="$1"
  [[ "$path" == docs/work/meetings/* ]]
}

is_valid_meeting_path() {
  local path="$1"
  python3 - "$path" <<'PY'
from datetime import date
import re
import sys

match = re.fullmatch(
    r"docs/work/meetings/(\d{4}-\d{2}-\d{2})_([a-z0-9]+(?:-[a-z0-9]+)*)\.md",
    sys.argv[1],
)
if not match:
    raise SystemExit(1)

try:
    date.fromisoformat(match.group(1))
except ValueError:
    raise SystemExit(1)
PY
}

reject_invalid_meeting_paths_in_command() {
  printf '%s' "$INPUT" | python3 -c '
import json
from datetime import date
import re
import sys

try:
    command = (json.load(sys.stdin).get("tool_input") or {}).get("command")
except json.JSONDecodeError:
    raise SystemExit(0)

if not isinstance(command, str):
    raise SystemExit(0)

pattern = re.compile(r"(?:\./)?docs/work/meetings(?:/[^\s;|&<>\"\x27]*)?")
filename = re.compile(
    r"docs/work/meetings/(\d{4}-\d{2}-\d{2})_([a-z0-9]+(?:-[a-z0-9]+)*)\.md"
)
for candidate in pattern.findall(command):
    relative = candidate.removeprefix("./")
    if relative in {"docs/work/meetings", "docs/work/meetings/", "docs/work/meetings/.gitkeep"}:
        continue
    match = filename.fullmatch(relative)
    if match:
        try:
            date.fromisoformat(match.group(1))
        except ValueError:
            match = None
    if not match:
        print(
            "Meeting files must use docs/work/meetings/YYYY-MM-DD_topic-slug.md "
            "with a real date and lowercase hyphen-separated slug.",
            file=sys.stderr,
        )
        raise SystemExit(2)
'
}

is_mutating_raw_command() {
  printf '%s' "$INPUT" | python3 -c '
import json
import os
from pathlib import Path
import re
import shlex
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)

tool_input = data.get("tool_input") or {}
command = tool_input.get("command")
if not isinstance(command, str) or "data/raw" not in command:
    sys.exit(1)

try:
    tokens = shlex.split(command)
except ValueError:
    tokens = command.replace(";", " ").replace("|", " ").replace("&", " ").split()

raw_refs = set(re.findall(r"(?:\\./)?data/raw(?:/[^\\s;|&<>\"\\x27]*)?", command))
for token in tokens:
    if token == "data/raw" or token.startswith("data/raw/") or token.startswith("./data/raw/"):
        raw_refs.add(token[2:] if token.startswith("./") else token)

root = Path(os.environ.get("PROJECT_ROOT") or ".")
existing_refs = {ref for ref in raw_refs if (root / ref).exists()}
if not existing_refs:
    sys.exit(1)

destructive_words = {
    "chmod", "chown", "chflags", "dd", "mv", "perl", "rm",
    "sed", "truncate",
}
if any(token in destructive_words for token in tokens):
    sys.exit(0)

overwrite_words = {"cp", "curl", "install", "rsync", "tee", "touch", "wget"}
if any(token in overwrite_words for token in tokens):
    sys.exit(0)

if re.search(r">+\\s*[\"\\x27]?(?:\\./)?data/raw(?:/|\\b)", command):
    sys.exit(0)

sys.exit(1)
'
}

if [[ "$TOOL" == "Bash" ]]; then
  protect_raw_permissions
  reject_invalid_meeting_paths_in_command
  if is_mutating_raw_command; then
    echo "Protected raw data: commands may add new files, but must not edit or delete existing files in data/raw." >&2
    exit 2
  fi
fi

if [[ "$TOOL" != "apply_patch" && "$TOOL" != "Edit" && "$TOOL" != "Write" ]]; then
  exit 0
fi

protect_raw_permissions

while IFS=$'\t' read -r ACTION FILE; do
  if [[ -z "${FILE:-}" ]]; then
    FILE="$ACTION"
    ACTION=""
  fi
  [[ -z "$FILE" ]] && continue

  REL_FILE="$FILE"
  if [[ -n "$CWD" && "$FILE" == "$CWD/"* ]]; then
    REL_FILE="${FILE#"$CWD"/}"
  fi

  if is_raw_path "$REL_FILE"; then
    RAW_TARGET="$PROJECT_ROOT/$REL_FILE"
    if [[ "$ACTION" == "Add" && ! -e "$RAW_TARGET" ]]; then
      continue
    fi
    if [[ "$TOOL" == "Write" && ! -e "$RAW_TARGET" ]]; then
      continue
    fi
    echo "Protected raw data: $REL_FILE already exists or would be modified/deleted. Add new raw files only; do not edit or delete existing raw files." >&2
    exit 2
  fi

  if is_meeting_path "$REL_FILE" && [[ "$REL_FILE" != "docs/work/meetings/.gitkeep" ]] && ! is_valid_meeting_path "$REL_FILE"; then
    echo "Meeting files must use docs/work/meetings/YYYY-MM-DD_topic-slug.md with a real date and lowercase hyphen-separated slug." >&2
    exit 2
  fi

  for PATTERN in "${PROTECTED_PATTERNS[@]}"; do
    if [[ "$REL_FILE" == "$PATTERN" ]]; then
      echo "Protected file: $REL_FILE. Edit intentionally, or remove the protection in .codex/hooks/protect-files.sh." >&2
      exit 2
    fi
  done
done < <(extract_paths)

exit 0
