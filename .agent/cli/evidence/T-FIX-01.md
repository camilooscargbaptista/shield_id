# Evidence Bundle — T-FIX-01 (Eliminar vazamento train/test do conjunto de controle)

**Branch:** `exp/hardening-pre-training` · **Estado:** `READY_FOR_ORACULO` · **Data:** 2026-08-13
**Validador:** Oráculo EXTERNO (sessão Cowork isolada). Este dev NÃO se auto-aprova.

## 1. Plano executado (≤10 linhas)
1. `config.py`: novo `control_train_fraction: float = 0.7` (rule 32 — fração em config, split por hash).
2. `train_text_detector.py`: `_control_bucket(text)` (sha256, sem RNG) + `_split_controls(controls, fraction)` → controles train/held-out DISJUNTOS.
3. `split_cross_generator`: ataques filtrados por `label==1`; controles via `_split_controls`; verificação defensiva → `ValueError` (I4) se textos de train∩held-out ≠ ∅.
4. `redteam.py`: `_shard_controls(controls, groups)` (sha256 por `sample_id`) → shard exclusivo por gerador; elimina vazamento E dupla contagem no pool in-distribution.
5. Notebook Colab (cells 3+6): `control_train_fraction=0.7` no CFG + split disjunto por hash espelhando `_split_controls`.
6. `tests/test_training_split.py`: 7 testes (disjunção, determinismo, ValueError defensivo forjado, shards redteam disjuntos, sem dupla contagem).

## 2. Diff-stat + arquivos tocados
```
 .agent/epics/EPIC-DETECTION-API/SHIELD-ID_Layer1_TextDetector_Colab.ipynb | 25 ++++++++++----
 src/shield_id/data/redteam.py                      | 28 ++++++++++++----
 src/shield_id/layers/layer1_detection/config.py    |  5 +++
 src/shield_id/training/train_text_detector.py      | 39 +++++++++++++++++++---
 4 files changed, 79 insertions(+), 18 deletions(-)
```
+ novo arquivo: `tests/test_training_split.py` (untracked → adicionado no commit).
Arquivos tocados (exatamente os 4 do task file + o teste novo): `config.py`, `train_text_detector.py`,
`redteam.py`, notebook Colab, `tests/test_training_split.py`. **Nenhum arquivo fora de escopo.**

## 3. Saídas REAIS e completas dos comandos do "Done quando"

### 3.1 `py_compile` dos módulos tocados
```
$ python3 -m py_compile \
    src/shield_id/layers/layer1_detection/config.py \
    src/shield_id/training/train_text_detector.py \
    src/shield_id/data/redteam.py \
    tests/test_training_split.py
py_compile OK (exit 0)
```

### 3.2 Suíte completa de testes
```
$ PYTHONPATH=src python3 -m pytest tests/ -q
........................                                                 [100%]
24 passed in 0.30s
```
Baseline antes da task: `17 passed`. Depois: `24 passed` = **17 antigos + 7 novos** (≥4 exigidos).
Testes novos em `tests/test_training_split.py`:
- `test_controls_disjoint_between_train_and_heldout` (a — disjunção)
- `test_split_controls_partitions_all_without_loss` (a — partição sem perda)
- `test_control_bucket_in_range_and_stable` (rule 07 — determinismo do hash)
- `test_split_is_deterministic` (b — determinismo)
- `test_defensive_check_raises_on_forged_overlap` (c — ValueError defensivo, fixture forjada)
- `test_redteam_control_shards_are_disjoint` (d — nenhum sample_id em 2 grupos)
- `test_redteam_split_no_double_count_of_controls` (d — sem dupla contagem no pool)

### 3.3 Demonstração — split de um JSONL sintético de 20 linhas (contagens disjuntas)
JSONL sintético (20 linhas): 10 controles + 6 ataques `chatgpt` (treino) + 4 ataques `gpt4` (held-out).
Split executado pelo caminho REAL (`load_jsonl` → `split_cross_generator`):
```
input rows: 20 | control_train_fraction=0.7
TRAIN   : 13 total = 6 attacks(['chatgpt']) + 7 control
HELD-OUT:  7 total = 4 attacks(['gpt4']) + 3 control
control split: 7 train + 3 held-out = 10 (input controls: 10)
control texts intersection train∩heldout: []  (MUST be empty)
ALL texts intersection train∩heldout: []  (MUST be empty)
DISJOINT verified ✓
```
Os 10 controles foram particionados em 7 (treino) + 3 (held-out), **disjuntos** — nenhum negativo
aparece nos dois lados (I4/D8). Antes da correção, os 10 controles apareciam nos DOIS lados.

### 3.4 Guards de pre-commit contra os arquivos tocados (fail-closed, sem `--no-verify`)
```
--- no_raw_biometric --- no_raw_biometric: OK      exit=0
--- no_real_pii ---      no_real_pii: OK            exit=0
--- secret_scan ---      secret_scan: OK            exit=0
--- no_hardcoded ---     no_hardcoded: OK           exit=0
```

## 4. Autoavaliação contra o "Done quando" (✓/✗)
- [✓] `PYTHONPATH=src python3 -m pytest tests/ -q` → 24 passed (17 antigos + 7 novos ≥ 4). Saída completa colada.
- [✓] `py_compile` dos módulos tocados → exit 0.
- [✓] Demonstração de split de JSONL de 20 linhas com contagens disjuntas colada.
- [✓] `config.py`: `control_train_fraction` em config (rule 32), split determinístico por hash documentado.
- [✓] `_split_controls` por sha256(text), sem RNG (rule 07); train/held-out disjuntos; ataques filtrados por `label==1`.
- [✓] Verificação defensiva → `ValueError` nomeando I4 quando train∩held-out ≠ ∅ (teste `test_defensive_check_raises_on_forged_overlap`).
- [✓] `redteam.py`: shards determinísticos disjuntos por `sample_id`; docstring atualizada; sem dupla contagem.
- [✓] Notebook Colab corrigido para o mesmo padrão.
- [✓] Anti-padrões evitados: sem RNG/seed no split de controle (é hash); fração NÃO hardcoded na lógica; thresholds/métricas NÃO tocados; NENHUM número de detector reportado (rule 15).

## 5. Riscos / observações para o Oráculo
- **Escolha do split de controle por hash:** `_control_bucket` usa os 64 bits altos de `sha256(text)`
  normalizados para [0,1). Quantização desprezível (2⁻⁶⁴). Determinístico entre execuções/máquinas (rule 07).
- **Divergência de chave entre os dois caminhos (intencional):** `train_text_detector` hasheia `text`
  (JSONL não tem `sample_id`); `redteam` hasheia `sample_id` (dataclass `Sample` não tem campo de texto).
  Cada caminho usa a chave estável disponível no seu esquema. Ambos produzem partição disjunta.
- **Notebook não é importável no Colab** (repo não instalado lá): o split foi INLINEADO espelhando
  `_split_controls` byte-a-byte na lógica (mesmo `_control_bucket`, mesma fração via `CFG`). O task
  permite reuso ("pode reusar") mas não obriga; inline mantém o notebook self-contained.
- **`fraction=0.7` fixo:** com 40 controles no teste (a), os dois lados ficam não-vazios; com poucos
  controles (<~4) um lado pode ficar vazio — comportamento correto (não é vazamento), só amostra pequena.
- **Sem push:** commit local na branch da sprint; Oráculo lê o working tree. Merge = gate humano.
