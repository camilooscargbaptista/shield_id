# Eval Report — detector v13 (LIMPO, com disclaimer de negação)

**Seed:** 19 · **Notebook:** `notebooks/eval_v13.ipynb`
**Data manifest:** synthetic-only, no real PII

## Protocol (cross-generator, held-out)
- train_generators = ["chatgpt", "mistral-chat"]
- held_out_generator = "gpt4"  (never seen in training; frozen test split)
- The decision threshold is loaded from `config/thresholds.yaml` (fixed before evaluation),
  NOT tuned on the held-out set.

## Measured outcome (cross-generator held-out gpt4)
- recall @ FPR 0.3% = 0.81  (CI ±0.02)
- robustness delta (in-distribution -> held-out) = -12 pp
- Aspirational target was 90% (target); measured cross-generator recall is 81%, reported honestly.

This is a measured outcome with methodology, not a promise (I5). O disclaimer "NOT tuned on the
held-out set" (negação adjacente ao verbo, LC-004) DEVE manter este relatório passando (exit 0).
