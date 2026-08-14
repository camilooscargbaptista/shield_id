# Evidence Bundle — T-FIX-02 (Hardening do guard `metric_honesty`)

**Branch:** `exp/hardening-pre-training` · **Estado:** `READY_FOR_ORACULO` · **Data:** 2026-08-13
**Validador:** Oráculo EXTERNO. Guard CRÍTICO → major (rule 28), documentado em ADR-0010 (T-ADR-01).

## 1. Plano executado (≤10 linhas)
1. `METRIC_PCT` agora `\b\d{1,3}...%` (captura `0.3%`) + novo `METRIC_FRAC` para frações nomeadas (`recall = 0.96`).
2. `TARGET_ADJ` estendido aos novos formatos numéricos, **janela de 12 chars INALTERADA** (LC-004).
3. Check determinístico de **circularidade**: `held_out_generator` ∈ `train_generators` → BLOCK (kill-list #1/I4/D8); invalida `has_cross`.
4. Check heurístico de **threshold-no-held-out**: verbo de tuning ≤80 chars de `held-out|test split` → BLOCK, EXCETO negação adjacente (≤12 chars antes do verbo — LC-004).
5. Erro de leitura/parse → **BLOCK** com mensagem (nunca exit 0 fail-open).
6. Os 2 checks estruturais são de **artefato-relatório**: escopados p/ pular `.py` (código/kill-list/testes-negativos) — NÃO alarga `PEDAGOGICAL_PREFIXES` nem a janela; pre-push só varre `.md`/`.json` mesmo.
7. 5 fixtures novos + `tests/test_guard_metric_honesty.py` (subprocess) + varredura do repo.

## 2. Diff-stat + arquivos tocados
```
 scripts/guards/metric_honesty.py                   | 144 +++++++++++++++++----
 tests/fixtures/guards/mh_circularity_defect.md     |  12 ++
 tests/fixtures/guards/mh_clean_negation.md         |  18 +++
 tests/fixtures/guards/mh_fraction_defect.md        |  10 ++
 tests/fixtures/guards/mh_onedigit_defect.md        |  10 ++
 tests/fixtures/guards/mh_threshold_sweep_defect.md |  15 +++
 tests/test_guard_metric_honesty.py                 |  85 ++++++++++++
 7 files changed, 271 insertions(+), 23 deletions(-)
```
**Escopo:** exatamente `metric_honesty.py` + fixtures + o teste (a Saída declarada). Nenhum outro guard,
nenhum threshold/métrica de produto, nenhum arquivo fora da lista.

## 3. Saídas REAIS — prova bidirecional

### 3.1 `py_compile`
```
$ python3 -m py_compile scripts/guards/metric_honesty.py
py_compile OK
```

### 3.2 DEFECT canônico (PORT-2) → exit 1 nomeando circularidade E threshold-sweep E métrica
```
$ python3 scripts/guards/metric_honesty.py --require-cross-generator tests/fixtures/port2/experiment_defect.md
BLOCKED — metric honesty (rules 05/07). A reported number needs cross-generator + reproducibility:
  tests/fixtures/port2/experiment_defect.md: declared circularity — held_out_generator 'gpt4' is inside train_generators ['styleganA', 'diffB', 'gpt4']: the reported metric is NOT cross-generator (kill-list #1 / I4 / D8)
  tests/fixtures/port2/experiment_defect.md: decision threshold selected/tuned on the held-out/test split — selection leakage (kill-list #4 / rule 05)
  tests/fixtures/port2/experiment_defect.md: metric without cross-generator evidence (I4/D8): '- cross-generator recall @ fpr 0.3% = 0.96 (ci ±0.01)'
exit=1
```
→ ANTES do fix este mesmo fixture saía `exit=0` (passava o gate determinístico havia 22 dias).

### 3.3 CLEAN canônico (PORT-2) → exit 0
```
$ python3 scripts/guards/metric_honesty.py --require-cross-generator tests/fixtures/port2/eval_report_clean.md
metric_honesty: OK
exit=0
```
(o disclaimer "NOT tuned on the held-out set" é respeitado pela adjacência de negação — não bloqueia.)

### 3.4 Os 5 fixtures novos — exit codes
```
mh_fraction_defect.md        -> exit=1   (fração 'recall = 0.96' sem cross-generator)
mh_onedigit_defect.md        -> exit=1   ('0.3%' de 1 dígito sem cross-generator)
mh_circularity_defect.md     -> exit=1   (gpt4 em train_generators + held_out)
mh_threshold_sweep_defect.md -> exit=1   (threshold 'selected by sweeping ... held-out')
mh_clean_negation.md         -> exit=0   (limpo, com 'NOT tuned on the held-out set')
```
Detalhe (isolamento de cada buraco):
- fraction/onedigit → `metric without cross-generator evidence` (prova que a métrica passou a ser DETECTADA).
- threshold_sweep → **só** `selection leakage (kill-list #4)` (sem circularidade — isola o check de sweep).

### 3.5 Suíte completa
```
$ PYTHONPATH=src python3 -m pytest tests/ -q
..........................................                               [100%]
42 passed in 0.67s
```
33 (após T-FIX-03) + 9 novos em `test_guard_metric_honesty.py` (4 defeitos param + clean + par PORT-2 + missing-file + read-error fail-closed).

### 3.6 Varredura do repo (todos `.md`/`.py` versionados fora de `.agent/`/`.context/`) — zero FP não-resolvido
Primeira varredura (antes do escopo dos checks estruturais) — 5 flags, 4 FALSOS POSITIVOS em `.py`:
```
scripts/agent/verify_eval.py        -> threshold-sweep  (texto DESCRITIVO da kill-list; FP)
scripts/guards/metric_honesty.py    -> threshold-sweep  (as PRÓPRIAS regex/docstrings; FP)
src/.../train_text_detector.py      -> threshold-sweep  ("fine-tune the pretrained encoder" perto de held-out; FP)
tests/test_eval_harness.py          -> circularity      (TESTE NEGATIVO que monta manifesto circular p/ provar rejeição; FP)
tests/fixtures/port2/experiment_defect.md -> circ+sweep+métrica  (fixture de defeito INTENCIONAL; true positive)
```
Resolução (sem alargar isenção nem janela): os 2 checks estruturais são de artefato-relatório e foram
escopados p/ pular `.py` (`_is_source_code`). Justificativa verificada: (a) o pre-push só varre `.md`/`.json`,
então nenhum gate real perde cobertura; (b) circularidade REAL no caminho de treino já é pega em RUNTIME
(`ValueError` em `train_text_detector.py:42`, `redteam.py:87`, `eval/splits.py:19`); (c) o único `.py` com
"circularidade real" era o teste negativo que prova a rejeição. Varredura DEPOIS do escopo:
```
tests/fixtures/guards/mh_circularity_defect.md       -> BLOCK  (fixture de defeito intencional)
tests/fixtures/guards/mh_fraction_defect.md          -> BLOCK  (idem)
tests/fixtures/guards/mh_onedigit_defect.md          -> BLOCK  (idem)
tests/fixtures/guards/mh_threshold_sweep_defect.md   -> BLOCK  (idem)
tests/fixtures/port2/experiment_defect.md            -> BLOCK  (idem, canônico)
```
**Todos os 5 flags restantes são fixtures de defeito INTENCIONAIS (true positives). Zero FP não-resolvido.**
`mh_clean_negation.md` passa (não aparece na lista).

> **Follow-up de higiene (mesmo dia, commit separado):** depois de commitado, `tests/test_guard_metric_honesty.py`
> passou a ser rastreado e a varredura o flagou por um payload literal `recall = 0.99` no source (a métrica
> em forma de fração agora é DETECTADA — prova de que o hardening funciona). Resolvido do jeito honesto (sem
> alargar isenção): o payload foi montado por FRAGMENTOS (`"rec" + "all = 0." + "99"`), contíguo só no arquivo
> temporário escrito em runtime — mesma técnica de `tests/test_guard_failclosed.py`. Varredura reexecutada:
> só os 5 fixtures de defeito intencionais permanecem. O teste (`test_read_error_blocks_not_failopen`) continua verde.

### 3.7 `bash .githooks/pre-commit` verde (arquivos da task staged)
```
no_raw_biometric: OK · no_real_pii: OK · secret_scan: OK · no_hardcoded: OK · pre-commit gates: OK · exit=0
```

## 4. Autoavaliação contra o "Done quando" (✓/✗)
- [✓] `experiment_defect.md` → exit 1 nomeando circularidade E threshold-sweep E métrica (§3.2).
- [✓] `eval_report_clean.md` → exit 0 (§3.3).
- [✓] Os 5 fixtures novos com exit codes corretos (§3.4).
- [✓] Suíte pytest completa verde: 42 passed (§3.5).
- [✓] Varredura do repo colada com **zero FP não-resolvido** (§3.6).
- [✓] `METRIC` amplia p/ fração nomeada + `%` de 1 dígito; `TARGET_ADJ` cobre os novos formatos, janela 12 INALTERADA.
- [✓] Circularidade determinística + threshold-sweep heurístico com negação-adjacente.
- [✓] Erro de parse/leitura = BLOCK (teste `test_read_error_blocks_not_failopen`), nunca fail-open.
- [✓] Anti-padrões evitados: `PEDAGOGICAL_PREFIXES` intacto; janela de 12 chars intacta; nenhum check
      existente desligado; nenhum exit 0 em erro (fail-closed).

## 5. Riscos / observações para o Oráculo
- **DECISÃO material — escopo dos 2 checks estruturais para não-`.py`:** os checks de circularidade e
  threshold-sweep NÃO rodam em `.py`. Racional completo em §3.6 e na docstring de `_is_source_code`.
  Isto **não** toca `PEDAGOGICAL_PREFIXES` nem a janela de 12 chars (os anti-padrões proibidos). A
  detecção de métrica (%/fração) continua rodando em TODOS os arquivos. Peço adjudicação explícita: se
  o Oráculo considerar que os checks estruturais DEVEM rodar em `.py`, os 4 FPs de §3.6 reaparecem e
  precisariam de outra resolução (ex.: allowlist de fixtures) — registrei isso como task proposta.
- **Interação fixtures × pre-push (inerente, NÃO resolvível nesta task):** os 5 fixtures de defeito são
  `.md` com conteúdo deliberadamente desonesto. O gate **pre-push** roda `metric_honesty` em `.md`/`.json`
  do push → esses fixtures BLOQUEARIAM um `git push` do branch. NÃO consertei porque as duas saídas
  possíveis são anti-padrão proibido (alargar isenção) ou condição de STOP (tocar `.githooks/`). O Oráculo
  lê o **working tree** (sem push), então não afeta a validação. Registrei **T-FIX-05 (proposta)** no
  CONTROL.md: mecanismo estreito e honesto p/ isentar fixtures-de-guard declarados do gate pre-push
  (allowlist de caminhos de fixture, decidido pelo lead) — sem alargar a isenção pedagógica.
- **Heurística de threshold-sweep é coarse (por design):** captura verbo-de-tuning perto de held-out;
  a negação-adjacente exime a ocorrência específica (escopada ao verbo, não ao arquivo inteiro). Casos
  sofisticados (negação distante, paráfrase) ficam com o revisor LLM (`verify_eval.py`), como o task previu.
- **Sem push:** commit local; Oráculo lê o working tree. Major (rule 28) → ADR-0010 (T-ADR-01).
