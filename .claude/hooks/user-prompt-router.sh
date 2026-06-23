#!/usr/bin/env bash
# UserPromptSubmit router for /approved, /start-experiment, /status.
INPUT="$(cat)"; ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROMPT="$(printf '%s' "$INPUT" | grep -oE '"prompt"\s*:\s*"[^"]*"' | sed -E 's/.*:\s*"(.*)"/\1/')"
case "$PROMPT" in
  /approved*) STEP="${PROMPT#/approved }"; python3 "$ROOT/scripts/agent/approve.py" "$STEP" 2>&1 || true;;
  /status*)   python3 "$ROOT/scripts/agent/status.py" 2>&1 || true;;
esac
exit 0
