---
id: rule-15-no-self-reported-metrics
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~500
description: Builder never reports a number. Forbidden/allowed phrase table.
---

# 15 — No Self-Reported Metrics

A **builder agent (detection-ml, data-redteam) MUST NOT report any accuracy/latency/FPR number.** Only
`eval-independent` reports, after re-running the harness in an isolated session (M5 / D4). See rule 07
(SSOT for reproducibility) and rule 05 (the protocol).

## Why
The builder has every incentive (and context bias) to report the best-looking, in-distribution number. The
whole credibility model collapses if the builder's self-report is trusted. The number must come from a
session that never saw the code being written.

## Forbidden vs allowed (in a builder's SUMMARY/model-card)
| Forbidden (builder) | Allowed (builder) |
|---------------------|-------------------|
| "achieved 96% recall" | "ready for evaluation; eval-plan at <path>" |
| "passes at 0.3% FPR" | "implements the detector per US-001; metrics pending eval-independent" |
| "fast: 80ms" | "latency harness wired; numbers pending eval-independent" |

The model-card's **Evaluation section is left empty by the builder**; eval-independent fills it.

## Worked example
detection-ml finishes and writes: "## BUILD COMPLETE — document detector fine-tuned from base@1.3; eval-plan
at eval/doc-detector.md; **no metric reported (rule 15)**." The orchestrator then spawns eval-independent.

## Anti-patterns
- ❌ Any number in a builder's output. ❌ "Preliminary results suggest…" (still a self-report).
