---
domain: layer2-behavioral
last_updated: 2026-06-17
maintainers: [detection-ml, privacy-ethics-review]
related_rules: [04, 02]
related_adrs: []
confidence: low
status: active
---

# Knowledge — Layer 2 (Behavioral Trust Graph / GNN)

## TL;DR
A GNN over **derived feature vectors** (typing cadence, device consistency, geolocation coherence, session
timing) producing an explainable, per-factor trust score. The lead's strongest area and the real
differentiator — **but it has no real data source this phase.**

## Key concepts
- **Derived vectors ONLY — never raw biometrics (I1, rule 04).** The GNN models relations between behavioral
  features, not raw signals. No raw face/voice/document ever persisted.
- **Explainability is structural:** output per-factor contributions (rule 01), never an opaque scalar.

## Gotchas (with source)
- **No longitudinal behavioral data this phase (LC-003, D7).** A behavioral GNN needs many sessions per
  identity over time. With "no real PII" + "no live deployment", there is **no honest data source** to
  *measure* Layer 2 accuracy this phase. → **specify/simulate and say so**; never claim measured behavioral
  accuracy without a data source. Escalate to PSP-data if it unblocks (D7 option B).
- **Invertibility trap:** a "derived" embedding that can be inverted to the raw biometric is still raw
  biometric (privacy-ethics-review checks this, not the field name).

## Decisions / open risks
- D7 (Layer 2 data source) — proposed: specify/simulate, escalate to PSP. Ratify in DECISION-LOG.
- Open: cold-start (a first-ever session has no behavioral history).
