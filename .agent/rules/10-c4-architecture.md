---
id: rule-10-c4-architecture
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~500
description: C4 mandatory in Mermaid; lives in .context/ARCHITECTURE.md; approval gate.
---

# 10 — C4 Architecture

All four C4 levels (Context, Container, Component, Code-as-needed) in **Mermaid**, authored in
`.context/ARCHITECTURE.md` (the SSOT for architecture). This is the C4 doc the Prototype Plan §6 references
and the CTO analysis flagged as gap #1 — instantiate the structural template from `modelo_documentacao/`
(D6: structure only, never Acesso-Imigra domain), adapt to Python/ML, and **add the ML sections** the CRUD
template lacks: model cards, training methodology, eval harness + cross-generator protocol, datasheet,
MLOps/retraining, fairness methodology.

## Gate
The C4 is an approval gate in the kickoff sequence (WORKFLOW-ENFORCEMENT): `c4` must be `/approved` before
`src/` edits (the `guard-src-edits` hook enforces it).

## Acceptance checklist
- [ ] L1 Context (actors: FI/KYC, regulator, red-team). [ ] L2 Containers (API, Layer1, Layer2, harness, data).
- [ ] ML sections added (not just the CRUD shell). [ ] No raw-biometric store in the data model. [ ] Approved.

## Anti-patterns
- ❌ Importing Acesso-Imigra domain content (D6). ❌ Skipping the ML sections. ❌ ASCII diagrams (use Mermaid).
