---
id: cheatsheet
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-08-16
trigger: on_demand
priority: MEDIUM
tokens: ~400
description: Fast path for trivial tasks. The 10 things you must never violate.
---

# CHEATSHEET (fast path)

**The 5 invariants (never violate):** (1) no raw biometrics — derived vectors only ·
(2) no real PII — synthetic only · (3) no metric without notebook+seed+data ·
(4) cross-generator eval mandatory · (5) metrics are targets, report what you measure.

**Before code:** `start_experiment.py <slug>` → human `/approved` the kickoff gates → then edit `src/`.
The `guard_src_edits` hook BLOCKS `src/` edits otherwise.

**Definition of Done:** lint clean · tests green (pasted output) · coverage ≥ target ·
no raw-biometric/PII/secret · committed (Conventional) · **pushed** · eval-independent signed (if metrics).

**M1:** never say "works"/"95%" without pasted evidence this session. M2: unknown → STOP.
M5: you do NOT validate your own metrics — eval-independent does, in an isolated session.

**Commands:** `start_experiment.py` · `approve.py <step>` · `status.py` · `verify_eval.py` · `retrospect`.
