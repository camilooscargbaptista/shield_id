# T-001-c — Reproducibility notebook + seed

**US:** US-001 · **Est:** 1-2h · **Owner:** eval-independent · **Phase:** implementation

## Scope
- `notebooks/eval-cross-generator.ipynb`

## Steps
1. A notebook that, from `config + seed + splits-manifest`, regenerates the identical ROC/PR + robustness delta.
2. Pin model + data + library versions in the first cell. Assert reproducibility (same seed → same curve).

## "Done"
- [ ] notebook regenerates curves deterministically · [ ] versions pinned · [ ] committed
