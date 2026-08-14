# Evidence Bundle — T-FIX-04 (Pinar `requirements-gpu.txt`)

**Branch:** `exp/hardening-pre-training` · **Estado:** `READY_FOR_ORACULO` · **Data:** 2026-08-13
**Validador:** Oráculo EXTERNO. rules 02/07/13 (supply-chain).

## 1. Plano executado (≤10 linhas)
1. Confirmar a contradição: `requirements-gpu.txt` tinha `datasets>=2.19`, mas o loader ABORTA em
   runtime se `datasets.__version__ != "4.5.0"` (`load_open_dataset.py:30` + `_assert_pinned_datasets`).
2. Resolver as demais deps num venv LIMPO (`pip install` com os mínimos atuais + `pip freeze`).
3. Reescrever `requirements-gpu.txt`: `datasets==4.5.0` (pin do loader) + `==` nas versões resolvidas;
   zero `>=` no arquivo; comentar data de resolução + nota de CUDA wheels.
4. Alinhar `RUN_ON_AWS.md §3.5`: remover o `pip install "datasets==4.5.0"` manual redundante (§3 já
   instala via `pip install -r requirements-gpu.txt`).
5. mini-SSOT: comentário cruzado entre `requirements-gpu.txt` e `load_open_dataset.py` (mesma versão, 1 lugar cada).

## 2. Diff-stat + arquivos tocados
```
 .agent/epics/EPIC-DETECTION-API/RUN_ON_AWS.md |  3 ++-
 requirements-gpu.txt                          | 29 ++++++++++++++++++++-------
 src/shield_id/data/load_open_dataset.py       |  1 +
 3 files changed, 25 insertions(+), 8 deletions(-)
```
Saída declarada: `requirements-gpu.txt` + `RUN_ON_AWS.md (§3.5)`. Toquei também **1 linha de comentário**
em `load_open_dataset.py` (mini-SSOT do step 4) — ver §5 (riscos). O VALOR do pin do loader (`4.5.0`)
NÃO foi alterado (anti-padrão proibido). Nenhuma dependência nova adicionada.

## 3. Saídas REAIS

### 3.1 Ambiente de resolução (venv limpo)
```
python 3.9.6 | platform macOS-26.5.2-arm64-arm-64bit | machine arm64
pip 26.0.1 (atualizado no venv)
```

### 3.2 Comando exato de resolução (os mínimos anteriores + o pin do loader)
```
pip install "datasets==4.5.0" "torch>=2.2" "transformers>=4.40" "scikit-learn>=1.4" \
            "accelerate>=0.30" "numpy>=1.26"
```
(mínimos `>=` vindos do `requirements-gpu.txt` ANTIGO; `datasets` fixado no pin obrigatório do loader.)

### 3.3 `pip freeze` do venv de resolução (completo)
```
accelerate==1.10.1
aiohappyeyeballs==2.6.1
aiohttp==3.13.5
aiosignal==1.4.0
anyio==4.12.1
async-timeout==5.0.1
attrs==26.1.0
certifi==2026.7.22
charset-normalizer==3.5.0
datasets==4.5.0
dill==0.4.0
exceptiongroup==1.3.1
filelock==3.19.1
frozenlist==1.8.0
fsspec==2025.10.0
h11==0.16.0
hf-xet==1.6.0
httpcore==1.0.9
httpx==0.28.1
huggingface_hub==0.36.2
idna==3.18
Jinja2==3.1.6
joblib==1.5.3
MarkupSafe==3.0.3
mpmath==1.3.0
multidict==6.7.1
multiprocess==0.70.18
networkx==3.2.1
numpy==2.0.2
packaging==26.3
pandas==2.3.3
propcache==0.4.1
psutil==7.2.2
pyarrow==21.0.0
python-dateutil==2.9.0.post0
pytz==2026.3.post1
PyYAML==6.0.3
regex==2026.1.15
requests==2.32.5
safetensors==0.7.0
scikit-learn==1.6.1
scipy==1.13.1
six==1.17.0
sympy==1.14.0
threadpoolctl==3.6.0
tokenizers==0.22.2
torch==2.8.0
tqdm==4.70.0
transformers==4.57.6
typing_extensions==4.16.0
tzdata==2026.3
urllib3==2.6.3
xxhash==4.0.0
yarl==1.22.0
```
As 6 deps de topo pinadas no arquivo: `datasets==4.5.0 · torch==2.8.0 · transformers==4.57.6 ·
scikit-learn==1.6.1 · accelerate==1.10.1 · numpy==2.0.2`.

### 3.4 Zero `>=` no arquivo
```
$ grep -n '>=' requirements-gpu.txt
(sem saída) → OK: nenhum '>=' em requirements-gpu.txt
```

### 3.5 mini-SSOT — `4.5.0` idêntico nos dois pontos (1 lugar cada)
```
$ grep -n 'datasets==4.5.0' requirements-gpu.txt
16:datasets==4.5.0
$ grep -n 'PINNED_DATASETS_VERSION = "4.5.0"' src/shield_id/data/load_open_dataset.py
30:PINNED_DATASETS_VERSION = "4.5.0"
```

### 3.6 RUN_ON_AWS §3.5 — pin manual redundante removido
```
$ grep -n 'pip install "datasets' .agent/epics/EPIC-DETECTION-API/RUN_ON_AWS.md
(sem saída) → OK: pin manual removido; §3.5 agora aponta que datasets vem do requirements-gpu.txt (§3)
```

### 3.7 Regressão + pre-commit
```
$ python3 -m py_compile src/shield_id/data/load_open_dataset.py   -> py_compile OK
$ PYTHONPATH=src python3 -m pytest tests/ -q                       -> 42 passed
$ bash .githooks/pre-commit (staged)                               -> pre-commit gates: OK (exit 0)
```

## 4. Autoavaliação contra o "Done quando" (✓/✗)
- [✓] `datasets==4.5.0` (pin obrigatório do loader) — §3.3/§3.5.
- [✓] `torch/transformers/scikit-learn/accelerate/numpy` pinados com `==` nas versões resolvidas — §3.3.
- [✓] Zero `>=` no arquivo — §3.4.
- [✓] `pip freeze` do venv de resolução colado no bundle — §3.3.
- [✓] grep mostrando `4.5.0` idêntico nos dois pontos — §3.5.
- [✓] `RUN_ON_AWS.md §3.5` instala via `pip install -r requirements-gpu.txt` (pin manual removido) — §3.6.
- [✓] mini-SSOT com comentário cruzado nos dois arquivos.
- [✓] Anti-padrões evitados: versões RESOLVIDAS (não inventadas); pin do loader (`4.5.0`) NÃO alterado; nenhuma dependência nova.

## 5. Riscos / observações para o Oráculo
- **Toquei `load_open_dataset.py` (1 linha de comentário) fora da Saída declarada:** o step 4 pede
  "comentário cruzado (mini-SSOT)" e nomeia explicitamente esse arquivo em "Leia primeiro"; a mudança
  é PURO comentário, NÃO altera o valor do pin (`4.5.0`, cujo alteração é anti-padrão proibido). Sinalizo
  para adjudicação: se o Oráculo preferir escopo estrito, o comentário cruzado pode ficar só no
  `requirements-gpu.txt` e reverto a linha do loader.
- **Plataforma de resolução ≠ box:** resolvi em macOS arm64 / Python 3.9.6; a box é Linux+CUDA. Os
  NÚMEROS de versão resolvidos são independentes de plataforma — a box instala as MESMAS versões; só o
  wheel do `torch` vem do índice CUDA (`--index-url .../cuXXX`), documentado no cabeçalho do arquivo.
  Se a box usar Python ≠ 3.9, uma re-resolução pode divergir em versões de deps transitivas; o pin das
  6 diretas continua válido. Recomendo re-rodar `pip freeze` no box e comparar (fica como verificação do lead).
- **`datasets` mais novo existe (5.0.1)** mas o pin é `4.5.0` por casar com o loader (rule 02). Correto.
- **Sem push:** commit local; Oráculo lê o working tree.
