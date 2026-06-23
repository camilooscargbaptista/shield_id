---
name: run-eval-and-report
description: Run the evaluation harness with the mandatory cross-generator protocol and produce a reproducible report with curves and a robustness delta. Use ONLY as the independent evaluator (eval-independent) in an isolated session. Triggers: run eval, benchmark, measure accuracy, eval report.
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
metadata:
  triggers: { keywords: [run eval, benchmark, measure, eval report, metrics], globs: ["src/shield_id/eval/**"] }
---

# Run Eval and Report

## When to use
Only as `eval-independent`, in an isolated session, to certify a model the builder produced (M5/D4).

## When NOT to use
If you are the agent that built the model — you may not evaluate your own work (M5).

## Constraints (hard)
- **Cross-generator mandatory** (rule 05): test on a held-out generator never seen in training.
- **Report curves, not points**; robustness delta is the headline.
- Re-run the harness yourself; do NOT trust the builder's printed numbers (M1).
- Output must be reproducible (notebook + seed + data + model version).

## Procedure
1. Load the frozen held-out test split (never seen in dev).
2. Compute P/R @ fixed FPR (ROC/PR + CI); compute cross-generator + stress-tier robustness delta.
3. Hand disaggregated results to fairness-auditor (rule 06).
4. Emit `verification-<ts>.json` (verdict) + a report. FAIL if cross-generator absent or not reproducible.
