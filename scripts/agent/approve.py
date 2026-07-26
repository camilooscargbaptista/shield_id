#!/usr/bin/env python3
"""Approve a gate step (the human gate). Auto-advances + appends to the audit log.

PORT-2 (M5/D4): a VERDICT-GATED step (at minimum `eval`) cannot be approved without an
independent-reviewer PASS/PASS_WITH_WARNINGS verdict present in current-experiment.json
(written by verify_eval.py). No verdict, or a FAIL/error verdict => REFUSE (non-zero).
Non-verdict gates (kickoff/spec/c4/eval-plan/...) behave exactly as before."""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import state  # noqa: E402

# Steps that require a passing independent-reviewer verdict before they can be approved.
VERDICT_GATED = {"eval"}
PASS_VERDICTS = {"PASS", "PASS_WITH_WARNINGS"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("--approver", default="camilo")
    a = ap.parse_args()

    if a.step in VERDICT_GATED:
        lv = state.get_verdict(a.step)
        if lv is None:
            print(
                f"REFUSED: cannot approve verdict-gated step '{a.step}' — no independent-reviewer "
                f"verdict recorded for it. Run: scripts/agent/verify_eval.py <artifact> --step {a.step}",
                file=sys.stderr,
            )
            raise SystemExit(1)
        verdict = lv.get("verdict")
        if verdict not in PASS_VERDICTS:
            reason = (lv.get("detail") or {}).get("reason", "")
            print(
                f"REFUSED: cannot approve '{a.step}' — independent-reviewer verdict is "
                f"'{verdict}' (need PASS or PASS_WITH_WARNINGS)."
                + (f" reviewer reason: {reason}" if reason else ""),
                file=sys.stderr,
            )
            raise SystemExit(1)
        print(f"Verdict gate OK for '{a.step}': {verdict} (recorded {lv.get('at')}).")

    s = state.approve(a.step, a.approver)
    print(f"Approved '{a.step}'. current_step -> {s['current_step']}")


if __name__ == "__main__":
    main()
