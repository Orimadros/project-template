#!/usr/bin/env bash
set -euo pipefail

# Block accidental edits to protected project calibration files.
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
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if match:
            paths.append(match.group(1).strip())

for path in dict.fromkeys(paths):
    print(path)
'
}

if [[ "$TOOL" != "apply_patch" && "$TOOL" != "Edit" && "$TOOL" != "Write" ]]; then
  exit 0
fi

PROTECTED_PATTERNS=(
  "docs/sources/references.bib"
  ".claude/references/domain-profile.md"
  ".claude/references/personal-style-guide.md"
  ".claude/references/journal-profiles.md"
  ".claude/settings.json"
  ".codex/config.toml"
)

while IFS= read -r FILE; do
  [[ -z "$FILE" ]] && continue

  REL_FILE="$FILE"
  if [[ -n "$CWD" && "$FILE" == "$CWD/"* ]]; then
    REL_FILE="${FILE#"$CWD"/}"
  fi

  for PATTERN in "${PROTECTED_PATTERNS[@]}"; do
    if [[ "$REL_FILE" == "$PATTERN" ]]; then
      echo "Protected file: $REL_FILE. Edit intentionally, or remove the protection in .codex/hooks/protect-files.sh." >&2
      exit 2
    fi
  done
done < <(extract_paths)

exit 0
