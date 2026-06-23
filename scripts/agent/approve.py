#!/usr/bin/env python3
"""Approve a gate step (the human gate). Auto-advances + appends to the audit log."""
import argparse, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib import state

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("--approver", default="camilo")
    a = ap.parse_args()
    s = state.approve(a.step, a.approver)
    print(f"Approved '{a.step}'. current_step -> {s['current_step']}")

if __name__ == "__main__": main()
