---
id: rule-12-mlops
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: MEDIUM
tokens: ~600
description: Retraining cadence, drift, model registry — specify this phase.
---

# 12 — MLOps

This phase: **specify, don't fully build** (Layer-3-style scoping). Define the operational story so it is
ready, without building production infra a solo team can't maintain yet.

## What to specify
1. **Red-team retraining cadence + trigger:** when a new generator appears or cross-generator delta degrades
   past a threshold (in config, rule 32), regenerate red-team batches (skill: generate-redteam-batch) and re-fine-tune.
2. **Model registry convention:** every shipped model = `model-card` + `datasheet` ref + `verification-*.json`
   (the eval-independent verdict). Version: `<base>@<ver>+ft-<date>`.
3. **Drift monitoring plan:** track cross-generator delta over time; alert on degradation.
4. **Compute cost estimate:** order-of-magnitude for training + red-team generation (the CTO-analysis gap).

## Acceptance checklist
- [ ] Retraining trigger defined (config-driven). [ ] Registry convention documented. [ ] Drift plan written.
- [ ] Compute cost estimated. [ ] Every model carries a model-card.

## Anti-patterns
- ❌ Building a full MLOps platform this phase. ❌ A model with no card/verdict. ❌ Ignoring compute cost.
