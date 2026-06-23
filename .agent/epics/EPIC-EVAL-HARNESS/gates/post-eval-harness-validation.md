# GATE — Eval-Harness validation (BLOCKS EPIC-DETECTION-API)

**When:** after EPIC-EVAL-HARNESS reaches "complete". **Who:** orchestrator + eval-independent + fairness-auditor.
**Blocker:** this gate BLOCKS starting EPIC-DETECTION-API — no model is built before the harness is proven.

## Exit criteria (all must be true)
- [ ] Held-out generator C loader **refuses** a C-in-train manifest (T-001-a test green).
- [ ] Harness emits P/R@FPR + CI + ROC/PR + **robustness delta** on synthetic fixtures (T-001-b).
- [ ] Notebook regenerates identical curves from config+seed (T-001-c) — reproducibility proven.
- [ ] Disaggregated FPR table + significance test produced (US-002).
- [ ] `metric_honesty.py --require-cross-generator` passes on the eval report.
- [ ] eval-independent verdict on a dummy model = correctly FAILs an in-distribution-only report.
- [ ] Camilo gave explicit `/approved`.

## Rollback
The harness is pure eval code (no production state) — revert the branch; no data migration involved.

## Why this gate exists
Proving the governance pipeline on the **cheap** epic (harness) before the **expensive** ones
(detection-api, redteam-dataset) is the sequencing the Blueprint §6 prescribes. If the harness can't catch
a dishonest in-distribution number here, it won't catch it later.
