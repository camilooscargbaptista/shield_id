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
| T-US009-01 | FastAPI `/api/v1/verify` (detector-mock testável aqui) | DETECTION/US-009 | pendente | `.agent/cli/tasks/T-US009-api.task.md` |
| T-TRAIN-01 | Treinar na AWS g4dn + certificar (eval-independent) | DETECTION/US-007 | bloqueado (só falta T-DATA-01 data-gen no box) | `RUN_ON_AWS.md` |
| T-US008-01 | Layer 2 comportamental (especificada/simulada — D7) | DETECTION/US-008 | pendente | (criar) |

## Inputs/decisões abertas (do lead)
- Data **oficial** do M1 (hoje provisória jun/2026).
- ~~Dados com ≥2 geradores~~ → **✅ decidido: RAID** (22/jun). Código pronto; data-gen roda no box AWS (decisão do lead).
- Confirmar cada avanço de **código de produto** (D11).
- **Verificar no box:** após gerar o JSONL, se algum gerador do split (`chatgpt`/`gpt4`) não aparecer na amostra alcançável, ajustar `EvalConfig` para geradores presentes (o RAID completo tem os 11 → deve funcionar).

## Log (append no TOPO — data · o que · status)
- 2026-06-22 · T-CFG-01: `TextDetectorConfig` alinhado ao split real do RAID (gpt-4o/claude/llama → chatgpt/mistral-chat/mpt-chat + held-out gpt4); py_compile OK + split sanity verificado pelo orquestrador (train não-vazio, gpt4 só held-out, guard de circularidade dispara); follow-up T-CFG-02 (SSOT) registrado · ok
- 2026-06-22 · T-DATA-01: loader RAID config-driven + split real (treino chatgpt/mistral-chat/mpt-chat, held-out gpt4) escritos e py_compile OK; **JSONL NÃO gerado** (RAID multi-GB não streama na sessão) → data-gen movida pro box AWS (`RUN_ON_AWS.md` §3.5); achado: training lê `TextDetectorConfig` (placeholder) e não `EvalConfig` → criada T-CFG-01 · blocked→handoff
- 2026-06-22 · lead escolheu **RAID** como dataset (T-DATA-01) · ok
- 2026-06-22 · Claude Code rodando (Opus 4.8, bypass on); `/status` lê o framework OK · ok
- 2026-06-18 · camada de orquestração CLI criada (.agent/cli + .claude/commands) · ok
- 2026-06-18 · US-007 código do detector texto-LLM escrito + RUN_ON_GPU/AWS · ok
