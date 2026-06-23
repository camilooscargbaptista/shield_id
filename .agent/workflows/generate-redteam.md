---
id: wf-generate-redteam
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~450
description: Generate a synthetic attack batch with cross-generator splits.
---

# generate-redteam

> Skill: `generate-redteam-batch`. Owner: data-redteam. Synthetic-only (I2).

## Steps
1. Read the eval-plan's splits-manifest (train {A,B} vs held-out C).
2. Generate per modality (documents first — D9). Label each: attack type · generation method · difficulty tier.
3. Build the synthetic legitimate control set (for FPR).
4. **Validate + document the demographic distribution** in the datasheet (rule 03/06).
5. Pin generator versions (reproducibility, rule 02). Never commit raw data (.gitignore).
6. Emit the splits-manifest naming the held-out generator. Hand to eval-independent (M5).

## The cross-generator imperative (LC-001)
Holding out generator C **by construction** is the dataset's most important property — without it the
downstream number is tautological. Do not use all generators in training.

## Anti-patterns
- ❌ Real PII. ❌ No held-out generator. ❌ No datasheet / unvalidated demographics. ❌ Unpinned versions.
