---
id: wf-pre-mortem
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~450
description: Mandatory before risky work.
---

# pre-mortem (mandatory before risky work)

> Mandatory before: a new detector, a metric-bearing eval, a privacy-sensitive data pipeline, an AITA layer,
> any change touching money/PII/auth.

## Steps
1. "Imagine it is 3 months later and this was a disaster — why?" Enumerate **≥10 risks**.
2. Score each P×I; assign an owner + a deadline.
3. Pick the **top-3 immediate actions**; define production alert signals + a rollback plan.
4. Write `00-pre-mortem.md` in the epic.

## SHIELD-ID-specific risks to always consider
the circularity trap (rule 05); a parity gap on a protected segment (rule 06); a "derived" vector that's
invertible (rule 04); a from-scratch detector overfitting; a supply-chain typosquat (rule 13);
solo-team over-scope (D9).

## Anti-patterns
- ❌ Skipping the pre-mortem on a metric-bearing or privacy-sensitive change. ❌ Risks with no owner/action.
