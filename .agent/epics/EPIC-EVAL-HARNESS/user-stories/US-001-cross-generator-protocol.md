# US-001 — Cross-generator evaluation protocol

**Epic:** EPIC-EVAL-HARNESS · **WS:** B · **Owner agent:** eval-independent

Como avaliador independente, quero um protocolo leave-one-generator-out, para medir generalização real
e não a circularidade (detectar o próprio gerador).

## Acceptance criteria (eval scenarios)
- **Cross-generator:** harness trains on {A,B}, tests on held-out C; outputs robustness delta.
- **Reproducible:** runs from config+seed; notebook produces identical curves.
- **No headline point:** output is ROC/PR + CI, never a single %.

## Tasks
| Task | Description | Owner | Est |
|------|-------------|-------|-----|
| T-001-a | splits-manifest schema (train vs held-out generator) | eval-independent | 1-2h |
| T-001-b | harness: compute P/R@FPR + robustness delta | eval-independent | 2-3h |
| T-001-c | reproducibility notebook + seed | eval-independent | 1-2h |

## Definition of Done
DELIVERY-GATE · cross-generator present · reproducible · no raw biometric/PII.
