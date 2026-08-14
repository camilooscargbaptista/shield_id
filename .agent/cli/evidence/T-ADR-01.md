# Evidence Bundle — T-ADR-01 (ADR das mudanças em guards + lições)

**Branch:** `exp/hardening-pre-training` · **Estado:** `READY_FOR_ORACULO` · **Data:** 2026-08-13
**Validador:** Oráculo EXTERNO. rules 20 · 28 · 29. **Só documentação — nenhum guard tocado.**

## 1. Plano executado (≤10 linhas)
1. Criar `ADR-0010` (template oficial) em `../../docs/06-governance/adr/` cobrindo os 4 blocos (a/b/c/d).
2. Atualizar o índice `../../docs/06-governance/adr/README.md` com a ADR-0010.
3. `.context/LESSONS-LEARNED.md`: LC-005 (split disjunto construído) + LC-006 (guard sem prova bidirecional é folclore).
4. `.context/METRICS.md`: contagens reais (guards py 7→8, epics 5→6).
5. Bump de versão dos 2 arquivos versionados (rule 28: editar sem bump = history-cheating).
6. CONTROL.md: T-ADR-01 `READY_FOR_ORACULO`, quitar a pendência do Log de 22/jun.

## 2. Diff-stat + arquivos tocados
**No repo (git-tracked):** `.context/LESSONS-LEARNED.md`, `.context/METRICS.md`, `.agent/cli/CONTROL.md`, `.agent/cli/evidence/T-ADR-01.md`.
**Externos ao repo (`../../docs/`, NÃO git-tracked aqui — o task os coloca lá):**
`docs/06-governance/adr/ADR-0010-guard-hardening-and-falsepositive-scope.md` (novo, 93 linhas) + `docs/06-governance/adr/README.md` (índice).
Nenhum arquivo de guard, state, hook ou approval-log tocado.

## 3. Saídas REAIS — diffs dos 4 arquivos

### 3.1 ADR-0010 (novo) — segue o template completo
Cabeçalhos (template: Status/Context/Decision/Consequences/Alternatives):
```
1: # ADR-0010 — Endurecimento dos guards críticos e escopo de falso-positivo
3: **Status:** accepted · **Data:** 13 ago 2026 · **Decisores:** Camilo · **Origem:** rule 28 ...
9: ## Contexto
18:## Decisão
20:  ### (a) 2026-06-22 — Escopo de falso-positivo em no_raw_biometric e no_hardcoded
29:  ### (b) 2026-07-21 (PORT-1.1) — Isenção pedagógica + adjacência no metric_honesty (LC-004)
36:  ### (c) 2026-08-13 (esta sprint) — Fail-open e hardening determinístico
54:  ### Prova bidirecional obrigatória
59:## Consequências
69:## Alternativas consideradas
79:## QUESTION para o lead (risco residual — decisão pendente)   <-- bloco (d)
```
Os 4 blocos exigidos: (a) jun/22, (b) jul/21 LC-004, (c) esta sprint (inclui "o fixture de defeito passava
o gate determinístico 22 dias"), (d) risco residual como QUESTION (isenção pedagógica cobre
`.agent/epics/*/state/` — verificado `_is_pedagogical(...)=True` sobre `verification-*.json` reais).

### 3.2 Índice ADR (`README.md`) — linha da ADR-0010
```
18:| 0010 | Endurecimento dos guards críticos + escopo de falso-positivo (...) | rule 28 | accepted |
21:Governança de guards: **ADR-0010** (mudanças major em guards críticos — sprint HARDENING-PRE-TRAINING).
```

### 3.3 `.context/LESSONS-LEARNED.md` (diff)
```
-version: 1.0.0            +version: 1.1.0
-last_updated: 2026-06-17  +last_updated: 2026-08-13
+| LC-005 | Split disjunto é propriedade CONSTRUÍDA, não assumida. ... (T-FIX-01) | _split_controls + _shard_controls + tests/test_training_split.py |
+| LC-006 | Guard sem prova bidirecional automatizada é folclore. O fixture de defeito passou 22 dias verde ... | tests/test_guard_failclosed.py + test_guard_metric_honesty.py; ADR-0010 |
```

### 3.4 `.context/METRICS.md` (diff)
```
-version: 1.0.0            +version: 1.1.0
-last_updated: 2026-06-17  +last_updated: 2026-08-13
-**Framework health:** ... guards (py) 7 ... epics 5.
+**Framework health:** ... guards (py) 8 ... epics 6.
```
Contagens verificadas por `ls`: `scripts/guards/*.py` = 8 (framework_selfcheck, index_drift, metric_honesty,
no_hardcoded, no_raw_biometric, no_real_pii, secret_scan, src_gate); epic dirs = 6 (AITA-V1, DETECTION-API,
EVAL-HARNESS, FRAMEWORK-EVOLUTIONS, PILOT-PATHWAY, REDTEAM-DATASET). guards (md)=7 já estava correto.

### 3.5 LC numeradas sem colisão
```
$ grep -oE "LC-00[0-9]" .context/LESSONS-LEARNED.md | sort -u
LC-001 LC-002 LC-003 LC-004 LC-005 LC-006   (únicas, sem colisão)
```

### 3.6 Pré-requisitos e higiene
```
$ PYTHONPATH=src python3 -m pytest tests/ -q                 -> 42 passed (nada quebrou; task é só doc)
$ bash .githooks/pre-commit (staged .context + evidence + CONTROL) -> pre-commit gates: OK
.context/LESSONS-LEARNED.md e METRICS.md: pedagogical-exempt=True (metric_honesty não os varre).
```

## 4. Autoavaliação contra o "Done quando" (✓/✗)
- [✓] ADR segue o template completo (Status/Contexto/Decisão/Consequências/Alternativas) — §3.1.
- [✓] Os 4 blocos de mudança (a/b/c/d) presentes; (c) inclui o achado do fixture verde 22 dias; (d) QUESTION p/ o lead.
- [✓] Índice ADR atualizado — §3.2.
- [✓] LCs numeradas sem colisão (LC-005, LC-006) — §3.5.
- [✓] `METRICS.md` com contagens reais (8 py / 6 epics) — §3.4.
- [✓] Diff dos 4 arquivos no bundle — §3.1–3.4.
- [✓] Anti-padrões evitados: ADR NÃO genérico (4 blocos concretos); nenhuma rule nova criada; NENHUM guard tocado.

## 5. Riscos / observações para o Oráculo
- **ADR-0010 + índice são EXTERNOS ao repo `shield_id`** (`../../docs/`, confirmado: não é git-tracked por
  este repo — o task os endereça lá). Portanto NÃO entram no commit git desta task; existem no disco e
  estão colados/resumidos acima. O commit desta task cobre só os arquivos in-repo (`.context/*` + bundle + CONTROL).
- **Bump de versão dos 2 arquivos `.context/`** (1.0.0→1.1.0, minor: adição backward-compatible por rule 28):
  fora da lista literal de "Saída" mas exigido pela própria rule 28 que o ADR documenta (editar versionado
  sem bump = history-cheating, que bloqueia merge). Sinalizo para adjudicação.
- **QUESTION do ADR (bloco d) é uma decisão REAL pendente do lead**, não retórica: verifiquei que
  `metric_honesty` não varre `.agent/epics/*/state/verification-*.json` (isenção `.agent/` prefix). Aceitar
  (redundante com `verify_eval` isolado) ou estreitar a isenção — decisão do lead.
- **Sem push:** commit local; Oráculo lê o working tree (in-repo) + os arquivos ADR no disco externo.
