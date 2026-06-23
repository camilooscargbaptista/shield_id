---
id: wf-review
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~350
description: Comprehensive 7-dimension review; reviewer != author.
---

# review

> 7-dimension review (CODE-REVIEW-CHECKLIST). Reviewer is never the author (M5 spirit).

## Steps
1. Walk the 7 dimensions: correctness · security · **privacy (no raw biometric)** · reproducibility ·
   ML hygiene (fine-tuned not from-scratch; builder reported no metric) · tests · docs & git.
2. Output: summary · critical MUST-fix · suggestions · positives · verdict **Approve | Request-Changes | Reject**.

## Worked example
PR prints "94%" → ML-hygiene dimension fails (rule 15, builder self-reported) → Request-Changes: remove the
number, route to eval-independent.

## Anti-patterns
- ❌ Reviewing your own code. ❌ Approving a raw-biometric field. ❌ Approving a builder-reported metric.
