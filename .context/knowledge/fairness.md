---
domain: fairness
last_updated: 2026-06-17
maintainers: [fairness-auditor]
related_rules: [06, 03]
related_adrs: []
confidence: medium
status: active
---

# Knowledge — Fairness

## TL;DR
**Disaggregated FPR is the PRIMARY metric (rule 06).** The populations SHIELD-ID most wants to protect are
the most exposed to false positives. A flat global FPR is a vanity metric.

## Key concepts / the math
Global FPR is a weighted average. Segment X (5% of data) at FPR 1.6% + the rest at 0.02% ≈ global 0.1% —
looks like the target is hit while X is 80× worse. **Report the table, not the average.** Target =
FPR-under-parity.

## Gotchas (with source)
- **Generator-bias masquerade (LC, rule 03):** a synthetic dataset inherits its generator's demographic
  bias. If you don't validate the dataset distribution, the audit measures the *generator*, not the
  *detector*. → datasheet distribution table is mandatory before any fairness claim.

## Patterns
Per-segment accuracy + FPR; statistical-significance test per gap (report p-value); human-review escalation
for all automated rejections; public disaggregated metrics (transparency-by-design).
