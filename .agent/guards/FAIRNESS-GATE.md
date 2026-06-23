---
id: guard-fairness-gate
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: on_demand
priority: HIGH
tokens: ~450
description: Blocks deployment claim on a significant disaggregated parity gap.
---

# FAIRNESS-GATE

> Before ANY deployment/readiness claim. Owned by fairness-auditor (which can BLOCK).

## Requires (all of)
- **Disaggregated accuracy + FPR reported per segment** (rule 06) — not just the global average.
- **No statistically significant parity gap** (the test + p-value shown, not a vibe).
- **FPR-under-parity is the stated target**, not a flat global FPR.
- The **dataset's own demographic distribution validated** (rule 03) — so we measure the detector, not the
  generator's bias.
- **Human-review escalation** exists for all automated rejections.

## Worked example
Global FPR 0.09% (looks like the <0.1% target is hit). Disaggregated: segment X FPR 0.8%, significant →
**BLOCK** the "we hit <0.1%" claim. The honest headline is the per-segment table + the gap + a mitigation plan.

## Anti-patterns
- ❌ Reporting only the global FPR. ❌ "Average is fine." ❌ A readiness claim without the segment table.
