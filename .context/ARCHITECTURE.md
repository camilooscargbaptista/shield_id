---
id: architecture
version: 1.0.0
last_updated: 2026-06-18
next_review: 2026-09-15
description: SSOT summary of the SHIELD-ID architecture. The comprehensive C4/UML/AWS/flows/DB doc lives in docs/.
---

# SHIELD-ID — Architecture (SSOT summary)

> **The comprehensive document is `docs/03-architecture/source/Architecture_C4_v0.1_EN.md`** (C4 L1–L4, UML class diagram, AWS v0
> reference, sequence diagrams, full PostgreSQL data model, security/observability, and the ML/Eval subsystem).
> This file is the short single-source-of-truth pointer (rule 29/SSOT) — do not duplicate the doc here.

## The shape in 6 lines
- **Detection API** (FastAPI `/api/v1/`) → explainable **trust score** + per-factor contributions + verification token.
- **Layer 1** multimodal detection (fine-tuned, documents first — D9), **Layer 2** behavioral GNN (**derived
  vectors only — I1**), **Layer 3** anchoring (specified only).
- **Data:** PostgreSQL holds derived vectors + hashed anchors + an **immutable audit trail** — **no raw biometric**.
  Synthetic red-team media lives in S3 (I2).
- **Eval:** cross-generator harness (I4) certified by an **isolated independent evaluator** (M5/D4).
- **AWS v0 (proposed, §8):** ECS Fargate + RDS Postgres + S3 + GPU Batch/SageMaker + Secrets Manager. No Stripe.
- **Stack:** Python-pure (D1); NestJS deferred (D2).

## Status & open ratifications
- The C4 satisfies the rule-10 C4 gate. **Ratify before building against:** the AWS v0 reference (§8) and
  decisions **D7** (Layer-2 data), **D8** (cross-generator — already enforced), **D9** (one modality).
- Layer 2 is specified/simulated this phase (D7); Layer 3 is reference-only.
