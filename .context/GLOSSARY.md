---
id: glossary
version: 1.1.0
last_updated: 2026-06-17
next_review: 2026-08-16
description: Ubiquitous language (SSOT). New term → here, or PR rejected (rule 29). One canonical term per concept.
---

# Glossary

| Term | Canonical | Definition | Non-confusables |
|------|-----------|------------|-----------------|
| Trust score | `trust_score` | Explainable, per-factor confidence from Layer 2. | NOT "confidence/risk score" |
| Contributing factor | `ContributingFactor` | One behavioral feature's signed contribution to the trust score. | — |
| Derived feature vector | `feature_vector` | Behavioral signal representation; the ONLY thing Layer 2 stores (never raw biometric). | NOT "embedding" if invertible |
| Raw biometric | — | A face image / voice sample / document scan in its original form. **Never persisted (I1).** | — |
| Cross-generator | — | Eval protocol: train on generators {A,B}, test on held-out C (rule 05). | NOT "cross-validation" |
| Robustness delta | — | Accuracy drop in-distribution → cross-generator (and standard → stress). The headline. | — |
| Held-out generator | `held_out_generator` | The generator (C) excluded from training entirely (rule 03). | — |
| Red-team set | — | Fully synthetic attack dataset + synthetic control set (I2). | NOT real attack data |
| Disaggregated FPR | — | False-positive rate per demographic segment; the PRIMARY fairness metric (rule 06). | NOT global FPR |
| Verification token | `VerificationToken` | Cryptographic token returned with a trust score for audit. | — |
| AITA | — | AI Identity Trust Architecture; the 4-layer policy framework. | — |
| Cascaded Accountability | — | AITA L4: sequential liability AI-provider → institution → regulator. | — |
| Eval-independent | — | The agent that certifies metrics in an isolated session (M5/D4); never the builder. | NOT "the reviewer" |
