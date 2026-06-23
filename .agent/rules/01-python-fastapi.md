---
id: rule-01-python-fastapi
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~1000
description: Python-pure clean architecture (FastAPI + ML). Layout, conventions, examples. Decision D1.
---

# 01 — Python / FastAPI (stack — decision D1)

**Stack:** Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy + Alembic (only when persistence is needed),
pytest, ruff + mypy (strict). **NestJS is deferred to Phase 3 (D2) — do not introduce it.** The API shell
is the easy 20%; ~80% of the hard work is ML, and Python is native for it + reproducibility (notebooks =
the evaluator lingua franca).

## Repository layout
```
src/shield_id/
  api/            # FastAPI routers, /api/v1/, JSON envelope, versioned
  layers/
    layer1_detection/   # fine-tuned detectors (NEVER from scratch — rule 05). Documents first (D9).
    layer2_behavioral/  # GNN over DERIVED feature vectors only (rule 04 / I1)
    layer3_anchoring/   # specified/reference only this phase
  eval/           # harness, metrics, cross-generator protocol (built BEFORE models)
  data/           # synthetic generation (no real PII — rule 03)
  schemas/        # pydantic models: TrustScore, ContributingFactor, VerificationToken
  config.py       # ALL thresholds/paths/seeds (rule 32 — nothing hardcoded in logic)
tests/            # pytest; tests allowed before kickoff approval (TDD red)
notebooks/        # reproducible eval notebooks (seed pinned — rule 07)
```

## Conventions
- **Response envelope:** `{"data": ..., "success": true, "trace_id": "..."}`; errors `{"error": {"code","message"}, "success": false}`.
- **Typed everywhere.** `mypy --strict` clean. Pydantic v2 models for all I/O. No `Any` without justification.
- **Size limits:** functions ≤ 50 lines, modules ≤ 500 (extract a service if larger).
- **No raw biometric** persisted at any layer (I1). **No hardcoded thresholds** (rule 32) — read `config`.
- **The trust score is explainable:** return per-factor contributions, never an opaque scalar.

## Worked example (the explainability convention)
❌ `return {"score": 0.83}`. ✅ `return TrustScore(score=0.83, factors=[ContributingFactor("typing_cadence", -0.05), ...], token=...)`.

## Acceptance checklist
- [ ] ruff + mypy --strict clean. [ ] /api/v1/ versioned, envelope used. [ ] no raw biometric field.
- [ ] thresholds from config. [ ] functions ≤50 / modules ≤500.

## Anti-patterns
- ❌ Introducing NestJS (D2). ❌ Returning an opaque score. ❌ Inline thresholds. ❌ Untyped public functions.
