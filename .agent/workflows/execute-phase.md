---
id: wf-execute-phase
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~450
description: Build under the gates, one group at a time.
---

# execute-phase

## Steps
1. Confirm the kickoff gates are `/approved` (else `guard-src-edits` blocks — M3).
2. Builder (detection-ml / data-redteam) executes **ONE task group at a time** (rule 14), TDD where
   applicable, atomic commit per task with inline evidence (date + SHA).
3. Builder reports **no metric** (rule 15); writes SUMMARY + model-card (Evaluation section empty) /
   datasheet → `## BUILD COMPLETE`.
4. Privacy + security gates run before merge; then hand to eval-independent (run-eval).

## Hard rules during execution
fine-tune not from-scratch (rule 05) · derived vectors only (rule 04) · thresholds from config (rule 32) ·
synthetic-only data (rule 03) · one modality deep (D9).

## Worked example
Group "backend detection": T-002-a fine-tune head (commit), T-002-b wire to API (commit), T-002-c tests
(commit). No number anywhere. Then verify_eval.py.

## Anti-patterns
- ❌ Building all groups at once. ❌ A number in the SUMMARY. ❌ Editing before gates. ❌ From-scratch training.
