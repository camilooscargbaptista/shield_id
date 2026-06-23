---
id: wf-verify
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: CRITICAL
tokens: ~400
description: Independent verification gate (no self-verification).
---

# verify

> Runs between build and pr-opened. Nobody verifies their own work (M5/D4).

## Steps
1. Collect: diff + eval-scenarios + `must_haves` + threat-model.
2. Fire in parallel: **eval-independent** (isolated, re-runs the harness) + **fairness-auditor** + the
   relevant gate agent (privacy-ethics-review if biometric/PII; security-auditor if API/auth).
3. Each falsifies its slice: eval-independent assumes the goal was missed until evidence proves it;
   privacy checks invertibility; security runs STRIDE + supply-chain.
4. PASS (all) → release `pr-opened`. Any FAIL → block + route back with the specific gap.

## Worked example
verify on the detector: eval-independent PASS_WITH_WARNINGS (84% cross-gen, reproducible) +
fairness-auditor PASS (no significant gap) + privacy-ethics-review PASS (derived vectors, non-retention
test exists) → release pr-opened.

## Anti-patterns
- ❌ The builder verifying itself. ❌ Trusting the SUMMARY. ❌ Releasing with one gate red.
