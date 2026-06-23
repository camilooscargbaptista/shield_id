# US-002 — Disaggregated fairness metrics (FPR-under-parity)

**Epic:** EPIC-EVAL-HARNESS · **WS:** B · **Owner agent:** fairness-auditor (depends_on eval-independent)

Como auditor de fairness, quero métricas de FPR desagregadas por segmento com teste de significância,
para garantir que a acurácia não degrade desproporcionalmente nas populações que mais queremos proteger.

## Acceptance criteria (eval scenarios)
- **Parity:** per-segment accuracy + FPR table; each gap tested for statistical significance (p-value shown).
- **Primary metric:** disaggregated FPR is primary; global FPR secondary (rule 06).
- **Dataset validity:** the dataset's demographic distribution is validated (rule 03) before any claim.

## Tasks
| Task | Description | Owner | Est |
|------|-------------|-------|-----|
| T-002-a | per-segment FPR + significance test | fairness-auditor | 2-3h |
| T-002-b | datasheet demographic-distribution validator | data-redteam | 1-2h |

## Definition of Done
DELIVERY-GATE · disaggregated table reported · no significant gap (or mitigation plan) · FAIRNESS-GATE pass.
