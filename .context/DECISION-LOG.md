---
id: decision-log
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
description: Locked project decisions D1-D9 (binding) + ADR index. SSOT owner for decisions.
---

# Decision Log — SHIELD-ID (binding unless overridden in-session by Camilo)

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| D1 | Stack: Python-pure (FastAPI + ML) for the prototype | ~80% of the hard work is ML; reproducibility | accepted |
| D2 | Defer NestJS / hybrid to Phase 3 | optimizes the easy 20%; only matters at production | accepted |
| D3 | Build 100% via Claude Code + Cowork; lead does spec→orchestrate→review | plays to architect strengths | accepted |
| D4 | **Separate build agent from independent evaluator; no self-reported metric without reproducible artifact** | the deliverable is a number evaluators reproduce | accepted |
| D5 | Metrics are targets to test, not promises; report measured outcomes | honesty beats an aspirational number | accepted |
| D6 | Acesso Imigra is a separate confidential project; reuse structure only, never domain/IP | keeps IP clean | accepted |
| D7 | **Layer 2 data source** — specify/simulate this phase (escalate to PSP data if it unblocks) | no longitudinal behavioral data exists this phase | accepted |
| D8 | **Cross-generator evaluation protocol mandatory** (leave-one-generator-out) | neutralizes the circularity trap | accepted |
| D9 | **Layer 1: one modality deep (documents) + two reference** | 3 modalities is over-scoped for a solo team | accepted |
| D10 | **Fase 2 permanece em nível de docs/planejamento; código é POC e só avança após ratificação explícita.** "Build" (D3) significa gerar código via agente — não disparar sem o lead confirmar a frente de código. | Evitar gerar produto/detector sem decisão deliberada; o valor desta fase está majoritariamente em docs/planejamento/política. | accepted (18 jun 2026) |
| D11 | **Código de produto retomado (sai da pausa D10).** 1º detector = **texto gerado por LLM** (consistência documental, Layer 1, D9); fine-tune de transformer pré-treinado (rule 05); treino em **nuvem GPU (AWS/Colab)**. O ambiente do agente escreve o código real; o treino roda na GPU do lead. | Camilo autorizou construir o produto de verdade; ambiente do agente não tem GPU/rede p/ modelos. | accepted (18 jun 2026) |

> D7–D9 ratified 2026-06-18 per project-lead instruction ("siga"). Remain overridable in-session.
> Any major rule change (rule 28) records an ADR here.

## ADR index
(none yet — first major rule bump will add ADR-001)
