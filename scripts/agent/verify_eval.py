#!/usr/bin/env python3
"""Independent evaluation gate (M5/D4). Assembles the package an isolated eval-independent
session must receive, and checks the eval report meets the hard invariants (I3/I4).
In production this spawns a SEPARATE model session fed ONLY this package (zero builder context)
-- mirroring zeca's verify-feature.sh. Here it validates the artifacts deterministically and
emits a verdict skeleton. Exit 1 = FAIL (gates the pipeline)."""
import sys, json, re
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("usage: verify_eval.py <eval-report.md|json>"); raise SystemExit(2)
    rep = Path(sys.argv[1])
    if not rep.exists(): print(f"FAIL: report not found: {rep}"); raise SystemExit(1)
    text = rep.read_text().lower()
    fails = []
    if "cross-generator" not in text and "cross generator" not in text:
        fails.append("I4/D8: no cross-generator protocol evidenced")
    if not re.search(r"(notebook|seed)\b", text):
        fails.append("I3/D5: no reproducible artifact (notebook/seed) referenced")
    if re.search(r"\b9\d(\.\d+)?\s*%", text) and "in-distribution" in text and "cross-generator" not in text:
        fails.append("headline % appears to be in-distribution only")
    verdict = {"verdict": "FAIL" if fails else "PASS_WITH_WARNINGS",
               "isolated_session": "REQUIRED (spawn eval-independent with package only)",
               "checks": {"cross_generator": "cross-generator" in text,
                          "reproducible": bool(re.search(r"(notebook|seed)", text))},
               "fails": fails}
    print(json.dumps(verdict, indent=2))
    raise SystemExit(1 if fails else 0)

if __name__ == "__main__": main()
