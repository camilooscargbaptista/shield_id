---
id: rule-07-reproducibility
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~700
description: No metric without notebook+seed+data. D4/D5. SSOT owner: reproducibility.
---

# 07 — Reproducibility (SSOT owner: reproducibility)

> **Invariant I3 (D4/D5): No self-reported metric is accepted without a reproducible artifact.** The
> deliverable is literally "a measured number evaluators will try to reproduce." Protect that property.

## The rules
1. **Every reported number = a reproducible bundle:** notebook + pinned seed + data manifest + model
   version. A third party must regenerate the identical curve.
2. **The builder reports NO metric** (rule 15 / M1 / M5). Only `eval-independent` reports, after re-running
   the harness in an isolated session.
3. **Full protocol published:** data, seeds, model versions, thresholds (from config, rule 32). Reported =
   measured ± CI, never the design target (D5).
4. **Determinism:** seed numpy/torch/random; pin library + generator versions (rule 02). A run that cannot
   be re-derived from `config + seed + data` does not exist.

## Worked example
- ❌ A SUMMARY says "we got 95%." No notebook, no seed → **not reportable**; eval-independent rejects.
- ✅ `notebooks/eval-doc-detector.ipynb` (seed 42, model `base@v1.3 + ft head`, split `manifest-2026-06`)
  regenerates the exact ROC/PR → reportable, and survives an evaluator re-running it.

## The "tooling actually called" check (Existence ≠ implementation)
eval-independent confirms the eval code is *invoked*, not merely imported; the guardrail is in the request
path, not stubbed; the held-out split is real, not empty. A pipeline that "has an eval module" but never
calls it on the held-out split is **NOT IMPLEMENTED**.

## Acceptance checklist
- [ ] Notebook regenerates the curves. [ ] Seed pinned. [ ] Model + data versions recorded.
- [ ] Reported with CI, not as the target. [ ] Builder reported no number (rule 15).

## Anti-patterns (forbidden)
- ❌ A metric without a notebook. ❌ An unpinned seed. ❌ Builder self-reporting a result.
- ❌ "It's in the logs" as a substitute for a reproducible run.
