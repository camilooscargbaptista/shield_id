---
id: wf-plan-phase
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~500
description: Goal-backward planning + plan-check loop.
---

# plan-phase

> Goal-backward, not forward. "What must be TRUE for the goal?" → `must_haves`.

## Steps
1. Orchestrator derives `must_haves: {truths, artifacts, key_links}` (ORCHESTRATOR §4) — each truth a
   checkable claim, each artifact a path, each key_link a grep/probe pattern.
2. A plan-check pass validates the plan: scope not shrunk (no "v1/stub/static for now" — M4), eval-scenarios
   present (rule 11), no from-scratch detector (rule 05), no raw-biometric field (rule 04).
3. Revision loop capped at **3 iterations → escalate to Camilo** (a Revision gate). Never loop forever.
4. **Never split by technical layer** — use SPIDR axes (rule 14).

## Worked example (must_haves)
Goal "reproducible cross-generator number for the doc detector":
truths = [held-out C recall@FPR with CI; robustness delta is headline; no raw doc persisted];
artifacts = [layers/detector.py, eval/cross_generator.py, reports/…md, notebooks/…ipynb];
key_links = [detector loads a fine-tuned base; cross_generator holds out C; no_raw_biometric passes].

## Anti-patterns
- ❌ Forward "what to build" planning. ❌ Layer-split phases. ❌ Prose must_haves (must be checkable). ❌ >3 revision loops.
