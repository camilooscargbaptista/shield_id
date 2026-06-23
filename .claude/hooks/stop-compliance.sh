#!/usr/bin/env bash
# Stop. Advisory summary of where we are. exit 0.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$ROOT/scripts/agent/status.py" 2>/dev/null || true
exit 0
