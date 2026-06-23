---
id: wf-new-experiment
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~550
description: Kickoff a new experiment/feature, gate by gate.
---

# new-experiment

## Steps
1. `python scripts/agent/start_experiment.py <slug> --type <experiment|api|dataset|policy>` → writes
   `state/current-experiment.json` with the ordered gate steps for that type.
2. Orchestrator P0–P1 (ORCHESTRATOR.md): parse + the 17 interrogation questions + size (XS→XL, rule 14).
   Decompose with SPIDR if too big. Resolve every "unknown" or HALT (M2).
3. Produce kickoff deliverables gate by gate: `spec → c4 → eval-plan [→ threat-model | datasheet]`, each
   `python scripts/agent/approve.py <step>` (the human gate).
4. Only after the required src-gating steps are approved does `guard-src-edits` allow `src/` edits (M3).
5. Hand to the builder (workflows/execute-phase).

## Type → step set (from scripts/lib/state.py)
- `experiment`: kickoff→spec→c4→eval-plan→data→implementation→eval→verify→pr-opened
- `api`: kickoff→spec→c4→threat-model→implementation→eval→verify→pr-opened
- `dataset`: kickoff→datasheet→data→eval-plan→verify→pr-opened
- `policy`: kickoff→outline→draft→framework-alignment→review

## Worked example
`start_experiment.py doc-detector --type experiment` → status shows gates → `/approved spec`, `/approved c4`,
`/approved eval-plan` → src unblocks → build.

## Anti-patterns
- ❌ Starting code without `start_experiment`. ❌ Approving your own gates (human approves). ❌ Skipping eval-plan.
