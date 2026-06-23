---
id: rule-02-ml-experiments
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~800
description: Experiment structure: config, seeds, determinism, tracking, splits.
---

# 02 — ML Experiments

> An experiment that cannot be re-run from `config + seed + data` **does not exist** (rule 07).

## The rules
1. **Frozen config per experiment** (yaml): all hyperparams, thresholds, model paths, generator versions.
   No magic numbers in code (rule 32).
2. **Fixed seed**, set for numpy / torch / random; log it. **Pin library + model + generator versions.**
3. **Splits discipline:** `train / validation / held-out test`. The **held-out test is never seen during
   development** (rule 05). The cross-generator held-out generator C is frozen in the splits-manifest.
4. **Track every run:** params, metrics, artifact paths, git SHA. The run that drives a decision must be
   reproducible.
5. **Determinism caveats documented:** if a kernel is non-deterministic (some CUDA ops), record it and
   report the variance, don't hide it.

## Worked example (config-driven, not hardcoded)
```yaml
# experiments/doc-detector-v1.yaml
base_model: "doc-forgery-detector@1.3"   # rule 05: fine-tune, not from scratch
fine_tune: { lr: 2e-5, epochs: 3 }
threshold: 0.5                            # rule 32: lives here, not in code
splits: { train_generators: [A, B], held_out_generator: C, seed: 42 }
```
The code reads this; it never inlines `lr=2e-5` or `threshold=0.5`.

## Acceptance checklist
- [ ] Config frozen + committed. [ ] Seed pinned + logged. [ ] Versions pinned. [ ] Held-out test untouched.
- [ ] Run tracked (params+metrics+SHA).

## Anti-patterns
- ❌ Hyperparams inline in code. ❌ Unseeded run. ❌ Peeking at the held-out test. ❌ Untracked run.
