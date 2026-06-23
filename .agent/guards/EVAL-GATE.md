---
id: guard-eval-gate
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: on_demand
priority: CRITICAL
tokens: ~600
description: Blocks any metric claim lacking cross-generator + reproducible artifact + isolated verdict.
---

# EVAL-GATE

> Blocks promotion of ANY result that is not honest-by-construction. This is the gate that protects the
> project's single scarcest asset: credibility under IEEE/OECD scrutiny.

## What it requires (all of)
1. **Held-out test split never seen in development** (rule 02). Check the splits-manifest.
2. **Cross-generator protocol present** (train {A,B} / test held-out C) — I4/D8.
3. **Reproducible artifact attached** (notebook + seed + data manifest + model version) — I3/D5.
4. **Reported as curves + robustness delta**, not a single point (rule 05).
5. **eval-independent ran in an ISOLATED session** and emitted PASS / PASS_WITH_WARNINGS (M5/D4).

## Enforcement
`scripts/guards/metric_honesty.py --require-cross-generator` (pre-push) + `scripts/agent/verify_eval.py`
(isolated eval-independent). A metric % in a committed file without "cross-generator" + a notebook/seed
reference is **blocked** (proven in the smoke test). BLOCKS the next phase.

## Worked example
A report says "96% precision" with no cross-generator mention → `metric_honesty.py` exit 1: "metric without
cross-generator evidence (I4/D8)" + "metric without reproducible artifact (I3/D5)". Promotion blocked.

## Anti-patterns
- ❌ Promoting an in-distribution headline. ❌ A point estimate. ❌ A metric the builder self-reported (rule 15).
