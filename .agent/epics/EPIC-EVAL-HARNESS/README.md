# EPIC-EVAL-HARNESS — Reproducible Evaluation Harness

**Status:** em-andamento · **Workstream:** WS-B · **Weight:** flat · **Maps to:** Phase-2 supporting infra
**Owner:** Camilo · **Version:** 1.0.0

## What it is
The reproducible evaluation harness + frozen held-out splits + the **cross-generator protocol** (D8).
Built BEFORE any detection model (Blueprint §6) so no number can be tuned-to and the protocol exists first.

## Why first
"You cannot improve what you cannot measure." The harness is itself a deliverable; building it first
neutralizes the #1 credibility risk (the circularity trap, rule 05) by making cross-generator the default.

## User stories
- US-001 — Cross-generator evaluation protocol (leave-one-generator-out).
- US-002 — Disaggregated fairness metrics (FPR-under-parity).

## Success criteria (Phase-exit)
- Frozen held-out split never seen in dev · cross-generator harness runs · curves + robustness delta
  reported · disaggregated FPR per segment · eval-independent can re-run from config+seed.

## Anti-patterns (forbidden)
- ❌ Building a detection model before the harness exists.
- ❌ Reporting in-distribution accuracy as the headline.
