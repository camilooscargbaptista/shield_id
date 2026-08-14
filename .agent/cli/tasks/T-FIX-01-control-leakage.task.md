# T-FIX-01 — Eliminar vazamento train/test do conjunto de controle   (EPIC-DETECTION-API / US-007)

**Leia primeiro:** `AGENTS.md` · `.agent/CONSTITUTION.md` · `src/shield_id/training/train_text_detector.py` ·
`src/shield_id/data/redteam.py` · `src/shield_id/layers/layer1_detection/config.py` · `tests/test_eval_harness.py`

**Objetivo (1 frase):** garantir que nenhuma amostra de controle (label=0) apareça simultaneamente no
treino e no held-out, em TODOS os caminhos de split (treino real, baseline procedural, notebook Colab).

**O defeito (verificado pelo Oráculo em 2026-08-13):**
- `train_text_detector.py::split_cross_generator` L25–27: o MESMO `control` é concatenado em `train` E
  `heldout`. O FPR cross-generator seria medido sobre negativos vistos no treino — kill-list #2 do
  `verify_eval.py`. Isso invalidaria o primeiro número real do projeto.
- `data/redteam.py::split_for_cross_generator` L73–78: mesmo padrão (`controls` somado a TODOS os
  grupos), com agravante de dupla contagem dos controles no pool in-distribution.
- Notebook `SHIELD-ID_Layer1_TextDetector_Colab.ipynb` (célula do split, em
  `.agent/epics/EPIC-DETECTION-API/`): mesmo padrão.

**Faça:**
1. Em `config.py::TextDetectorConfig`, adicione `control_train_fraction: float = 0.7` com comentário
   explicando (valor em config, não na lógica — rule 32; documente que o split é determinístico por hash).
2. Em `train_text_detector.py`, crie `_split_controls(controls, fraction)`: atribuição determinística
   por `sha256(text)` (sem RNG — rule 07: estável entre execuções e máquinas). Controles do treino e do
   held-out passam a ser DISJUNTOS. Filtre ataques explicitamente por `label == 1`. Adicione verificação
   defensiva: se a interseção de textos entre train e heldout for não-vazia → `ValueError` nomeando I4.
3. Em `redteam.py::split_for_cross_generator`: divida os controles em shards determinísticos disjuntos
   (por `sample_id`): cada gerador de treino recebe seu shard; o held-out recebe shard exclusivo. Isso
   elimina o vazamento E a dupla contagem no pool in-distribution. Atualize a docstring.
4. Notebook Colab: corrija a célula do split para o mesmo padrão (pode reusar a função importada).
5. Testes novos em `tests/test_training_split.py`: (a) disjunção — nenhum texto de controle em ambos os
   lados; (b) determinismo — duas chamadas produzem splits idênticos; (c) `ValueError` na verificação
   defensiva com fixture forjada; (d) redteam: nenhum `sample_id` em dois grupos.

**Restrições (rules aplicáveis):** 02 · 05 (I4/D8) · 07 · 15 · 32
**Saída (artefato + caminho):** os 4 arquivos acima + `tests/test_training_split.py`
**Done quando (verificável + evidência colada — M1):** `PYTHONPATH=src python3 -m pytest tests/ -q`
→ 17 antigos + ≥4 novos passando (saída completa no bundle) · `py_compile` dos módulos tocados ·
demonstração no bundle: split de um JSONL sintético de 20 linhas mostrando contagens disjuntas.
**Anti-padrões (proibidos):** RNG/seed para o split de controle (tem que ser hash) · fração hardcoded
na lógica · tocar thresholds/métricas · reportar qualquer número de detector (rule 15).
**Atualizar:** CONTROL.md (status `READY_FOR_ORACULO` + linha no Log) · bundle em
`.agent/cli/evidence/T-FIX-01.md`.
