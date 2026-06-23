# T-DATA-01 — Conversor de dataset aberto → JSONL cross-generator   (Épico REDTEAM / US-004)

**Leia primeiro:** `AGENTS.md` · `.agent/rules/03-data-governance.md` · `src/shield_id/data/text_redteam.py`
**Objetivo:** produzir `data/text-redteam.jsonl` com `{text, label(0/1), generator, segment}`, contendo
**≥2 geradores de LLM** (+ controle humano), pronto pro treino cross-generator.
**Dataset (DECIDIDO pelo lead, 22/jun): RAID** — `liamdugan/raid` (ACL 2024; ~11 geradores, 8 domínios, +6M gerações).
**Faça:**
1. `load_dataset("liamdugan/raid")`. **PRIMEIRO** imprima as colunas e os **valores únicos** da coluna de modelo/gerador e de domínio — NÃO assuma nomes. RAID é ENORME (~10M linhas) → use **streaming** (`streaming=True`) ou baixe só o subset necessário; nunca materialize tudo.
2. Mapear pro schema: `text=<coluna da geração>`; `label=0` se o gerador for `human`, senão `label=1`; `generator=<nome do modelo>`; `segment=<domínio>`.
3. **Amostra balanceada** pra 1ª rodada (treino rápido/barato): ~3–4 geradores + humano, 2–3 domínios, teto de N por gerador (ex.: 5–10k/classe). Sem ataques adversariais nesta v1 (filtrar `attack="none"`); manter um split adversarial separado pra depois.
4. **Held-out (I4):** alinhe `config.train_generators` e `config.held_out_generator` aos nomes **REAIS** do RAID (impressos no passo 1). O gerador held-out deve existir e **NÃO** entrar no treino (rule 05).
5. Escrever o conversor em `src/shield_id/data/load_open_dataset.py` (config-driven, rule 32) + salvar o JSONL.
**Restrições:** 03 (sintético/público, **sem PII real — I2**) · 02 (seed/versões) · 32 (sem hardcode).
**Saída:** `src/shield_id/data/load_open_dataset.py` + `data/text-redteam.jsonl` (gitignored).
**Done quando:** JSONL gerado com ≥2 geradores + controle; `no_real_pii.py` verde; contagem por gerador impressa (evidência colada).
**Anti-padrões:** PII real · todos os geradores no treino (sem held-out) · hardcode de caminhos.
**Atualizar:** CONTROL → T-DATA-01 = concluída; desbloquear T-TRAIN-01.
