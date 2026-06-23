---
id: rule-04-privacy-biometrics
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~900
description: Never persist raw biometrics. Derived vectors only. Invertibility check. SSOT owner: privacy.
---

# 04 — Privacy & Biometrics (SSOT owner: privacy)

> **Invariant I1: Never persist raw biometrics. Derived feature vectors only.**
> Enforced by `scripts/guards/no_raw_biometric.py` (pre-commit, exit 1 — proven to block).

## Why this is structural, not cosmetic
A centralized biometric store is (a) the highest-value breach target imaginable and (b) a ready-made
surveillance instrument. Removing it is not compliance theater — it is the project's **core value
proposition (trust/privacy) compiled into the architecture.** It also shrinks liability and attack surface.

## The rules
1. **Layer 2 operates on derived feature vectors only** — typing cadence, device consistency, geolocation
   coherence, session timing — never the raw face/voice/document blob.
2. **No centralized biometric database.** No cross-institution identity correlation outside a governed,
   explicit threat-intelligence agreement.
3. **The "derived" test is invertibility, not the field name.** A near-lossless autoencoder latent that can
   be inverted back to the raw biometric is **still raw biometric**, whatever you call it. privacy-ethics-
   review checks invertibility, not the column name.
4. **Verifiable non-retention.** There MUST be an automated test that FAILS if any schema field persists a
   raw biometric. "How we prove zero retention" is itself a Phase-2 deliverable.
5. **Data minimization** at every collection point; **PII masked in logs** (rule 16); GDPR/LGPD aligned.

## Worked examples
- ❌ `raw_face = Column(LargeBinary)` → blocked (I1).
- ❌ `face_embedding = Column(LargeBinary)` where the embedding is invertible → blocked (name doesn't save it).
- ✅ `typing_cadence_vector = Column(JSON)` (derived behavioral feature) → allowed.

## Non-retention test (the deliverable)
```python
def test_no_raw_biometric_field_persists():
    # fails if any ORM column on an identity table is a raw face/voice/document blob
    assert not any(is_raw_biometric(col) for col in Identity.__table__.columns)
```

## Anti-patterns (forbidden)
- ❌ Persisting any raw biometric "temporarily" or "for re-verification". ❌ Trusting a field name.
- ❌ Shipping without the non-retention test. ❌ Logging an un-masked biometric/PII value.
