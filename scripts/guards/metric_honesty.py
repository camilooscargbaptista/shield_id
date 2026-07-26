#!/usr/bin/env python3
"""I3/I4 (rules 05/07): a file that claims a metric must also evidence the cross-generator
protocol AND a reproducible artifact. Scans given files (e.g., staged reports/SUMMARY).
--require-cross-generator hard-fails if a metric % lacks 'cross-generator'. Exit 1 = BLOCK.

Hardening (LC-004, found by eval-independent on US-001 certification): the exemption for a
*target* declaration must be ADJACENT to the number (a tight window), not merely the word
"target" appearing anywhere in the file. Otherwise an unrelated "target" whitelisted a whole
dishonest report. The exemption now requires `target|aspirational` within ~12 chars of the %."""
import sys, re
from pathlib import Path

METRIC = re.compile(r"\b\d{2,3}(?:\.\d+)?\s*%")
# A bare TARGET declaration is exempt ONLY when target/aspirational is adjacent to the number.
# PORT-1.1 (2026-07-21): same tight-adjacency rule extended to pedagogical text —
# example/illustrative/hypothetical/estimate adjacent to the number marks it as a
# non-claim (teaching dialogue in .agent/ cards, cost estimates). Window stays 12 chars
# so a real result cannot be laundered by a distant word (LC-004 rationale).
EXEMPT_WORDS = r"(?:target|aspirational|example|illustrative|hypothetical|estimate|estimativa|exemplo)"
TARGET_ADJ = re.compile(EXEMPT_WORDS + r"\W{0,12}\d{2,3}(?:\.\d+)?\s*%"
                        r"|\d{2,3}(?:\.\d+)?\s*%\W{0,12}" + EXEMPT_WORDS, re.I)

# PORT-1.1 (2026-07-21): policy/pedagogy scope. `.agent/` and `.context/` hold rules,
# thresholds ("coverage >= 80%") and teaching examples — never measured RESULTS (SSOT:
# results live in docs/reports + the verification artifacts emitted by verify_eval.py,
# rule 15). Scanning them produced only false positives, which trains humans to ignore
# the gate. Everything outside these trees keeps the strict scan.
PEDAGOGICAL_PREFIXES = (".agent/", ".context/")


def _is_pedagogical(path: str) -> bool:
    norm = path.replace("\\", "/")
    while norm.startswith("./"):
        norm = norm[2:]
    return norm.startswith(PEDAGOGICAL_PREFIXES)


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    fails = []
    for f in files:
        p = Path(f)
        if not p.is_file():
            continue
        if _is_pedagogical(f):
            continue
        low = p.read_text(errors="ignore").lower()
        has_cross = ("cross-generator" in low) or ("cross generator" in low)
        has_repro = bool(re.search(r"(notebook|seed|reproducib)", low))
        # scan line by line so the exemption is scoped to the actual metric, not the whole file
        for ln in low.splitlines():
            if not METRIC.search(ln):
                continue
            if TARGET_ADJ.search(ln):          # an adjacent "target 95%" / "95% (target)" is allowed bare
                continue
            if not has_cross:
                fails.append((f, f"metric without cross-generator evidence (I4/D8): '{ln.strip()[:60]}'"))
            if not has_repro:
                fails.append((f, f"metric without reproducible artifact (I3/D5): '{ln.strip()[:60]}'"))
    if fails:
        print("BLOCKED — metric honesty (rules 05/07). A reported number needs cross-generator + reproducibility:")
        for f, m in fails:
            print(f"  {f}: {m}")
        raise SystemExit(1)
    print("metric_honesty: OK")
    raise SystemExit(0)

if __name__ == "__main__":
    main()
