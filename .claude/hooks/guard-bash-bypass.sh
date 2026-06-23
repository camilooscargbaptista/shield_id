#!/usr/bin/env bash
# PreToolUse(Bash). exit 2 = BLOCK. Stops gate-bypass and state tampering.
INPUT="$(cat)"
CMD="$(printf '%s' "$INPUT" | grep -oE '"command"\s*:\s*"[^"]*"' | sed -E 's/.*:\s*"(.*)"/\1/')"
if printf '%s' "$CMD" | grep -qiE -- '--no-verify|git .*commit.*-n\b'; then
  echo "BLOCKED: --no-verify bypasses the gates (M6). Forbidden." >&2; exit 2
fi
if printf '%s' "$CMD" | grep -qiE 'rm .*(\.agent/state|approval-log\.jsonl|\.git/hooks)|>\s*\.agent/state'; then
  echo "BLOCKED: tampering with audit state (approval-log/.agent/state)." >&2; exit 2
fi
exit 0
