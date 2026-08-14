# SPRINT HARDENING-PRE-TRAINING — Orchestrator Master Prompt (STATIC — do not edit during execution)

## Identity
Sprint: HARDENING-PRE-TRAINING (2026-08) · Pré-requisito duro de T-DATA-01/T-TRAIN-01 e do deploy.
Contexto: reunião Global Trust Challenge em 31/08. Owner: Camilo. Fonte dos achados:
`docs/02-analysis/CTO-Competition-Readiness-Audit_2026-08-13.md` (fora do repo, em `../../docs/`).

## Leia primeiro (nesta ordem, nada além disto)
`AGENTS.md` · `.agent/CONSTITUTION.md` · `.agent/INDEX.md` (rotas) · `.agent/cli/CONTROL.md` · este arquivo.

## Non-negotiables desta sprint
1. **M5 reforçado:** o validador desta sprint é um **Oráculo EXTERNO a esta sessão** (sessão Cowork
   isolada operada pelo lead). Você NÃO se auto-aprova, NÃO marca task como done, NÃO emite veredito.
   Seu estado final permitido por task é `READY_FOR_ORACULO`.
2. **M1 evidência-ou-silêncio:** toda task termina com um *evidence bundle* em
   `.agent/cli/evidence/<TASK>.md` (protocolo em `.agent/cli/ORACULO-HANDOFF.md`). Sem bundle = task
   não existe.
3. **M4 escopo é lei:** exatamente 5 tasks, na ordem abaixo. Nenhum refactor cosmético, nenhuma
   melhoria oportunista, nenhum arquivo fora dos listados em cada task. Se descobrir problema novo:
   registre em CONTROL.md como task proposta e SIGA — não conserte.
4. **M2 unknown → HALT:** qualquer ambiguidade material, PARE e pergunte ao lead.
5. **M6/rule 08:** micro-commits por task na branch da sprint, Conventional Commits, NUNCA
   `--no-verify`. Criar branch: `exp/hardening-pre-training` a partir de `exp/port-framework-evolutions`.
   NÃO fazer merge — gate humano.
6. **rule 15:** nenhum número de métrica de produto reportado por você, em nenhum artefato.
7. Guards são o produto desta sprint: mudança em guard CRÍTICO é major → exige ADR (rule 28), coberta
   por T-ADR-01. Prova **bidirecional** obrigatória (violação sintética → BLOCK · caso limpo → OK).

## Ordem de execução (dependências)
1. `T-FIX-01` — vazamento train/test do conjunto de controle (produto; bloqueia o treino)
2. `T-FIX-03` — fail-open do `no_raw_biometric` (guard; correção pequena e independente)
3. `T-FIX-02` — hardening do `metric_honesty` (guard; a maior task — depende de T-FIX-03 só por foco)
4. `T-FIX-04` — pins do `requirements-gpu.txt`
5. `T-ADR-01` — ADR das mudanças de guards (jun + esta sprint) + lições LC

Task files: `.agent/cli/tasks/T-FIX-0{1..4}-*.task.md` e `.agent/cli/tasks/T-ADR-01-guards-adr.task.md`.

## Por task, o ciclo é
(a) ler o task file + arquivos que ele nomeia → (b) plano curto (≤10 linhas) colado no início do
evidence bundle → (c) implementar → (d) rodar TODA a verificação exigida no "Done quando" e colar
saídas REAIS (não resumidas) no bundle → (e) commit da task → (f) atualizar CONTROL.md (linha no Log,
status `READY_FOR_ORACULO`) → (g) próxima task.

## STOP conditions (HALT imediato + pergunta ao lead)
- Qualquer teste da suíte existente quebra e a correção não é óbvia dentro do escopo da task.
- Um guard bloqueia seu próprio commit e a causa não é a violação que você acabou de criar de propósito.
- A prova bidirecional de T-FIX-02 não fecha (defeito passa OU limpo bloqueia) após 2 tentativas.
- Você se pegar prestes a editar: qualquer arquivo de `.agent/state/`, `approval-log.jsonl`,
  `current-experiment.json`, hooks de `.githooks/`, ou o escopo de isenção de qualquer guard
  além do especificado na task.

## Ao final da sprint
Resumo de ≤15 linhas no CONTROL.md (Log, topo) listando os 5 bundles + hashes dos commits.
Estado final: branch `exp/hardening-pre-training` com 5 commits, NÃO mergeada, aguardando
veredito do Oráculo + aprovação do lead (a palavra "aprovado" no prompt; registre-a via
`python3 scripts/agent/approve.py <step>` para que o approval-log receba a entrada). Nada além disso.
