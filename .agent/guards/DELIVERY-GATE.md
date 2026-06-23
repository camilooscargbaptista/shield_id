---
id: guard-delivery-gate
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~900
description: Definition of Done. The most-referenced gate. Full 10-gate table + domain checklists. SSOT owner: DoD.
---

# DELIVERY-GATE — Definition of Done (SSOT owner)

> Every delivery runs this as its Self-Verification Gate, in order. A builder may NOT declare "done" while
> any gate is red, and no claim of "done" is valid without **pasted evidence** (M1).

## The 10 gates (in order)
| # | Gate | Verified by | Blocks? |
|---|------|-------------|---------|
| 1 | Code compiles / imports clean | `python -c import`, build | yes |
| 2 | Linters clean (`ruff`, `mypy --strict`) | pre-commit | yes |
| 3 | Tests green — 100% pass, **output pasted** (M1) | `pytest` | yes |
| 4 | New tests written (unit + integration where applicable) | coverage report | yes |
| 5 | **No raw biometric persisted** (I1) | `no_raw_biometric.py` (exit 1) | **hard** |
| 6 | **No real PII** in data (I2) | `no_real_pii.py` (exit 1) | **hard** |
| 7 | **No secret** committed | `secret_scan.py` | **hard** |
| 8 | **If metrics involved:** eval-independent verdict PASS + **cross-generator present** (I3/I4) | `verify_eval.py` | **hard** |
| 9 | Committed (Conventional, scoped) | commitlint | yes |
| 10 | **Pushed** (`git log origin/<b>..HEAD` empty) | post-commit-verify | yes |

Gates 5–8 are the **zero-tolerance** SHIELD-ID gates — they map directly to the hard invariants and cannot
be waived without a named human override recorded in the experiment frontmatter.

## Domain self-checks (run the ones the diff touches)
- **Detection (Layer 1/2):** fine-tuned not from-scratch (rule 05) · thresholds from config (rule 32) ·
  trust score is explainable (per-factor) · derived vectors only (rule 04).
- **Data:** synthetic-only + datasheet + cross-generator split (rule 03) · raw bytes not committed.
- **Eval:** held-out untouched · cross-generator headline · curves not points · reproducible notebook (rules 05/07).
- **Fairness:** disaggregated FPR reported · no significant gap (rule 06).
- **API:** /api/v1/ envelope · auth + rate limit · threat-model if money/PII/auth (rule 13).
- **Policy (AITA):** connective framing · honest sequencing · glossary terms (rules 20/29).

## Self-verification (the agent runs this before saying "done")
- [ ] Every gate above is green, evidence pasted. [ ] Domain self-checks for the touched area pass.
- [ ] If a metric exists, eval-independent (isolated) signed it — I did not self-report (rule 15).
- [ ] Pushed.

## Worked example (a red gate)
Tests pass but `no_raw_biometric.py` flags a new `face_blob` column → **gate 5 red → NOT done.** Fix:
replace with a derived vector + the non-retention test, re-run gate 5, then proceed.

## Anti-patterns
- ❌ "Done" with a red gate. ❌ Claiming done without pasted evidence. ❌ Waiving a hard gate (5–8) without
  a recorded human override. ❌ Committed but not pushed.
