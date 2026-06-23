#!/usr/bin/env python3
"""Fail the push if .agent/INDEX.md is out of sync with the rules/agents/guards/workflows dirs.
Mirrors zeca's index-drift-check. Exit 1 = BLOCK."""
import sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2] / ".agent"
def main():
    index = (ROOT / "INDEX.md").read_text()
    drift = []
    for d in ["rules", "agents", "guards", "workflows"]:
        for f in sorted((ROOT / d).glob("*.md")):
            stem = f.stem.replace(".template", "")
            key = stem.split("-", 1)[0] if d == "rules" else stem
            if key not in index and stem not in index:
                drift.append(f"{d}/{f.name} not referenced in INDEX.md")
    if drift:
        print("BLOCKED — INDEX.md drift (update INDEX when adding files):")
        for d in drift: print("  ", d)
        raise SystemExit(1)
    print("index_drift: OK"); raise SystemExit(0)
if __name__ == "__main__": main()
