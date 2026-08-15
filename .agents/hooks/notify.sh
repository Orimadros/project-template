#!/usr/bin/env bash
set -euo pipefail

# Desktop notification, shared across harnesses. Claude Code's Notification
# event carries message/title directly; Codex has no equivalent event and
# instead fires this on PermissionRequest, which carries tool_name and
# tool_input.description instead. Probe the payload shape rather than
# branching on which harness is running.

INPUT="$(cat)"
MESSAGE="$(printf '%s' "$INPUT" | python3 -c 'import json, sys
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {}
message = data.get("message")
if message:
    print(message)
else:
    tool_name = data.get("tool_name") or "a tool"
    description = ((data.get("tool_input") or {}).get("description") or "")
    print(description or f"Approval requested for {tool_name}.")')"
TITLE="$(printf '%s' "$INPUT" | python3 -c 'import json, sys
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {}
print(data.get("title") or "Agent needs attention")')"

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
