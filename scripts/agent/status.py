#!/usr/bin/env python3
"""Where are we: print the active experiment + gate status."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import state

s = state.load()
if not s: print("No active experiment. Run scripts/agent/start_experiment.py <slug>."); raise SystemExit(0)
print(f"Experiment: {s['experiment']} (type={s['type']})  branch={s['branch']}")
print(f"current_step: {s['current_step']}")
for k, v in s["steps"].items():
    mark = "x" if v["approved"] else " "
    gate = " [gates src]" if v["gates_src"] else ""
    print(f"  [{mark}] {k}{gate}")
pend = state.unapproved_src_gates()
if pend: print("src/ edits BLOCKED until approved:", pend)
