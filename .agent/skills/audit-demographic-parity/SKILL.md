---
name: audit-demographic-parity
description: Audit a model's disaggregated accuracy and false-positive rate across demographic segments and decide if a parity gap is statistically significant. Use as fairness-auditor. Triggers: fairness, bias audit, parity, disaggregated, demographic.
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
metadata:
  triggers: { keywords: [fairness, bias, parity, disaggregated, demographic], globs: ["src/shield_id/eval/**"] }
---

# Audit Demographic Parity

## When to use
As fairness-auditor, after eval-independent has results (depends_on: eval-independent).

## Constraints (hard)
- **Disaggregated FPR is the PRIMARY metric** (rule 06); global FPR is secondary.
- Target is **FPR-under-parity**, not a vanity global number.
- Validate the dataset's own demographic distribution first (a generator's bias must not be read as fairness).

## Procedure
1. Compute accuracy + FPR per segment from the eval results.
2. Test each segment gap for statistical significance.
3. Verdict: BLOCK the readiness claim if any gap is significant; else PASS with the disaggregated table.
4. Publish disaggregated metrics (transparency-by-design).
