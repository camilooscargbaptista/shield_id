# Evidence Bundle — T-FIX-05 (Allowlist estreita de `tests/fixtures/` no pre-push)

**Branch:** `exp/hardening-pre-training` · **Estado:** `READY_FOR_ORACULO` · **Data:** 2026-08-13
**Validador:** Oráculo EXTERNO. Mudança em hook autorizada pelo lead (STOP suspenso SÓ p/ esta task).

## 1. Plano executado (≤10 linhas)
1. Reproduzir o bloqueio: pre-push real sobre `d9d0130..HEAD` → exit 1 (4 fixtures `mh_*_defect.md`).
2. `.githooks/pre-push`: na montagem da lista `MD`, adicionar `case` que EXCLUI o prefixo `tests/fixtures/`
   (allowlist estreita, comentada, citando ADR-0010 + aprovado do lead). Nada mais tocado.
3. Prova bidirecional com o HOOK REAL (via contrato de stdin do git pre-push): (a) range `d9d0130..HEAD`
   → exit 0; (b) `.md` desonesto plantado FORA de `tests/fixtures/` no range → exit 1; depois removido.
4. Suíte pytest completa verde.

## 2. Diff-stat + arquivos tocados
```
 .githooks/pre-push | 12 ++++++++++--   (só o bloco de montagem da lista MD)
```
+ novo: `.agent/cli/tasks/T-FIX-05-fixture-allowlist.task.md` (task file, do _TEMPLATE).
**Escopo:** SÓ `.githooks/pre-push` (bloco MD). NÃO toquei `metric_honesty.py`, `PEDAGOGICAL_PREFIXES`,
nem qualquer outro guard/hook. Exclusão limitada ao prefixo `tests/fixtures/` (não `tests/` inteiro).

### Diff do hook
```diff
 # md/json files in the push that still exist in the working tree (deleted-later files skipped).
+# ALLOWLIST ESTREITA (T-FIX-05, ADR-0010 + aprovado do lead 2026-08-13): os fixtures de guard sob
+# `tests/fixtures/` são relatórios DESONESTOS-POR-DESIGN (entradas de teste do metric_honesty) ...
 MD=""
 while IFS= read -r f; do
-  [ -n "$f" ] && [ -f "$ROOT/$f" ] && case "$f" in *.md|*.json) MD="${MD}${f}
-";; esac
+  [ -n "$f" ] && [ -f "$ROOT/$f" ] && case "$f" in
+    tests/fixtures/*) : ;;                                  # allowlist estreita (T-FIX-05)
+    *.md|*.json) MD="${MD}${f}
+";;
+  esac
 done <<EOF_FILES
```

## 3. Saídas REAIS — prova bidirecional (HOOK REAL, contrato stdin do git pre-push)

### 3.1 ANTES do fix — pre-push real sobre `d9d0130..HEAD` → BLOQUEIA (exit 1)
```
$ printf 'refs/heads/x <HEAD> refs/heads/x <d9d0130>\n' | bash .githooks/pre-push
BLOCKED — metric honesty (rules 05/07). ...
  tests/fixtures/guards/mh_circularity_defect.md: declared circularity ...
  tests/fixtures/guards/mh_fraction_defect.md: metric without cross-generator evidence ...
  tests/fixtures/guards/mh_onedigit_defect.md: metric without cross-generator evidence ...
  tests/fixtures/guards/mh_threshold_sweep_defect.md: decision threshold selected/tuned ...
PRE-PUSH exit=1
```
(index_drift e framework_selfcheck passam standalone — o bloqueio é 100% metric_honesty × fixtures.)

### 3.2 (a) DEPOIS do fix — pre-push real sobre `d9d0130..HEAD` → exit 0
```
$ printf 'refs/heads/x <HEAD-com-task-file-rastreado> refs/heads/x <d9d0130>\n' | bash .githooks/pre-push
metric_honesty: OK
index_drift: OK
framework_selfcheck: OK
pre-push gates: OK
PROOF-A exit=0
```

### 3.3 (b) NARROWNESS — `.md` desonesto plantado FORA de `tests/fixtures/` no range → exit 1
`BOGUS-REPORT.md` (raiz do repo) com `- recall = 0.99 (in-distribution only, no cross-generator)`:
```
$ printf 'refs/heads/x <HEAD-com-bogus> refs/heads/x <d9d0130>\n' | bash .githooks/pre-push
BLOCKED — metric honesty (rules 05/07). A reported number needs cross-generator + reproducibility:
  BOGUS-REPORT.md: metric without reproducible artifact (I3/D5): '- recall = 0.99 (in-distribution only, no cross-generator)'
PROOF-B exit=1
```
Prova que a allowlist é ESTREITA: um relatório desonesto fora de `tests/fixtures/` continua bloqueando.
O plantado foi REMOVIDO em seguida (temp-commits desfeitos via `git reset --soft` ao anchor; working tree preservado).

### 3.4 Suíte completa
```
$ PYTHONPATH=src python3 -m pytest tests/ -q
..........................................                               [100%]
42 passed in 0.65s
```

### 3.5 Higiene do harness de prova
As provas (a)/(b) usaram temp-commits (`--no-verify` SÓ nos commits TEMP descartáveis do harness, nunca
no commit real da task) desfeitos com `git reset --soft` até o anchor `9fefc14`; `BOGUS-REPORT.md`
apagado. Confirmado pós-restore: HEAD = anchor, hook edit presente, sem lixo no working tree.

## 4. Autoavaliação contra o "Done quando" (✓/✗)
- [✓] (a) simulação do gate contra `d9d0130..HEAD` → exit 0 (§3.2).
- [✓] (b) `.md` desonesto FORA de `tests/fixtures/` no range → exit 1, depois removido (§3.3).
- [✓] Suíte pytest completa verde: 42 passed (§3.4).
- [✓] Exclusão SÓ do prefixo `tests/fixtures/` (não `tests/` inteiro, não `PEDAGOGICAL_PREFIXES`).
- [✓] `metric_honesty.py` e todos os outros guards/hooks INTACTOS.
- [✓] Anti-padrões evitados: sem `--no-verify` no commit real; sem exclusão ampla; sem tocar guard.

## 5. Riscos / observações para o Oráculo
- **Mudança em `.githooks/pre-push`** autorizada explicitamente pelo lead (STOP suspenso SÓ p/ T-FIX-05);
  documentada no comentário do hook citando ADR-0010 + o aprovado. Precedente de exclusão-narrow já
  existe no repo (`no_raw_biometric` exclui `scripts/guards/`; `framework_selfcheck` exclui seus fixtures).
- **Vetor residual (aceito):** um relatório desonesto salvo DENTRO de `tests/fixtures/` escaparia do
  pre-push. Mitigação: (i) `tests/fixtures/` é, por convenção, só entrada de teste; (ii) o revisor LLM
  isolado (`verify_eval`) e a suíte pytest continuam cobrindo; (iii) a allowlist é por prefixo exato.
- **Método de prova:** usei o HOOK REAL via contrato stdin do git (remote_sha=`d9d0130`, local_sha=`HEAD`),
  não uma reimplementação — o mesmo caminho de código do `git push` de verdade.
- **Pós-commit desta task:** o full pre-push sobre `d9d0130..HEAD` fica exit 0 (task file rastreado),
  reconfirmado antes do push real.
- **Sem merge:** commit local; push com hooks ativos é o próximo passo (item 3 do aprovado).
