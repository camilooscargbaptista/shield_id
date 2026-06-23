#!/usr/bin/env bash
# SessionStart. Advisory: recommend the cheapest adequate model for the current step. Always exit 0.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STEP="$(python3 - "$ROOT" <<'PY' 2>/dev/null || true
import json,sys,os
p=os.path.join(sys.argv[1],".agent","state","current-experiment.json")
print(json.load(open(p))["current_step"] if os.path.exists(p) else "")
PY
)"
case "$STEP" in
  kickoff|status|outline|review) echo "[cost] step '$STEP' is light → consider /model haiku (~95% cheaper)";;
  spec|eval-plan|data|implementation|datasheet|draft) echo "[cost] step '$STEP' → /model sonnet";;
  c4|threat-model|verify|eval) echo "[cost] step '$STEP' is architectural/critical → /model opus";;
  *) : ;;
esac
exit 0
