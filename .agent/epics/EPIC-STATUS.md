---
id: epic-status
version: 1.2.0
last_updated: 2026-07-21
next_review: 2026-08-16
trigger: on_demand
priority: HIGH
tokens: ~350
description: Portfolio index of all Phase-2 epics. Synced with docs/04-planning Delivery Plan §6.
---

# EPIC STATUS — Portfolio Index

> Sincronizado com o **Plano de Entrega Fase 2** (`docs/04-planning`) §5–6. Não carregue épicos `planejado`
> sem necessidade. Sequenciamento: EVAL-HARNESS → REDTEAM-DATASET → DETECTION-API; AITA-V1 paralelo; PILOT ao fim.

| Épico | WS | Status | USs | Read? | Notas |
|-------|----|--------|-----|-------|-------|
| EPIC-EVAL-HARNESS | B | **em-andamento** | US-001 ✓cert · US-002 ✓cert | **YES** | harness + cross-gen; US-001+US-002 certificadas; próximo: REDTEAM-DATASET |
| EPIC-REDTEAM-DATASET | B | **em-andamento** | US-003..006 ✓baseline | sob demanda | pipeline+datasheet+baseline (procedural); geradores reais pendentes |
| EPIC-DETECTION-API | A | **em-andamento** | US-007 código✓ (treino na GPU) | sob demanda | detector texto-LLM real escrito (D11); treino pendente de GPU |
| EPIC-AITA-V1 | C | **em-andamento** | US-011..013 | sob demanda | **draft v1.0 pronto** em docs/05-policy; pendente engajamento |
| EPIC-PILOT-PATHWAY | D | planejado (plano escrito) | US-014..016 | sob demanda | plano em docs/04-planning; ≥1 engajamento (PSP/BACEN/IEEE) |
| EPIC-FRAMEWORK-EVOLUTIONS | B | **em-andamento** | PORT-1 ✓ · **PORT-1.1 ✓** · PORT-2/3 planejados | sob demanda | PORT-1.1 (2026-07-21): pre-push corrigido (era fail-open) + classe F (hygiene) no selfcheck; **pendente humano**: `git add` dos arquivos do framework + configurar remote (CI nunca rodou) — ver CHANGELOG 1.1.0 |

Lifecycle: `planejado` → `em-andamento` → `completo`. Detalhe das US/tasks: ver o README de cada épico + Plano §6.
