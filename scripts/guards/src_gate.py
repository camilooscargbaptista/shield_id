#!/usr/bin/env python3
"""Used by guard-src-edits hook. Exit 1 if editing a src/ file while required src-gating
steps are unapproved (or no active experiment). Tests are always allowed (TDD red)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import state

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    if "/src/" not in path and not path.startswith("src/"): raise SystemExit(0)   # not production code
    if path.endswith(("_test.py", "test_.py")) or "/tests/" in path: raise SystemExit(0)  # tests allowed
    pend = state.unapproved_src_gates()
    if pend is None:
        print("BLOCKED: no active experiment. Run scripts/agent/start_experiment.py <slug> first (M3).")
        raise SystemExit(1)
    if pend:
        print(f"BLOCKED: src/ edits require approved gates first (M3). Pending: {pend}")
        print("Approve with: python scripts/agent/approve.py <step>")
        raise SystemExit(1)
    raise SystemExit(0)

if __name__ == "__main__": main()
