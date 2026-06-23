---
name: generate-redteam-batch
description: Generate a batch of synthetic identity attacks (faces/voices/documents) + a synthetic legitimate control set, with cross-generator splits and a datasheet. Use when building or extending the red-team dataset (WS-B). Triggers: red-team, synthetic attack, dataset batch, generate samples.
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
metadata:
  triggers: { keywords: [red-team, synthetic, dataset, attack batch, generate samples], globs: ["data/**", "src/shield_id/data/**"] }
---

# Generate Red-Team Batch

## When to use
Building/extending the open-source red-team attack dataset (EPIC-REDTEAM-DATASET).

## When NOT to use
Any task involving real user data — forbidden (I2). This skill is synthetic-only.

## Constraints (hard)
- **Synthetic-only.** `no_real_pii.py` blocks real PII.
- **Cross-generator by construction (I4/D8):** designate ≥1 generator as held-out; never use it in training.
- Never commit raw data (`data/raw/`, `data/biometric/` are gitignored).
- Record demographic distribution (rule 06) so fairness isn't the generator's bias.

## Procedure
1. Read the eval-plan's splits-manifest (train generators vs held-out C).
2. Generate per modality (start with documents — D9). Label each: attack type · generation method · difficulty tier.
3. Write/refresh the datasheet (templates/datasheet) incl. demographic table.
4. Emit a splits-manifest. Hand to eval-independent (you do not evaluate — M5).

See `references/generators.md` for the approved generator list and version pinning.
