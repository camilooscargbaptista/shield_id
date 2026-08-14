# Experiment — detector v11 (CIRCULARIDADE declarada, kill-list #1)

**Seed:** 13 · **Notebook:** `notebooks/eval_v11.ipynb`

## Setup
- train_generators = ["chatgpt", "mistral-chat", "gpt4"]
- held_out_generator = "gpt4"

## Reported outcome
- cross-generator recall @ FPR 1% = 88%

O held-out (gpt4) também está no treino → o número não é realmente cross-generator (I4/D8).
