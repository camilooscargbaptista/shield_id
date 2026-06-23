---
domain: layer1-detection
last_updated: 2026-06-17
maintainers: [detection-ml, eval-independent]
related_rules: [05, 01, 02]
related_adrs: []
confidence: medium
status: active
---

# Knowledge — Layer 1 (Multimodal Synthetic-Content Detection)

## TL;DR
Detect AI-generated faces (diffusion), voices (neural TTS), documents (LLM) at KYC. **Fine-tune existing
open-source detectors; NEVER train from scratch (rule 05).** Start with **documents (D9)** — most tractable,
least saturated, lowest FP cost. The real test is **cross-generator** generalization, not in-distribution.

## Key concepts
- **The arms race is asymmetric.** Generators evolve faster than detectors; beating frontier detectors is a
  losing bet (CTO analysis). Our edge is the integrated system + policy + reproducibility, not a single best model.
- **Financial calibration ≠ media calibration.** Shorter interaction windows, lower-resolution inputs,
  **higher FP cost** than media-deepfake detection. Off-the-shelf media detectors are mis-calibrated here.

## Gotchas (with source)
- **Circularity (LC-001, retrospect 2026-06):** training + testing on the same generators inflates the
  number; it collapses on unseen generators. → hold out generator C by construction (rule 03/05).
- **From-scratch overfit:** a detector trained from random init on our own red-team set memorizes our
  generators' artifacts → great in-distribution, useless cross-generator. → fine-tune a published base.

## Patterns
- Document consistency via transformer; facial artifact via CNN; voice via spectral/AASIST-style. Ensemble,
  calibrated for finance. Report the robustness delta vs the base model.

## Decisions / open risks
- D9 (one modality deep, documents first) — proposed, ratify in DECISION-LOG.
- Open: which published base models to fine-tune (security-auditor must vet the supply chain — rule 13).
