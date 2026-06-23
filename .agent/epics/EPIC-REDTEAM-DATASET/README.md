# EPIC-REDTEAM-DATASET — Open Synthetic Attack Dataset

**Status:** planejado · **WS:** B · **Weight:** full · **Maps to:** D-DATA (entregável Fase 2)
**Depende de:** EPIC-EVAL-HARNESS (splits-manifest) · **Owner:** Camilo · **Version:** 1.0.0

## O que é
Dataset red-team **sintético aberto**: faces/vozes/documentos sintéticos + conjunto de controle legítimo,
com datasheet e scripts reprodutíveis. Sintético-only (I2); **splits cross-generator por construção (I4/D8)**.

## User stories (do Plano §6)
| US | Descrição | Tasks | Est | Owner | Aceitação |
|----|-----------|-------|-----|-------|-----------|
| US-003 | Pipeline de geração reprodutível (documentos primeiro — D9) | gerador docs · versões fixadas · seeds | L | data-redteam | regenera de config+seed |
| US-004 | Splits cross-generator + conjunto de controle | manifest train{A,B}/held-out C · controle legítimo | M | data-redteam | held-out C nunca no treino |
| US-005 | Datasheet + validação de distribuição demográfica | datasheet · tabela demográfica validada | M | data-redteam + fairness-auditor | datasheet completo; distribuição documentada |
| US-006 | Release open-source + benchmark | licença permissiva · baseline | S | data-redteam | publicado; sem dado cru commitado |

## Critério de saída (gate)
Dataset publicado + datasheet + scripts reprodutíveis + splits-manifest (held-out C) + baseline.
`no_real_pii.py` verde; nenhum dado cru commitado (.gitignore).

## Anti-padrões (proibidos)
- ❌ Qualquer PII real (I2). ❌ Todos os geradores no treino (sem held-out). ❌ Sem datasheet. ❌ Versões não-fixadas.
