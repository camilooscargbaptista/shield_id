---
id: rule-16-observability
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: MEDIUM
tokens: ~450
description: Structured logs (no PII), eval run logging, health.
---

# 16 — Observability

## The rules
1. **Structured JSON logs:** `trace_id, layer, action, latency_ms`. **Never log raw biometrics or PII** —
   mask (rule 04/13). A log line that could leak a face/voice/document or a CPF is a P0 issue.
2. **Eval run logging:** every run logs params + metrics + artifact paths + git SHA (rule 02/07).
3. **Health endpoint** for the API (`/api/v1/health`): model loaded, dependencies reachable.
4. **No metric in logs as a substitute for a reproducible run** (rule 07) — logs are for ops, not for claims.

## Worked example
❌ `log.info(f"verifying {raw_face_b64}")`. ✅ `log.info("verify", extra={"trace_id": t, "layer": 1, "decision": "flag"})` (no biometric).

## Acceptance checklist
- [ ] JSON logs with trace_id. [ ] No PII/biometric in logs. [ ] Eval runs logged. [ ] Health endpoint.

## Anti-patterns
- ❌ Logging an input that may contain biometric/PII. ❌ Treating a log line as evidence of a metric.
