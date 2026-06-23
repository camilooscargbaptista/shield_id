---
id: wf-mandatory-checklist
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: CRITICAL
tokens: ~800
description: The law. 4-phase gating for any task, with control verbs and examples.
---

# MANDATORY-CHECKLIST (the law)

> The canonical procedure for any non-trivial task. Composes rules (what), guards (gates), agents (who).

## Phase 0 — Analyze existing
Reuse, never recreate. Load the BOOTSTRAP route. Grep for existing code/patterns before writing anything.
*Ex: need a metric? extend `src/shield_id/eval/`, don't fork it.*

## Phase 1 — Read context
CONSTITUTION + the owning rules for your route + the active eval-plan. Confirm an active experiment
(`status.py`).

## Phase 2 — Kickoff deliverables (gated, each `/approved`)
Per task type, produce in order, each an approval gate that the `guard-src-edits` hook enforces before
`src/` edits:
`spec (eval-scenarios) → c4 (ARCHITECTURE delta) → eval-plan (cross-generator + splits) → [data | model | policy] → threat-model (if money/PII/auth)`.

## Phase 3 — Build
One group at a time (rule 14). TDD where applicable (tests allowed pre-approval). Atomic commit per task.
Builder reports **no metric** (rule 15). Thresholds from config (rule 32). Derived vectors only (rule 04).

## Phase 4 — VERIFY BEFORE COMPLETION
Run each DELIVERY-GATE gate; **paste the output** (M1). For metrics: hand to `eval-independent` (isolated,
M5) — never self-report. DELIVERY-GATE 10/10. Then push. Then `/retrospect` (learning-curator).

## Control verbs
`/approved <step>` · `/rejected <step>` · `/skip-<step>` (logged, discouraged) · `/fast-mode` ·
`/full-mode` (default).

## Worked example (the gate sequence)
"Build the document detector" → P0 grep eval/ + layers/ → P1 read rules 01/02/04/05 → P2 spec→c4→eval-plan
`/approved` (now `src/` unblocks) → P3 fine-tune + commits, no number → P4 verify_eval.py (isolated) →
DELIVERY-GATE → push → retrospect.

## Anti-patterns
- ❌ Skipping Phase 0/1 (recreate instead of reuse, code on wrong assumptions). ❌ Editing `src/` before P2
  gates. ❌ Self-reporting a metric in P4. ❌ Declaring done without pasted evidence.
