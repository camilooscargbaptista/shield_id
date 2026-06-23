# EPIC-DETECTION-API — Layer 1 + Layer 2 + FastAPI

**Status:** planejado · **WS:** A · **Weight:** full · **Maps to:** D-API (entregável Fase 2)
**Depende de:** EPIC-EVAL-HARNESS, EPIC-REDTEAM-DATASET · **Owner:** Camilo · **Version:** 1.0.0

## O que é
Layer 1 (detecção multimodal — **documentos primeiro, D9**; **fine-tune, nunca do zero — rule 05**), Layer 2
(grafo comportamental — **só vetores derivados, I1**; **especificada/simulada nesta fase — D7**), Layer 3
(ancoragem — só especificada), unificadas numa **FastAPI `/api/v1/`** com score explicável + token.

## User stories (do Plano §6)
| US | Descrição | Tasks | Est | Owner | Aceitação |
|----|-----------|-------|-----|-------|-----------|
| US-007 | Layer 1 — detector de documento (fine-tuned) | carregar base · fine-tune head · model-card (sem nº) | L | detection-ml | recall@FPR cross-gen reportado pelo eval-independent |
| US-008 | Layer 2 — grafo comportamental (especificado/simulado — D7) | derivação de features · GNN · explicabilidade | L | detection-ml | só vetores derivados; score por-fator; honesto sobre simulação |
| US-009 | Detection API (/api/v1/verify) | router · envelope · token HMAC · audit imutável | M | detection-ml + security-auditor | contrato verify; sem persistência de cru (I1) |
| US-010 | Layer 3 — ancoragem (especificada, referência) | desenho hash/ledger permissionado | S | detection-ml | spec; sem preimagem biométrica |

## Critério de saída (gate)
Recall@FPR **cross-generator** certificado (eval-independent); latência medida (p50/p95/p99); sem persistência
de biometria crua (teste de não-retenção verde); score explicável por-fator. DELIVERY-GATE 10/10.

## Anti-padrões (proibidos)
- ❌ Treinar detector do zero (rule 05). ❌ Persistir face/voz/doc cru (I1). ❌ Limiar hardcoded (rule 32).
- ❌ Builder reportar número (rule 15). ❌ As 3 modalidades de uma vez (D9).
