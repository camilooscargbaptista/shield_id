#!/usr/bin/env python3
"""I2 (rule 03): no real personal data in datasets. Scans data files for real-PII markers
(CPF/CNPJ patterns, real-looking emails) under data/ and dataset dirs. Exit 1 = BLOCK.
Synthetic markers (synthetic_, fake_, example.com) are allowed."""
import sys, re
from pathlib import Path

CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CNPJ = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")
EMAIL = re.compile(r"\b[a-z0-9._%+-]+@(?!example\.com|synthetic\.|test\.)[a-z0-9.-]+\.[a-z]{2,}\b", re.I)
SYNTH_OK = re.compile(r"(synthetic|fake|dummy|sample|example|generated)", re.I)

def main():
    targets = sys.argv[1:]
    if not targets:
        targets = [str(p) for p in Path("data").rglob("*") if p.is_file()] if Path("data").exists() else []
    hits = []
    for f in targets:
        p = Path(f)
        if not p.is_file(): continue
        try: text = p.read_text(errors="ignore")
        except Exception: continue
        if SYNTH_OK.search(p.name): continue
        for i, line in enumerate(text.splitlines(), 1):
            if SYNTH_OK.search(line): continue
            if CPF.search(line) or CNPJ.search(line) or EMAIL.search(line):
                hits.append((f, i, line.strip()[:80]))
    if hits:
        print("BLOCKED — I2 possible REAL PII in data (rule 03). Datasets must be synthetic-only:")
        for f, i, l in hits[:20]: print(f"  {f}:{i}: {l}")
        raise SystemExit(1)
    print("no_real_pii: OK"); raise SystemExit(0)

if __name__ == "__main__": main()
