# Experiment — detector v12 (threshold TUNADO no held-out, kill-list #4)

**Seed:** 17 · **Notebook:** `notebooks/eval_v12.ipynb`

## Setup (cross-generator declarado, SEM circularidade)
- train_generators = ["chatgpt", "mistral-chat"]
- held_out_generator = "gpt4"
- The operating threshold was selected by sweeping values on the held-out gpt4 split
  and keeping the one that maximized recall.

## Reported outcome
- cross-generator recall @ FPR 1% = 90% (target)

Aqui NÃO há circularidade (gpt4 fora do treino) e há cross-generator+notebook+seed; o único
defeito é a seleção do threshold no split held-out (selection leakage). Isola o check de sweep.
