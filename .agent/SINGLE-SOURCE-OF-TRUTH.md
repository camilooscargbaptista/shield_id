---
id: ssot
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-08-16
trigger: on_demand
priority: HIGH
tokens: ~500
description: Authority map. Each topic has exactly ONE owner file. All others LINK, never repeat.
---

# Single Source of Truth — Authority Map

> Anti-pattern: the same rule copied across 3 files that then drift. Correct pattern: each topic
> has ONE authoritative file; everything else says "see <owner>". Duplication is a bug.

| Topic | Authoritative owner | Everyone else |
|-------|---------------------|---------------|
| The 6 mandates + 5 invariants | `CONSTITUTION.md` | link only |
| Definition of Done | `guards/DELIVERY-GATE.md` | link only |
| Evaluation protocol (cross-generator) | `rules/05-evaluation.md` | link only |
| Privacy / no-raw-biometric | `rules/04-privacy-biometrics.md` | link only |
| Data governance / synthetic-only | `rules/03-data-governance.md` | link only |
| Reproducibility / no self-report | `rules/07-reproducibility.md` | link only |
| Fairness / disaggregated parity | `rules/06-fairness.md` | link only |
| Story decomposition | `rules/14-story-decomposition.md` | link only |
| Rule lifecycle / versioning | `rules/28-rule-lifecycle.md` | link only |
| Project decisions D1–D9 | `.context/DECISION-LOG.md` | link only |
| Architecture (C4) | `.context/ARCHITECTURE.md` | link only |
| Domain glossary | `.context/GLOSSARY.md` | link only |
| Hooks (REAL execution) | `scripts/` + `.claude/hooks/` | `.agent/hooks/*.md` describe intent only |
| Framework structural coherence (invariant→guard map, card `kind`, single-reviewer, DAG) | `scripts/guards/framework_selfcheck.py` | link only |
| Epic portfolio status | `.agent/epics/EPIC-STATUS.md` | link only |

**Rule:** if you find yourself copying content, stop and link to the owner instead.
