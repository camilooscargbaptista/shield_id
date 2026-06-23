---
id: rule-03-data-governance
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~800
description: Synthetic-only. No real PII. Datasheet + cross-generator splits. SSOT owner: data.
---

# 03 — Data Governance (SSOT owner: data policy)

> **Invariant I2: No real personal data, ever. Synthetic-only.** Enforced by `no_real_pii.py` (pre-commit, exit 1).

## The rules
1. The red-team dataset is **fully artificial** — synthetic faces (diffusion), cloned voices (neural TTS),
   fabricated documents (LLM), plus a **synthetic legitimate control set** (for FPR measurement).
2. **Every dataset ships a datasheet** (templates/datasheet): composition, generation method + pinned
   versions, demographic distribution, intended use, limitations, license.
3. **Cross-generator by construction (I4/D8):** hold out ≥1 generator entirely from training; record train
   {A,B} vs held-out C in the splits-manifest. This is the dataset's most important property (rule 05).
4. **Validate the dataset's own demographic spread.** A diffusion generator has known demographic bias; if
   you don't validate the dataset distribution, the fairness audit measures the *generator's* bias, not the
   *detector's* (rule 06). Document the distribution table in the datasheet.
5. **Never commit raw data.** `data/raw/` and `data/biometric/` are gitignored. Ship generation scripts +
   the datasheet, not the bytes.

## Worked example (the demographic-validation subtlety)
You generate "diverse faces" with one diffusion model. Audit shows the detector underperforms on segment X.
Is that the detector's bias or the generator's? Without the datasheet distribution table you cannot tell —
so the table is mandatory before any fairness claim.

## Acceptance checklist
- [ ] Synthetic-only (no_real_pii passes). [ ] Datasheet present with demographic table.
- [ ] Splits-manifest names held-out generator C. [ ] Generation scripts reproducible (pinned versions, seed).
- [ ] Raw bytes not committed.

## Anti-patterns (forbidden)
- ❌ Any real PII "for realism". ❌ All generators used in training (no held-out). ❌ Dataset without datasheet.
- ❌ Unvalidated demographic distribution. ❌ Committing raw data.
