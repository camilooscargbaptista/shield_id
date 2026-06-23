---
id: rule-13-security
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: on_demand
priority: HIGH
tokens: ~700
description: Security of the API AND the build pipeline itself. STRIDE, supply-chain, secrets.
---

# 13 — Security

The product's value IS security; the **build pipeline must be secure too** (100%-agent-built, D3 — the
CTO-analysis §7 gap). security-auditor owns this.

## The rules
1. **STRIDE threat model** for the Detection API (templates/threat-model). Mandatory if money/auth/PII/external.
2. **Dependency supply-chain:** pin versions; flag typosquatting/slopsquatting on ML packages (a real vector
   when an agent runs `pip install`). Review the manifest in code review.
3. **Secrets:** none in code/logs (`secret_scan.py` blocks). PII masked in logs (rule 16).
4. **Prompt-injection in data:** red-team/external inputs may carry injection payloads → review the ingestion path.
5. **Auth + rate limiting** on any non-public endpoint. **Layer-3 ledger** permissioned, no cross-institution
   correlation (specify only this phase).

## Worked example (supply-chain)
A PR adds `pip install reqeusts` (typo of `requests`) → potential malicious package. security-auditor
BLOCKs and flags the supply-chain risk. Pin: `requests==2.32.3`.

## Acceptance checklist
- [ ] STRIDE table present (if triggered). [ ] Deps pinned, no typosquat. [ ] No secret in code/logs.
- [ ] PII masked in logs. [ ] Auth + rate limit on protected endpoints.

## Anti-patterns
- ❌ Reviewing the API but ignoring the pipeline. ❌ Unpinned deps. ❌ Logging raw inputs (may contain PII).
