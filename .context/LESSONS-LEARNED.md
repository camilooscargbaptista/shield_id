---
id: lessons-learned
version: 1.2.0
last_updated: 2026-08-14
next_review: 2026-09-15
description: Lessons (LC-xxx). Each should graduate into a guard/rule (retrospect → guard).
---

# Lessons Learned

> A lesson that stays markdown is folklore. Each LC should become an executable guard or a rule.

| ID | Lesson | Became |
|----|--------|--------|
| LC-001 | The circularity trap: testing detection on your own generators inflates the number. | rule 05 + `metric_honesty.py --require-cross-generator` (guard) |
| LC-002 | A flat global FPR can hide a high minority FPR. | rule 06 (disaggregated FPR primary) + FAIRNESS-GATE |
| LC-003 | Layer 2 has no behavioral data source this phase. | D7 (specify/simulate, escalate to PSP) |
| LC-004 | The `metric_honesty` guard whitelisted a whole file if the word "target" appeared anywhere — an in-distribution metric could bypass it. Found by **eval-independent** during US-001 certification (the judge caught what the builder missed). | Hardened `scripts/guards/metric_honesty.py`: the target-exemption must now be ADJACENT to the number (re-tested: bypass blocked, honest/target pass). The lesson became a guard fix, not just a note. |
| LC-005 | **Split disjunto é propriedade CONSTRUÍDA, não assumida.** O mesmo conjunto de controle (label=0) era concatenado em train E held-out em todos os caminhos de split — o FPR cross-generator seria medido sobre negativos já vistos no treino (kill-list #2). Achado pelo Oráculo antes do primeiro treino real (T-FIX-01). | Split de controle DISJUNTO e determinístico por `sha256` (rule 07, sem RNG) em `train_text_detector.py::_split_controls` + `redteam.py::_shard_controls`, com verificação defensiva `ValueError` (I4) e testes de disjunção/determinismo (`tests/test_training_split.py`). |
| LC-006 | **Guard sem prova bidirecional automatizada é folclore.** O fixture de defeito plantado do `metric_honesty` passou o gate determinístico VERDE por 22 dias (frações/1-dígito/circularidade/threshold-sweep eram invisíveis ao regex); o `no_raw_biometric` não escaneava nada de um cwd sem `src/` (fail-open por precedência). | Toda mudança de guard passa a exigir prova bidirecional AUTOMATIZADA (violação sintética→BLOCK · limpo→OK) com fixtures versionados: `tests/test_guard_failclosed.py`, `tests/test_guard_metric_honesty.py`. Consolidado em ADR-0010 (rule 28). |
| LC-007 | **Prova de hook se faz com stdin-contract ou worktree descartável, NUNCA com `--no-verify`** (rule 08 é absoluta). Incidente auto-reportado: os temp-commits do harness de prova da T-FIX-05 usaram `--no-verify`, o que o `guard-bash-bypass` registrou como `bypass_used` no `approval-log` (append-only, preservado); os commits reais nunca usaram bypass. | Prática adotada: provar um hook dirigindo-o pelo **contrato de stdin do git** (`printf '<ref> <local> <ref> <remote>' \| bash .githooks/pre-push`) ou num **worktree/branch descartável** — jamais contornando o gate. Reforço do `guard-bash-bypass` (o bypass já é auditado; a lição fecha o loop humano). |
