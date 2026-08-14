# T-FIX-02 — Hardening do guard `metric_honesty`   (governança / EPIC-FRAMEWORK-EVOLUTIONS)

**Leia primeiro:** `AGENTS.md` · `.agent/CONSTITUTION.md` · `scripts/guards/metric_honesty.py` ·
`tests/fixtures/port2/experiment_defect.md` · `tests/fixtures/port2/eval_report_clean.md` ·
`scripts/agent/verify_eval.py` (só a kill-list, para alinhamento de linguagem)

**Objetivo (1 frase):** fechar os buracos que deixam um relatório desonesto passar o gate determinístico,
mantendo o caso limpo verde (prova bidirecional).

**Os buracos (verificados pelo Oráculo em 2026-08-13, por execução):**
1. `METRIC = \b\d{2,3}(?:\.\d+)?\s*%` não captura: frações nomeadas (`recall = 0.96`) nem `%` de
   1 dígito (`FPR 0.3%`). O fixture de defeito plantado **passa** o guard hoje (exit 0).
2. O guard não detecta circularidade declarada no próprio artefato (`gpt4` em `train_generators` E
   como `held_out_generator`) — kill-list #1, hoje só o revisor LLM pega.
3. O guard não detecta threshold tunado no held-out declarado no artefato — kill-list #4.

**Faça:**
1. Amplie `METRIC` para: `\b\d{1,3}(?:\.\d+)?\s*%` E um segundo padrão de fração nomeada:
   `\b(recall|precision|fpr|tpr|fnr|auroc|auprc|accuracy|f1|robustness[ _-]?delta)\b[^=:\n]{0,25}[=:]\s*-?[01]?\.\d+`.
2. Atualize `TARGET_ADJ` para cobrir as novas formas numéricas (mesma janela de 12 chars — LC-004;
   NÃO alargar a janela).
3. Novo check determinístico de **circularidade**: parseie `train_generators\s*[=:]\s*\[(...)\]` e
   `held_out_generator\s*[=:]\s*["']?(\S+)`; se o held-out estiver na lista de treino → BLOCK nomeando
   I4/D8. (Se os campos não existirem no artefato, não bloqueia — isso é papel do revisor LLM.)
4. Novo check heurístico de **threshold-no-held-out**: verbo de tuning
   (`sweep|swept|sweeping|tun\w+|varr\w+|selected|picking|maximiz\w+`) a ≤80 chars de `held-?out|test split`
   → BLOCK — EXCETO se houver negação adjacente ao verbo (`not|never|não|nunca` a ≤12 chars antes;
   mesma filosofia de adjacência do LC-004). Obrigatório: o fixture limpo contém "NOT tuned on the
   held-out set" e DEVE continuar passando.
5. Fixtures de regressão novos em `tests/fixtures/guards/`: `mh_fraction_defect.md` (métrica como
   fração, sem cross-generator), `mh_onedigit_defect.md`, `mh_circularity_defect.md`,
   `mh_threshold_sweep_defect.md`, `mh_clean_negation.md` (com a negação). Teste pytest
   `tests/test_guard_metric_honesty.py` que roda o guard via `subprocess` contra cada fixture e afere
   exit codes.
6. Rode o guard contra TODOS os `.md`/`.py` versionados fora de `.agent/`/`.context/` e cole a lista de
   novos flags no bundle. Cada falso positivo novo se resolve com rotulagem honesta no arquivo
   (`target`/`exemplo` adjacente) — NUNCA alargando isenção de escopo ou janela.

**Restrições (rules aplicáveis):** 05 · 07 · 15 · 28 (major → ADR via T-ADR-01)
**Saída (artefato + caminho):** `scripts/guards/metric_honesty.py` · fixtures ·
`tests/test_guard_metric_honesty.py`
**Done quando (verificável + evidência colada — M1):** prova bidirecional no bundle:
`experiment_defect.md` → **exit 1 nomeando circularidade E threshold-sweep E métrica** ·
`eval_report_clean.md` → **exit 0** · os 5 fixtures novos com exit codes corretos · suíte pytest
completa verde · varredura do repo colada com zero FP não-resolvido.
**Anti-padrões (proibidos):** alargar `PEDAGOGICAL_PREFIXES` · alargar a janela de 12 chars ·
desligar check existente · exit 0 em caso de erro de parse (fail-open) — erro de parse = BLOCK
com mensagem.
**Atualizar:** CONTROL.md (status `READY_FOR_ORACULO` + Log) · bundle em `.agent/cli/evidence/T-FIX-02.md`.
