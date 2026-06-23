#!/usr/bin/env python3
"""Enforce M4 (scope is law) and M5 (independent verification exists).
--scope-allow <prefix>... : every changed file must be under an allowed prefix.
Reads changed files from argv after '--files'. Exit 1 = not ready."""
import sys
def main():
    args = sys.argv[1:]
    allow, files, mode = [], [], None
    for a in args:
        if a == "--scope-allow": mode = "allow"; continue
        if a == "--files": mode = "files"; continue
        (allow if mode == "allow" else files).append(a)
    bad = [f for f in files if allow and not any(f.startswith(p) for p in allow)]
    if bad:
        print("M4 VIOLATION (scope is law). Out-of-scope files:"); [print("  ", b) for b in bad]
        raise SystemExit(1)
    print("constitution-check: OK"); raise SystemExit(0)
if __name__ == "__main__": main()
