#!/usr/bin/env bash
# PostToolUse(Bash). Audit: if a bypass was used, record it. Advisory. exit 0.
INPUT="$(cat)"; CMD="$(printf '%s' "$INPUT" | grep -oE '"command"[^,]*' || true)"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if printf '%s' "$CMD" | grep -qiE -- '--no-verify'; then
  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"event\":\"bypass_used\",\"detail\":\"--no-verify\"}" >> "$ROOT/.agent/state/approval-log.jsonl"
  echo "[audit] bypass recorded — will surface in CI" >&2
fi
exit 0
