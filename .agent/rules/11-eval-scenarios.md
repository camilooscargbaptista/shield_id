---
id: rule-11-eval-scenarios
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~700
description: Acceptance criteria are EVALUATION scenarios, not UI BDD. With the canonical scenario set.
---

# 11 — Eval Scenarios (acceptance criteria for an ML product)

For SHIELD-ID, a user story's acceptance criteria are **evaluation scenarios**, not UI Gherkin. Each maps
to a `must_have` the `eval-independent` agent checks. They live in each epic's `eval-scenarios/`.

## The canonical scenario set (use these as the template)
```
Held-out:      on the unseen test split, recall ≥ <X> @ fixed FPR (curve + CI reported)
Cross-gen:     trained on {A,B}, tested on held-out C → robustness delta reported (rule 05 / I4)
Parity:        no statistically significant disaggregated FPR gap across segments (rule 06)
Privacy:       an automated test FAILS if any raw-biometric field is persisted (rule 04 / I1)
Reproducible:  a notebook + seed regenerates the identical curve (rule 07 / I3)
Latency:       p50/p95/p99 measured (this phase: measure, do not chase)
```

## Worked example (a story's eval scenarios)
Story "detect synthetic ID documents":
- Held-out: recall ≥ target @ FPR 0.3% on unseen docs.
- Cross-gen: held-out generator C robustness delta reported as the headline.
- Parity: per-segment FPR table, no significant gap.
- Privacy: no document image persisted (no_raw_biometric passes).

## Acceptance checklist
- [ ] Every story has explicit eval scenarios. [ ] Cross-gen + parity + privacy scenarios present.
- [ ] Each scenario is a checkable `must_have`, not prose.

## Anti-patterns
- ❌ UI-style Gherkin ("I click the button"). ❌ A story with no eval scenario. ❌ Omitting the cross-gen scenario.
