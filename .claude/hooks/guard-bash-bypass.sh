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
# hooksPath tampering: the only legitimate use is installing the canonical path (.githooks).
# Unsetting it, or pointing it elsewhere (incl. `git -c core.hooksPath=...`), disables every gate.
if printf '%s' "$CMD" | grep -qiE 'core\.hooksPath' \
   && ! printf '%s' "$CMD" | grep -qE 'core\.hooksPath([= ]|%3D)+\.githooks([^A-Za-z0-9_/.-]|$)'; then
  echo "BLOCKED: core.hooksPath tampering disables the gates (M6). Only 'git config core.hooksPath .githooks' is allowed." >&2; exit 2
fi
exit 0
