# Protocolo Oráculo — Sprint HARDENING-PRE-TRAINING (M5 externo)

## Papéis
- **Dev (builder):** sessão Claude CLI rodando `ORCHESTRATOR-HARDENING-2026-08.md`. Escreve código,
  testes e evidence bundles. NÃO valida, NÃO aprova, NÃO faz merge.
- **Oráculo (validador):** sessão Cowork ISOLADA (contexto separado, sem acesso ao raciocínio do dev).
  Lê os bundles + o código real no working tree, reexecuta as provas de forma independente e emite
  veredito. Não escreve código de produto.
- **Lead (Camilo):** único com poder de `/approved`, commit final na main e merge.

## Evidence bundle (o dev escreve, por task)
`.agent/cli/evidence/<TASK>.md` contendo, nesta ordem:
1. Plano executado (≤10 linhas)
2. Diff-stat + lista de arquivos tocados
3. **Saídas REAIS e completas** de cada comando exigido no "Done quando" do task file
4. Autoavaliação contra cada linha do "Done quando" (checklist ✓/✗ — ✗ = task não está pronta)
5. Riscos/observações que o Oráculo deve saber (omitir algo aqui = FAIL automático se descoberto)

## Veredito do Oráculo
`.agent/cli/evidence/<TASK>.verdict.json`:
```json
{"task": "T-FIX-0X", "verdict": "PASS|PASS_WITH_WARNINGS|FAIL",
 "checks": {"reproduced_independently": true, "bidirectional_proof": true,
            "scope_respected": true, "no_test_theater": true},
 "findings": ["..."], "reviewed_at": "ISO-8601"}
```
Regras do veredito (herdadas do `verify_eval.py` / tabela-verdade M5):
- O Oráculo **reexecuta** os comandos-chave ele mesmo; saída colada em bundle sem reprodução
  independente NÃO conta como evidência.
- Postura adversarial: assumir que a task NÃO está pronta até o código provar o contrário.
- Kill-list desta sprint: (1) fail-open novo introduzido ao consertar fail-open; (2) teste-teatro
  (testa o mock, não o comportamento; asserts triviais); (3) alargamento de isenção/janela disfarçado
  de correção; (4) escopo extrapolado (arquivo tocado fora da lista da task); (5) prova bidirecional
  incompleta (só o lado feliz); (6) "existência ≠ implementação" (função criada mas não ligada ao
  caminho real); (7) qualquer edição em `.agent/state/`, hooks ou approval-log pelo dev.
- FAIL em qualquer item da kill-list. PASS_WITH_WARNINGS só para achados que não alteram a validade.

## Fluxo por task
dev termina → `READY_FOR_ORACULO` no CONTROL → lead aciona o Oráculo na sessão Cowork →
Oráculo reexecuta + veredito JSON → PASS → lead `/approved` + commit segue na branch ·
FAIL → dev corrige na MESMA task (nova rodada, máx. 3; na 3ª falha → HALT e lead decide).

## Encerramento da sprint
5 vereditos PASS/PASS_WITH_WARNINGS → Oráculo emite resumo consolidado → lead decide merge
`exp/hardening-pre-training` → `exp/port-framework-evolutions` (ou direto para main com os dois).
