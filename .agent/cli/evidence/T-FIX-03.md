# Evidence Bundle — T-FIX-03 (Fail-open do `no_raw_biometric`)

**Branch:** `exp/hardening-pre-training` · **Estado:** `READY_FOR_ORACULO` · **Data:** 2026-08-13
**Validador:** Oráculo EXTERNO. Guard CRÍTICO (I1) → mudança de comportamento coberta por ADR em T-ADR-01.

## 1. Plano executado (≤10 linhas)
1. Reproduzir o fail-open a partir de `/tmp` (sem `src/`), com violação plantada passada por argumento.
2. `no_raw_biometric.py`: parentetizar o fallback — `args or ([glob] if Path("src").exists() else [])`.
3. Fail-closed na seleção: arquivo pedido por arg que não existe → WARNING no stderr (não silêncio);
   sem args e sem `src/` → WARNING + exit 0 (genuinamente nada a escanear).
4. Inspecionar irmãos `no_real_pii.py` e `secret_scan.py` pela mesma classe de defeito (precedência).
5. `tests/test_guard_failclosed.py`: subprocess, cwd temporário SEM `src/`, cada guard: violação → 1, limpo → 0.
6. Prova bidirecional + suíte verde + `bash .githooks/pre-commit` verde num commit de teste.

## 2. Diff-stat + arquivos tocados
```
 scripts/guards/no_raw_biometric.py |  17 ++++++-
 tests/test_guard_failclosed.py     | 100 +++++++++++++++++++++++++++++++++++++
 2 files changed, 116 insertions(+), 1 deletion(-)
```
**Escopo respeitado:** só `no_raw_biometric.py` (o defeito) + o teste novo. Os irmãos foram
INSPECIONADOS mas NÃO precisaram de mudança (ver §5). Padrões de detecção NÃO alterados (escopo é só
seleção de arquivos). Nenhum `|| true`, nenhuma exceção engolida.

## 3. Saídas REAIS — prova bidirecional

### 3.1 ANTES do fix — bug reproduzido a partir de `/tmp` (sem `src/`)
```
$ cd /tmp/failopen_probe   # printf 'raw_face = open("face.jpg","rb").read()\n' > leak.py
$ python3 .../scripts/guards/no_raw_biometric.py leak.py
no_raw_biometric: OK
exit=0        <-- FAIL-OPEN: violação I1 passada por arg foi IGNORADA
```
Causa: `files = sys.argv[1:] or [glob] if Path("src").exists() else []` avaliado como
`(sys.argv[1:] or [glob]) if Path("src").exists() else []` → sem `src/` no cwd, `files=[]`.

### 3.2 DEPOIS do fix — mesma execução a partir de `/tmp`
```
--- violação passada por arg -> MUST exit 1 ---
BLOCKED — I1 raw-biometric persistence (rule 04). Use derived feature vectors only:
  leak.py:1: raw_face = open("face.jpg", "rb").read()
exit=1
--- arquivo limpo -> MUST exit 0 ---
no_raw_biometric: OK
exit=0
--- arg inexistente -> aviso no stderr, exit 0 ---
no_raw_biometric: WARNING — requested path not found, not scanned: nope.py
no_raw_biometric: OK
exit=0
```

### 3.3 Diff do guard (o fix + hardening fail-closed)
```diff
-    files = sys.argv[1:] or [str(p) for p in Path("src").rglob("*.py")] if Path("src").exists() else []
+    args = sys.argv[1:]
+    files = args or ([str(p) for p in Path("src").rglob("*.py")] if Path("src").exists() else [])
+    if args:
+        for f in args:
+            if not Path(f).is_file():
+                print(f"no_raw_biometric: WARNING — requested path not found, not scanned: {f}", file=sys.stderr)
+    elif not files:
+        print("no_raw_biometric: WARNING — no files passed and no src/ tree; nothing to scan.", file=sys.stderr)
```

### 3.4 Suíte completa de testes
```
$ PYTHONPATH=src python3 -m pytest tests/ -q
.................................                                        [100%]
33 passed in 0.49s
```
33 = 24 (após T-FIX-01) + **9 novos** em `test_guard_failclosed.py` (violação→1 e limpo→0 para os 4
guards de seleção de arquivos + o caso arg-inexistente→warning do `no_raw_biometric`).

### 3.5 `bash .githooks/pre-commit` verde (arquivos da task staged)
```
$ git add scripts/guards/no_raw_biometric.py tests/test_guard_failclosed.py
$ bash .githooks/pre-commit
no_raw_biometric: OK
no_real_pii: OK
secret_scan: OK
no_hardcoded: OK
pre-commit gates: OK
hook exit=0
```

### 3.6 O próprio arquivo de teste NÃO dispara os guards que o escaneiam (sem auto-trip)
```
no_raw_biometric exit=0 · no_real_pii exit=0 · secret_scan exit=0 · no_hardcoded exit=0
```
(Payloads de violação montados por concatenação de fragmentos: contíguos só no arquivo temporário
escrito em runtime, nunca no source do teste.)

## 4. Autoavaliação contra o "Done quando" (✓/✗)
- [✓] Prova bidirecional: violação de QUALQUER cwd → exit 1; limpo → exit 0 (colada em §3.2).
- [✓] Suíte completa verde: 33 passed.
- [✓] `bash .githooks/pre-commit` verde num commit de teste (§3.5).
- [✓] Parentetização aplicada (§3.3).
- [✓] Fail-closed: arg inexistente → warning no stderr (não silêncio) (§3.2, teste dedicado).
- [✓] Irmãos inspecionados: `no_real_pii` e `secret_scan` — defeito AUSENTE (ver §5).
- [✓] Anti-padrões evitados: padrões de detecção intactos; nenhum `|| true`; nenhuma exceção engolida.

## 5. Riscos / observações para o Oráculo
- **`no_real_pii.py`: verificado, AUSENTE.** Usa `targets = sys.argv[1:]; if not targets: targets = [...]`
  — sem `or` misturado com ternário, então não há bug de precedência. Prova: de `/tmp`, com CPF plantado
  → **exit 1** (BLOCK). Coberto por `test_no_real_pii_blocks_violation_from_foreign_cwd`.
- **`secret_scan.py`: verificado, AUSENTE.** Linha `files = sys.argv[1:] or [glob]` sem ternário
  `if/else` — o fallback (`Path(".").rglob`) sempre existe, sem fail-open por precedência. Prova: de
  `/tmp`, com segredo plantado → **exit 1**. Coberto por `test_secret_scan_blocks_violation_from_foreign_cwd`.
- **`no_hardcoded.py`: já correto** (é a referência do padrão parentetizado) — incluído no teste como
  regressão (violação→1, limpo→0).
- **Decisão fail-closed sobre arg inexistente:** WARNING + exit governado pelos arquivos existentes
  (NÃO exit 1). Racional: um arquivo inexistente não tem bytes a vazar; bloquear quebraria fluxos onde
  um caminho deletado é passado. Isto NÃO reintroduz fail-open — a violação real (arquivo que EXISTE
  com conteúdo proibido, passado por arg de qualquer cwd) agora sempre → exit 1.
- **Guard CRÍTICO alterado** (I1): major por rule 28 → documentado no ADR-0010 (T-ADR-01).
- **Sem push:** commit local; Oráculo lê o working tree.
