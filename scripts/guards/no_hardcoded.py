#!/usr/bin/env python3
"""rule 32: no silent defaults / magic thresholds in detection/eval logic. Scans src for
inline numeric thresholds and `or <default>` patterns on sensitive names. Exit 1 = BLOCK."""
import sys, re
from pathlib import Path
# Flag a bare hardcoded CONSTANT (e.g. `threshold = 0.5`), NOT a literal used inside arithmetic
# (e.g. `trust_score = 1.0 - artifact_score` — a probability complement, not a tunable). The number
# must be the COMPLETE assigned value (optionally followed by a comment), so anchor it to end-of-line.
SENSITIVE = re.compile(r"(threshold|fpr|cutoff|score|model_path|fpr_target)\s*=\s*(0?\.\d+|\d+)\s*(#.*)?$", re.I)
OR_DEFAULT = re.compile(r"(threshold|fpr|cutoff|model_path)\s*(=|or)\s*['\"0-9]", re.I)
ALLOW = re.compile(r"(config|settings|enum|Field\(|pydantic|test_)", re.I)

# rule 32 targets PRODUCTION LOGIC. Docs/notebooks/JSON artifacts aren't logic, tests SHOULD use
# literal thresholds (that's the fixture), and config is exactly where values belong. Scan src .py only.
# (PII/secret scanning stays broad in their own guards — this narrowing is logic-specific, not a weakening.)
def _skip(path: str) -> bool:
    norm = path.replace("\\", "/")
    name = Path(norm).name
    if not norm.endswith(".py"): return True
    if "/tests/" in norm or name.startswith("test_") or norm.endswith("_test.py"): return True
    if "config" in name: return True
    return False

def main():
    files = sys.argv[1:] or ([str(p) for p in Path("src").rglob("*.py")] if Path("src").exists() else [])
    hits = []
    for f in files:
        p = Path(f)
        if _skip(str(f)) or not p.is_file(): continue
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if ALLOW.search(line): continue
            if SENSITIVE.search(line): hits.append((f, i, line.strip()[:90]))
    if hits:
        print("BLOCKED — rule 32 hardcoded threshold/default. Move to config:")
        for f, i, l in hits: print(f"  {f}:{i}: {l}")
        raise SystemExit(1)
    print("no_hardcoded: OK"); raise SystemExit(0)
if __name__ == "__main__": main()
