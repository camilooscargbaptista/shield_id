---
id: guard-preflight
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: on_demand
priority: HIGH
tokens: ~450
description: Pre-action checklist; read context + verify reality before code.
---

# PREFLIGHT

> Run this mental checklist BEFORE writing any code. Grounds the agent in reality (counters the
> curse-of-knowledge: re-read the codebase as if you'd never seen it).

## The 6 checks
1. **Active experiment?** `status.py` shows one, and the src-gating steps are `/approved` (else the
   `guard-src-edits` hook will block you anyway — M3).
2. **Read the route** (BOOTSTRAP) + the owning rules + the active eval-plan.
3. **Read the eval-plan first** — the harness/cross-generator splits exist before the model (rule 05).
4. **Verify reality:** the schema fields / config keys / function signatures you reference actually exist.
   Do **not** invent a column name or a generator (M1/M2).
5. **Privacy pre-check:** does anything you're about to add persist a raw biometric or touch real PII? If
   unsure → STOP (rule 04/03).
6. **Scope:** confirm the files you'll touch are in-scope (M4).

## Worked example
About to write a query against `Identity.face_hash`. Preflight check 4: grep the model — there is no
`face_hash` column (and there must not be — I1). STOP, ask, use the derived vector instead.

## Anti-patterns
- ❌ Coding before reading context. ❌ Inventing a field/key. ❌ Skipping the privacy pre-check.
