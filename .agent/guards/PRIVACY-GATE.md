---
id: guard-privacy-gate
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~550
description: P0 block on raw-biometric persistence or real PII. Invertibility + non-retention test.
---

# PRIVACY-GATE

> P0 (highest-severity) gate. The project's core value proposition is trust & privacy; a violation here is
> not a bug, it is an existential breach of the product's premise.

## P0 BLOCKER on any of
- Any **raw-biometric field persisted** (I1) — including a "derived" field that is **invertible** back to
  the raw biometric (privacy-ethics-review checks invertibility, not the field name).
- Any **real PII** in datasets (I2).
- Any **cross-institution identity correlation** outside a governed agreement.
- **PII/biometric unmasked in logs** (rule 16).

## Required (verifiable non-retention)
There must exist an automated test that FAILS if any schema field persists a raw biometric. "How we prove
zero retention" is itself a Phase-2 deliverable (rule 04).

## Enforcement
`scripts/guards/no_raw_biometric.py` + `scripts/guards/no_real_pii.py` (pre-commit, exit 1 — both proven to
block) + privacy-ethics-review reasoning for the gray areas. Writes `.context/BLOCKER-privacy.md` on a P0.

## Worked example
`embedding = Column(LargeBinary)` where the embedding is a near-lossless invertible latent → P0 BLOCKER
despite the benign name. Required fix: a non-invertible derived representation + the non-retention test.

## Anti-patterns
- ❌ Trusting a field name. ❌ "Temporary" raw storage. ❌ Shipping without the non-retention test.
