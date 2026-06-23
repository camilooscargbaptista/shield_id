#!/usr/bin/env bash
# PreToolUse(Edit|Write|MultiEdit). exit 2 = BLOCK the edit.
# Blocks production src/ edits unless an experiment is active AND required gates are approved (M3).
set -euo pipefail
INPUT="$(cat)"
# Extract the target file path from the tool input JSON (best-effort, stdlib jq-free).
FILE="$(printf '%s' "$INPUT" | grep -oE '"(file_path|path)"\s*:\s*"[^"]+"' | head -1 | sed -E 's/.*:\s*"([^"]+)".*/\1/')"
[ -z "${FILE:-}" ] && exit 0
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if ! python3 "$ROOT/scripts/guards/src_gate.py" "$FILE" 2>&1; then
  echo "Edit blocked by guard-src-edits (M3 zero-skip). Complete + approve the kickoff gates first." >&2
  exit 2
fi
exit 0
