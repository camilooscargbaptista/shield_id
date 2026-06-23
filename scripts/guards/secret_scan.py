#!/usr/bin/env python3
"""Block committed secrets. Exit 1 = BLOCK."""
import sys, re
from pathlib import Path
PATTERNS = [r"sk-[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"(api[_-]?key|secret|token)\s*=\s*['\"][A-Za-z0-9/+]{16,}['\"]"]
def main():
    files = sys.argv[1:] or [str(p) for p in Path(".").rglob("*.py")]
    hits = []
    for f in files:
        p = Path(f)
        if not p.is_file() or ".git" in f: continue
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            for pat in PATTERNS:
                if re.search(pat, line): hits.append((f, i))
    if hits:
        print("BLOCKED — possible secret:"); [print(f"  {f}:{i}") for f, i in hits]; raise SystemExit(1)
    print("secret_scan: OK"); raise SystemExit(0)
if __name__ == "__main__": main()
