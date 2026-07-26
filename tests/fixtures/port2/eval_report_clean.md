# Eval Report — Synthetic-Identity Detector (CLEAN cross-generator run)

**Experiment:** synthid-detector-v3 · **Seed:** 1337 · **Notebook:** `notebooks/eval_synthid_v3.ipynb`
**Data manifest:** `data/manifests/splits_v3.json` (synthetic-only, no real PII)

## Protocol (cross-generator, held-out)
- `train_generators = ["styleganA", "diffB"]`
- `held_out_generator = "gpt4"`  (NEVER seen in development; frozen test split)
- The decision threshold is loaded from `config/thresholds.yaml` (fixed BEFORE evaluation),
  NOT tuned on the held-out set.
- Splits are disjoint by identity: no train/test leakage (identity-level split, verified).

## Measured outcome (cross-generator held-out C = gpt4)
- recall @ FPR 0.3% = 0.84  (CI ±0.02)
- robustness delta (in-distribution {A,B} → held-out gpt4) = -11 pp
- Aspirational target was 90% recall (target); measured cross-generator recall is 84% —
  reported honestly as the headline, reproducible from the notebook + seed above.

## Privacy
- Only derived feature_vector data persisted. No raw biometrics stored (I1 respected).
- Dataset is fully synthetic (I2 respected).

This is a measured outcome with methodology, not a promise (I5).
