# EPIC-EVAL-HARNESS — Live progress (date + SHA + PR por task)

State: em-andamento (US-001 + US-002 construídas e certificadas) · Tasks: 5/5 das US ativas
Gates: [x] kickoff [x] spec [x] c4 [x] eval-plan [x] data [x] implementation [x] eval [ ] verify [ ] pr-opened
(verify/pr-opened aguardam /approved do Camilo + commit)

## User stories
- US-001 — Cross-generator protocol — **certificada PASS_WITH_WARNINGS** (state/verification-eval-harness-us001.json)
- US-002 — Disaggregated fairness — **certificada PASS** (state/verification-eval-harness-us002.json)

## Task log (append, never delete)
- [x] T-001-a/b/c cross-generator harness (2026-06-18) — src/shield_id/eval/{splits,metrics,cross_generator}.py
- [x] EVAL US-001 (independente, isolada) — PASS_WITH_WARNINGS
- [x] T-002-a disaggregated fairness audit (2026-06-18) — src/shield_id/eval/fairness.py (+ tests/test_fairness.py)
- [x] EVAL US-002 (independente, isolada) — PASS

## Follow-ups (do verdict da US-002 — notas, não bloqueios)
- T-002-b: validador de distribuição demográfica do dataset (data-redteam, rule 03) — pendente.
- Acurácia por segmento (além de FPR) + escalonamento humano/contestação para a FAIRNESS-GATE completa.
- Correção de múltiplas comparações com >2 segmentos (hardening); tratamento de segmento vazio.
- (US-001) endurecer metric_honesty (LC-004, já feito) — concluído.

## Metrics
Tasks US-001+US-002 completas: 5/5. Próximo épico (gate de saída): EPIC-REDTEAM-DATASET → EPIC-DETECTION-API.
