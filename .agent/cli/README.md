# SHIELD-ID — Orquestração via Claude Code CLI

Camada de **prompts** pra tocar o desenvolvimento no terminal, no padrão *orquestrador + prompts-filhos +
doc vivo* (analisado de zeca_site/.agent + GSD). Liga-se à constituição, rules, guards, agentes e épicos.

## Como usar
```bash
cd repository/shield_id
claude                      # Claude Code lê AGENTS.md (→ CLAUDE.md) automaticamente
```
Depois, no CLI:
- **`/orchestrate`** → pega a próxima tarefa do CONTROL e executa sob os gates (pausa nos `/approved`).
- **`/next`** → executa só a próxima tarefa pendente (um item).
- **`/status`** → mostra onde estamos (lê o CONTROL, não executa).

## Peças
| Arquivo | Papel |
|---|---|
| `.agent/cli/CONTROL.md` | **doc vivo de controle** — estado + fila de tarefas + inputs abertos + log. Claude lê 1º, atualiza por último. |
| `.agent/cli/tasks/*.task.md` | **prompts-filhos** curtos — nomeiam os arquivos a ler; o trabalho vive nos arquivos. |
| `.claude/commands/{orchestrate,next,status}.md` | os **slash commands** (o orquestrador e atalhos). |
| `.agent/agents/ORCHESTRATOR.md` | o agent card do orquestrador (comportamento detalhado). |
| `.agent/epics/*/` | épicos + user stories + gates (o backlog de longo prazo). |

## O loop
`/orchestrate` → lê **CONTROL** → abre o **task prompt** → executa **sob os gates/guards** →
**atualiza CONTROL** (status + log) → **propõe a próxima**. Construtor ≠ juiz (eval-independent isolado).
Código de produto só com confirmação do lead (D10/D11); treino roda na GPU (AWS), não na sessão.

## Adicionar uma tarefa
Copie `tasks/_TEMPLATE.task.md` → `tasks/T-XXX-...task.md`, preencha, e adicione a linha na fila do CONTROL.
