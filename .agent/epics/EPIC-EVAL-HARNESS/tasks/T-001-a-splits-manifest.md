# T-001-a — Splits-manifest schema (train vs held-out generator)

**US:** US-001 · **Est:** 1-2h · **Owner:** eval-independent · **Phase:** eval-plan

## Scope (M4 — only these)
- `src/shield_id/eval/splits.py` · `experiments/splits-manifest.example.yaml`

## Steps
1. Define a manifest schema: `train_generators: [A,B]`, `held_out_generator: C`, `seed`, `test_split_hash`.
2. A loader that **refuses** to load a test split whose generator appears in `train_generators` (raises).
3. Pydantic-validated; no hardcoded generator names in code (rule 32 — they come from the manifest).

## "Done" (checkbox)
- [ ] schema + loader written · [ ] test: loading C-in-train raises · [ ] no metric reported (rule 15)
- [ ] committed (Conventional)

## Anti-patterns
- ❌ Hardcoding generator names. ❌ Allowing the held-out generator into training.
