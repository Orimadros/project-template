#!/bin/bash
# Block accidental edits to protected files.
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
FILE=""

if [ "$TOOL" = "Edit" ] || [ "$TOOL" = "Write" ]; then
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
fi

if [ -z "$FILE" ]; then
  exit 0
fi

PROTECTED_PATTERNS=(
  "docs/sources/references.bib"
  ".claude/references/domain-profile.md"
  ".claude/references/personal-style-guide.md"
  ".claude/references/journal-profiles.md"
  "settings.json"
)

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
REL_FILE="$FILE"
if [ -n "$PROJECT_DIR" ]; then
  REL_FILE="${FILE#$PROJECT_DIR/}"
fi
BASENAME=$(basename "$FILE")

for PATTERN in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$REL_FILE" == "$PATTERN" || "$BASENAME" == "$PATTERN" ]]; then
    echo "Protected file: $REL_FILE. Edit manually or remove protection in .claude/hooks/protect-files.sh" >&2
    exit 2
  fi
done

exit 0
