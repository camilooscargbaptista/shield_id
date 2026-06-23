---
id: wf-run-eval
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: CRITICAL
tokens: ~600
description: The independent, cross-generator eval loop.
---

# run-eval

> The heart of credibility. Never let a builder hand you a number — re-run it, isolated.

## Steps
1. `python scripts/agent/verify_eval.py --experiment <slug>` spawns **eval-independent in an ISOLATED
   session**, fed only the eval-plan + artifacts (zero builder context) — M5/D4.
2. eval-independent re-runs the harness itself (does NOT trust the SUMMARY), applies the **cross-generator
   protocol** (rule 05): train {A,B}, test held-out C.
3. Computes curves (P/R@fixed FPR + CI, ROC/PR) + the **robustness delta** (the headline) + hands
   disaggregated results to `fairness-auditor` (rule 06).
4. Emits `verification-<ts>.json` (verdict). Routes:
   - PASS / PASS_WITH_WARNINGS → proceed (+ retrospect).
   - FAIL (cross-generator missing) → back to builder: add the protocol (not optional, I4).
   - FAIL (not reproducible) → back to builder: notebook + seed (I3).
   - FAIL (parity gap) → fairness-auditor + builder investigate (rule 06).
   - FAIL (raw biometric) → P0 → privacy-ethics-review, halt (I1).

## Worked example
Builder's card says 96%. verify_eval ignores it, loads held-out C, re-runs → 84% @ FPR 0.3% (CI ±2pp),
delta −12pp. Verdict PASS_WITH_WARNINGS. The deck reports **84% cross-generator**, never 96%.

## Anti-patterns
- ❌ Reading the builder's number. ❌ Skipping the held-out C. ❌ Reporting a point. ❌ Same session builds+evals.
