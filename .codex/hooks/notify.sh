#!/usr/bin/env bash
set -euo pipefail

# Desktop notification for Codex PermissionRequest hooks.
# Codex has no Claude-style Notification event; PermissionRequest is the
# lifecycle event that fires when Codex is about to ask for approval.

INPUT="$(cat)"
TOOL="$(printf '%s' "$INPUT" | python3 -c 'import json, sys
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {}
print(data.get("tool_name") or "tool")')"
DESCRIPTION="$(printf '%s' "$INPUT" | python3 -c 'import json, sys
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {}
print(((data.get("tool_input") or {}).get("description") or ""))')"

TITLE="Codex approval requested"
if [[ -n "$DESCRIPTION" ]]; then
  MESSAGE="$DESCRIPTION"
else
  MESSAGE="Codex needs approval for $TOOL."
fi

case "$(uname -s)" in
  Darwin)
    MESSAGE="${MESSAGE//\"/\\\"}"
    TITLE="${TITLE//\"/\\\"}"
    osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\"" 2>/dev/null || true
    ;;
  Linux)
    if command -v notify-send >/dev/null 2>&1; then
      notify-send "$TITLE" "$MESSAGE" 2>/dev/null || true
    else
      echo "[$TITLE] $MESSAGE" >&2
    fi
    ;;
  *)
    echo "[$TITLE] $MESSAGE" >&2
    ;;
esac

exit 0
