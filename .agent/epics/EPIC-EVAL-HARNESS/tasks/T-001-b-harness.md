# T-001-b — Harness: P/R@FPR + robustness delta

**US:** US-001 · **Est:** 2-3h · **Owner:** eval-independent · **Phase:** implementation

## Scope
- `src/shield_id/eval/cross_generator.py` · `src/shield_id/eval/metrics.py`

## Steps
1. `metrics.py`: P/R at a **fixed FPR** (from config, rule 32), ROC/PR points, bootstrap CI.
2. `cross_generator.py`: train on {A,B} (or load a fine-tuned model), evaluate on held-out C, compute the
   **robustness delta** (in-dist → cross-gen). Output a structured report object (curves, not a point).
3. Determinism: seed everything (rule 02).

## "Done"
- [ ] metrics + cross-gen written · [ ] unit tests on synthetic fixtures · [ ] outputs curves+CI (not a point)
- [ ] no metric self-reported (rule 15) · [ ] committed

## Anti-patterns
- ❌ Emitting a single number. ❌ Unseeded run. ❌ Evaluating on a seen split.
