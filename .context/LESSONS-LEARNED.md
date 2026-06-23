---
id: lessons-learned
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
description: Lessons (LC-xxx). Each should graduate into a guard/rule (retrospect → guard).
---

# Lessons Learned

> A lesson that stays markdown is folklore. Each LC should become an executable guard or a rule.

| ID | Lesson | Became |
|----|--------|--------|
| LC-001 | The circularity trap: testing detection on your own generators inflates the number. | rule 05 + `metric_honesty.py --require-cross-generator` (guard) |
| LC-002 | A flat global FPR can hide a high minority FPR. | rule 06 (disaggregated FPR primary) + FAIRNESS-GATE |
| LC-003 | Layer 2 has no behavioral data source this phase. | D7 (specify/simulate, escalate to PSP) |
| LC-004 | The `metric_honesty` guard whitelisted a whole file if the word "target" appeared anywhere — an in-distribution metric could bypass it. Found by **eval-independent** during US-001 certification (the judge caught what the builder missed). | Hardened `scripts/guards/metric_honesty.py`: the target-exemption must now be ADJACENT to the number (re-tested: bypass blocked, honest/target pass). The lesson became a guard fix, not just a note. |
