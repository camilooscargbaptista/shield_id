---
id: guard-code-review-checklist
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: on_demand
priority: HIGH
tokens: ~500
description: 7-dimension review; reviewer != author.
---

# CODE-REVIEW-CHECKLIST

> 7 dimensions. The reviewer is never the author of the code under review (M5 spirit).

| # | Dimension | Checks |
|---|-----------|--------|
| 1 | Correctness | does it satisfy the eval scenarios (rule 11)? |
| 2 | Security | no secret; PII masked in logs; deps pinned (no typosquat); auth + rate limit (rule 13) |
| 3 | Privacy | **no raw biometric; derived vectors only; invertibility ok** (rule 04 / I1) |
| 4 | Reproducibility | config+seed; no magic numbers (rule 32); a number has a notebook (rule 07) |
| 5 | ML hygiene | fine-tuned not from-scratch (rule 05); held-out untouched; builder reported no metric (rule 15) |
| 6 | Tests | unit+integration; coverage target; no skipped without reason |
| 7 | Docs & git | model-card/datasheet present (rule 20); atomic Conventional commits (rule 08); glossary terms (rule 29) |

## Output
summary · critical MUST-fix · suggestions · positives · verdict **Approve | Request-Changes | Reject**.

## Worked example
A PR fine-tunes a detector and prints "94%". Dimension 5 fails: the builder self-reported a metric (rule 15).
Request-Changes: remove the number; route to eval-independent.

## Anti-patterns
- ❌ Reviewing your own code. ❌ Approving with a raw-biometric field. ❌ Approving a builder-reported metric.
