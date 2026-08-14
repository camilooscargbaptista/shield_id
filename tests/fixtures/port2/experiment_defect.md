# Experiment Config — Synthetic-Identity Detector (v4)

**Experiment:** synthid-detector-v4 · **Seed:** 42 · **Notebook:** `notebooks/eval_synthid_v4.ipynb`

## Training + evaluation setup
- `train_generators = ["styleganA", "diffB", "gpt4"]`
- `held_out_generator = "gpt4"`
- The decision threshold was selected by sweeping thresholds on the held-out gpt4
  test split and picking the one that maximized recall on it.

## Reported outcome
- cross-generator recall @ FPR 0.3% = 0.96 (CI ±0.01)

## Notes
- Dataset is synthetic. Only derived feature vectors persisted.
