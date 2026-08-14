# SHIELD-ID — CONTROL (doc vivo de controle)

> **Heartbeat do projeto.** O Claude Code LÊ este arquivo PRIMEIRO e o ATUALIZA por ÚLTIMO (toda sessão).
> É a fonte única de "onde estamos / qual é a próxima". Mantenha curto. Versione (git) a cada mudança.

## Estado atual
- **Fase:** Global Trust Challenge 2026 — Fase 2 (M1 provisório = jun/2026).
- **Modo (D10/D11):** docs/planejamento livres; **código de PRODUTO** (detector/treino) só com **confirmação explícita do lead**. Treino roda na **GPU (AWS g4dn)**, nunca na sessão do agente.
- **Épico ativo:** EPIC-DETECTION-API.
- **US ativa:** US-007 (detector texto-LLM) — código escrito; treino na GPU pendente de dados.
- **Dataset (decidido pelo lead, 22/jun):** **RAID** (`liamdugan/raid`) — multi-gerador; usar **held-out de 1 gerador** (I4).
- **Próxima ação sugerida:** lead roda o conversor RAID **no box AWS** (`RUN_ON_AWS.md` §3.5) → gera `data/text-redteam.jsonl` + `no_real_pii.py` verde → destrava T-TRAIN-01. (T-CFG-01 ✅ feita; config do treino já casa com o split real.)

## Fila de tarefas (backlog priorizado)
| ID | Tarefa | Épico/US | Status | Prompt |
|----|--------|----------|--------|--------|
| T-DATA-01 | Conversor **RAID** → JSONL `{text,label,generator,segment}` (≥2 geradores, 1 held-out) | REDTEAM/US-004 | **código pronto** (loader+config, py_compile OK); **data-gen movida pro box AWS** (D11) — falta rodar `RUN_ON_AWS.md` §3.5 + `no_real_pii.py` | `.agent/cli/tasks/T-DATA-loader.task.md` |
| T-CFG-01 | Alinhar `TextDetectorConfig` ao split REAL do RAID (treino chatgpt/mistral-chat/mpt-chat + held-out gpt4) | DETECTION/US-007 | **✅ concluída** (py_compile OK; split sanity verificado pelo orquestrador — train não-vazio, gpt4 só held-out; guard de circularidade intacto) | — |
| T-CFG-02 | Unificar o split de geradores num único SSOT (hoje em 3 lugares: `EvalConfig`/`TextDetectorConfig`/`RaidLoaderConfig`) | tech-debt | pendente (baixa prio) | (criar) |
| T-US009-01 | FastAPI `/api/v1/verify` (detector-mock testável aqui) | DETECTION/US-009 | **✅ concluída** (10/10 pytest + py_compile + 4 guards verdes, verificado pelo orquestrador; curl real PASS/REVIEW/FLAG com score+fatores+token+trace_id; I1 ok — input cru nunca persistido/ecoado). **Não commitada ainda.** | `.agent/cli/tasks/T-US009-api.task.md` |
| T-SEC-01 | Threat model STRIDE da Detection API (rule 13): `token_signing_key` → secret manager (hoje placeholder); auth + rate-limit no `/verify` antes de expor | DETECTION/US-009 | pendente (security-auditor) | (criar) |
| T-ADR-01 | ADR (rule-28) das 3 correções de falso-positivo nos guards CRÍTICOS (`no_raw_biometric` docs/self; `no_hardcoded` escopo `.py` + literal-constante-vs-aritmética) + revisão learning-curator | governança | pendente | (criar) |
| T-TRAIN-01 | Treinar na AWS g4dn + certificar (eval-independent) | DETECTION/US-007 | bloqueado (só falta T-DATA-01 data-gen no box) | `RUN_ON_AWS.md` |
| T-US008-01 | Layer 2 comportamental (especificada/simulada — D7) | DETECTION/US-008 | pendente | (criar) |

## Inputs/decisões abertas (do lead)
- Data **oficial** do M1 (hoje provisória jun/2026).
- ~~Dados com ≥2 geradores~~ → **✅ decidido: RAID** (22/jun). Código pronto; data-gen roda no box AWS (decisão do lead).
- Confirmar cada avanço de **código de produto** (D11).
- **Verificar no box:** após gerar o JSONL, se algum gerador do split (`chatgpt`/`gpt4`) não aparecer na amostra alcançável, ajustar `EvalConfig` para geradores presentes (o RAID completo tem os 11 → deve funcionar).

## Log (append no TOPO — data · o que · status)
- 2026-08-13 · **T-FIX-03** (fail-open do `no_raw_biometric`, guard CRÍTICO I1): bug de precedência de operador na seleção de arquivos (`args or [glob] if src else []` → de um cwd sem `src/`, `files=[]` mesmo com arquivo passado por argumento → guard saía 0 sem escanear). Corrigido parentetizando o fallback (`no_hardcoded.py` já era a referência correta) + fail-closed (arg inexistente → WARNING no stderr, não silêncio). Irmãos `no_real_pii`/`secret_scan` inspecionados → defeito **ausente** (provado por teste). Prova bidirecional de `/tmp`: violação→exit 1, limpo→exit 0. `pytest tests/ -q` → **33 passed** (9 novos em `test_guard_failclosed.py`); `bash .githooks/pre-commit` verde. Bundle: `.agent/cli/evidence/T-FIX-03.md`. Major (rule 28) → ADR-0010 em T-ADR-01. **Estado: `READY_FOR_ORACULO`.** · READY_FOR_ORACULO
- 2026-08-13 · **Sprint HARDENING-PRE-TRAINING** (branch `exp/hardening-pre-training` a partir de `exp/port-framework-evolutions`; validador = Oráculo EXTERNO, M5). **T-FIX-01** (vazamento train/test do conjunto de controle): split de controle agora DISJUNTO e determinístico por `sha256` (rule 07, sem RNG) em `train_text_detector.py::_split_controls` (+ `control_train_fraction=0.7` em `config.py`, rule 32) e em `redteam.py::_shard_controls` (shard por `sample_id` — elimina vazamento E dupla contagem); verificação defensiva `ValueError` nomeando I4 se train∩held-out ≠ ∅; notebook Colab alinhado. `pytest tests/ -q` → **24 passed** (17 antigos + 7 novos); py_compile OK; 4 guards pre-commit verdes; demo de JSONL de 20 linhas mostra 7 train + 3 held-out disjuntos. Bundle: `.agent/cli/evidence/T-FIX-01.md`. **Estado: `READY_FOR_ORACULO`** (não commitada na main, não mergeada — aguarda veredito do Oráculo). · READY_FOR_ORACULO
- 2026-06-30 · **EPIC-FRAMEWORK-EVOLUTIONS** (branch `exp/port-framework-evolutions`, aprovado pelo lead): 3 ports zeca-V5 portados p/ Python, cada um PROVADO (verificado independentemente pelo orquestrador). **PORT-1** `framework_selfcheck.py` (meta-guard fail-closed: invariante→guard, `kind` nos 9 cards, single-reviewer, DAG, label-honesty) — born-RED→GREEN, wired pre-push+CI, bite test meu confirmou. **PORT-2** UPGRADE `verify_eval.py` in-place (reviewer M5 `claude -p` isolado + kill-list ML + verdict tipado fail-closed → `current-experiment.json`; `approve.py` recusa gate sem PASS) — prova bidirecional: reرodei o defeito plantado → FAIL nomeando a circularidade (gpt4 em train_generators); clean → PASS_WITH_WARNINGS. **PORT-3** `agent_run.py` + `trace.jsonl` (runner isolado genérico, schema tipado TYPE+ENUM fail-closed, cost/duration reais) — rodei 1 run real (cost 0.102, 1964ms) + fail-closed provado. **F2 (DAG multi-agente) NÃO portado** (STOP baseado em evidência: profundidade sem ganho de catch-rate, ~1.6×). Corrigi drift de escopo que um builder introduziu no README/EPIC-STATUS (PORT-3/4 fantasmas → PORT-2/3 reais). **Nada commitado; NÃO mergeado — human gate.** · ok
- 2026-06-22 · T-US009-01: API `/api/v1/verify` (casca FastAPI + `MockDetector` determinístico, D11) construída; `src/shield_id/api/**` + `tests/test_api.py`; 10/10 pytest, py_compile, 4 guards verdes (verificado pelo orquestrador); curl real PASS/REVIEW/FLAG (score+fatores+token HMAC+trace_id); I1/rule 16 ok. 2ª refinada no `no_hardcoded` (literal-constante vs aritmética: `trust_score = 1.0 - artifact_score` era falso-positivo) — testada adversarialmente. Follow-ups: T-SEC-01 (rule 13) + T-ADR-01. **Não commitada.** · ok
- 2026-06-22 · **baseline commit `6ee6e06` + tag `v0.1-baseline`** (182 arquivos; root-commit em `master`); 4 guards do pre-commit verdes. Correções de **falso-positivo em 2 guards CRÍTICOS** (rule-28): `no_raw_biometric` ignora `.md`+própria fonte; `no_hardcoded` escopo a `.py` de produção (pula docs/notebooks/json/tests/config). Proteção real preservada (testado adversarialmente: ainda bloqueia violação em `.py`). **PENDENTE: ADR (rule-28) + revisão do learning-curator** → ver T-ADR-01 · ok
- 2026-06-22 · T-CFG-01: `TextDetectorConfig` alinhado ao split real do RAID (gpt-4o/claude/llama → chatgpt/mistral-chat/mpt-chat + held-out gpt4); py_compile OK + split sanity verificado pelo orquestrador (train não-vazio, gpt4 só held-out, guard de circularidade dispara); follow-up T-CFG-02 (SSOT) registrado · ok
- 2026-06-22 · T-DATA-01: loader RAID config-driven + split real (treino chatgpt/mistral-chat/mpt-chat, held-out gpt4) escritos e py_compile OK; **JSONL NÃO gerado** (RAID multi-GB não streama na sessão) → data-gen movida pro box AWS (`RUN_ON_AWS.md` §3.5); achado: training lê `TextDetectorConfig` (placeholder) e não `EvalConfig` → criada T-CFG-01 · blocked→handoff
- 2026-06-22 · lead escolheu **RAID** como dataset (T-DATA-01) · ok
- 2026-06-22 · Claude Code rodando (Opus 4.8, bypass on); `/status` lê o framework OK · ok
- 2026-06-18 · camada de orquestração CLI criada (.agent/cli + .claude/commands) · ok
- 2026-06-18 · US-007 código do detector texto-LLM escrito + RUN_ON_GPU/AWS · ok
