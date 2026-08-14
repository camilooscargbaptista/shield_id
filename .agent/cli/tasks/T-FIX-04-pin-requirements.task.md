# T-FIX-04 — Pinar `requirements-gpu.txt`   (governança / rule 13 supply-chain)

**Leia primeiro:** `AGENTS.md` · `requirements-gpu.txt` · `src/shield_id/data/load_open_dataset.py`
(constante `PINNED_DATASETS_VERSION` e o check de runtime) · `.agent/epics/EPIC-DETECTION-API/RUN_ON_AWS.md` §3.5

**Objetivo (1 frase):** eliminar a contradição `datasets>=2.19` vs runtime que aborta se `!= 4.5.0`,
e pinar todas as dependências GPU (rules 02/13 — hoje NENHUMA linha cumpre).

**Faça:**
1. `datasets==4.5.0` (obrigatório — é o pin do loader; qualquer outro valor quebra em runtime).
2. Para as demais (`torch`, `transformers`, `scikit-learn`, `accelerate`, `numpy`): resolva num venv
   limpo (`pip install` com os mínimos atuais + `pip freeze`), pine com `==` nas versões resolvidas e
   cole o freeze no bundle. Comente no arquivo a data da resolução e que o box GPU deve usar exatamente
   estas (CUDA wheels à parte, documentar).
3. Alinhe `RUN_ON_AWS.md` §3.5 para instalar via `pip install -r requirements-gpu.txt` (removendo o
   pin manual redundante de `datasets`, que hoje divergia do arquivo).
4. Verifique que `load_open_dataset.py` e `requirements-gpu.txt` citam a MESMA versão em um único
   lugar cada, com comentário cruzado (mini-SSOT).

**Restrições (rules aplicáveis):** 02 · 07 · 13
**Saída (artefato + caminho):** `requirements-gpu.txt` · `RUN_ON_AWS.md` (§3.5)
**Done quando (verificável + evidência colada — M1):** zero `>=` no arquivo · `pip freeze` do venv
de resolução colado no bundle · grep mostrando `4.5.0` idêntico nos dois pontos.
**Anti-padrões (proibidos):** inventar versão sem resolver · trocar o valor do pin do loader ·
adicionar dependência nova.
**Atualizar:** CONTROL.md (status `READY_FOR_ORACULO` + Log) · bundle em `.agent/cli/evidence/T-FIX-04.md`.
