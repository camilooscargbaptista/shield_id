#!/usr/bin/env python3
"""Start a new experiment: writes the active-experiment state machine."""
import argparse, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import state

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--type", default="experiment", choices=list(state.STEP_SETS))
    a = ap.parse_args()
    s = state.start(a.slug, a.type)
    print(f"Started '{a.slug}' (type={a.type}).")
    print("Ordered gates:", " -> ".join(s["steps"]))
    print("src/ edits BLOCKED until these are approved:",
          [k for k, v in s["steps"].items() if v["gates_src"]])

if __name__ == "__main__": main()
