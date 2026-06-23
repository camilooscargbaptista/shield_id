---
id: bootstrap
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-08-16
trigger: on_demand
priority: HIGH
tokens: ~600
description: Token-economy router. Given a task type, load ONLY the listed files. Do NOT read everything.
---

# BOOTSTRAP — What to Read (and What NOT to Read)

> The framework is large. Loading it all wastes context (rule = context engineering).
> **If it is not on your task's route, do not read it.** Always-load = CONSTITUTION + the route.

## Always load (every task)
`CONSTITUTION.md` · `rules/00-general.md` · `guards/DELIVERY-GATE.md`

## Routes by task type

| Task type | Also READ | Do NOT read |
|-----------|-----------|-------------|
| **Detection model (Layer 1/2)** | rules 01,02,04,05,07 · agents/detection-ml,eval-independent · templates/model-card,eval-plan · epic EPIC-DETECTION-API | epics/* others · aita-policy |
| **Red-team data** | rules 02,03,05 · agents/data-redteam · templates/datasheet · skills/generate-redteam-batch · epic EPIC-REDTEAM-DATASET | api/fastapi rules |
| **Evaluation / metrics** | rules 05,06,07,11,15 · agents/eval-independent,fairness-auditor · templates/eval-plan · skills/run-eval-and-report,audit-demographic-parity | rules 01,12 |
| **API / FastAPI** | rules 01,13,16 · agents/detection-ml,security-auditor · templates/threat-model | redteam/aita |
| **AITA policy (writing)** | rules 20,29 · agents/aita-policy · templates/adr · epic EPIC-AITA-V1 · .context/knowledge/aita-policy.md | all code rules |
| **New epic/feature kickoff** | rules 14 · workflows/new-experiment · templates/epic,user-story,task · guards/PREFLIGHT | — |
| **Bug fix** | rules 08 · workflows/fix-bug · CHEATSHEET-COMPACT | epics/* |
| **Trivial (1–5 lines)** | CHEATSHEET-COMPACT only | everything else |

## Never load without explicit need (context-cost map)
- `epics/*/` other than your active epic (skeletons; high token, low value)
- `.context/LESSONS-LEARNED.md` in full (grep the relevant LC-xxx instead)
- the whole `rules/` directory (load only your route's numbers)
