---
id: rule-06-fairness
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~800
description: Disaggregated FPR is PRIMARY. FPR-under-parity. SSOT owner: fairness.
---

# 06 — Fairness (SSOT owner: fairness)

> Fairness is a **first-class deliverable, not a footnote.** The cruel irony of this project: the
> populations SHIELD-ID most wants to protect (Global South, marginalized, thin-credit-file users) are the
> **most exposed to false positives** in biometric/behavioral systems trained on high-income, urban,
> Western data. A fraud system that wrongly flags them recreates the harm it set out to prevent.

## The rules
1. **Disaggregated FPR is the PRIMARY metric.** The global FPR is **secondary.** (LESSON LC-002: a flat
   global 0.1% FPR can hide a 1% FPR for a minority segment — for *this* project that is an ethical failure
   disguised as a metric success.)
2. **The real target is FPR-under-parity**, not a vanity global number. A beautiful global FPR with a
   significant per-segment gap is a **fail**, not a pass.
3. **Mandatory demographic performance-parity testing before any deployment claim.** Publish disaggregated
   accuracy + FPR per segment. (fairness-auditor owns this; it can BLOCK.)
4. **Validate the dataset's own demographic distribution first** (rule 03) — otherwise you measure the
   generator's bias, not the detector's.
5. **Human-review escalation** for all automated rejections; **contestation pathway** for flagged users.

## The math that makes this non-negotiable
Global FPR is a weighted average. If segment X is 5% of the data and has FPR 1.6%, the other 95% at 0.02%
yields a global ≈ 0.1% — looks like the target is hit, while segment X is 80× worse. **Report the table,
not the average.**

## Worked example
Global FPR 0.09% (looks like <0.1% target hit). Disaggregate → segment X FPR 0.8%, significant.
fairness-auditor verdict: **BLOCK** the "we hit <0.1%" claim. The honest headline is the per-segment table
+ the gap + a mitigation plan.

## Acceptance checklist
- [ ] Per-segment accuracy + FPR reported. [ ] Each gap tested for statistical significance (p-value shown).
- [ ] FPR-under-parity is the stated target. [ ] Dataset demographic distribution validated (rule 03).
- [ ] Human-review escalation exists for rejections.

## Anti-patterns (forbidden)
- ❌ Reporting only the global FPR. ❌ "Average accuracy is fine." ❌ Treating synthetic diversity as given.
- ❌ A deployment claim without the disaggregated table.
