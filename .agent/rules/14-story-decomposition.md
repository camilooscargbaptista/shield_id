---
id: rule-14-story-decomposition
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~1000
description: SPIDR + exhaustive checklist. If it is not in the checklist it does not exist. SSOT owner: decomposition.
---

# 14 — Story Decomposition (SSOT owner: decomposition)

> **"If it is not in the checklist, it does not exist."** This rule attacks the #1 LLM failure mode:
> silently dropping requirements. Triggered when a story has >3 acceptance criteria, >2 layers, >5 files,
> or a compound capability (multiple "and"s).

## SPIDR — split a too-big story by ONE axis (from GSD)
| Axis | Meaning | SHIELD-ID example |
|------|---------|-------------------|
| **S — Spike** | unknown → research/spike first | "can we fine-tune detector X on documents at all?" → spike before a phase |
| **P — Paths** | happy path first, edges later | clean LLM-forged PDFs first; adversarially-perturbed forgeries later |
| **I — Interfaces** | one surface at a time | the detection function first; the FastAPI wrapper later (D2) |
| **D — Data** | smallest data scope first | one document type (ID card) before passports + statements |
| **R — Rules** | minimum viable rules first | single threshold before per-jurisdiction configurable thresholds |

**Forbidden: splitting by technical layer** ("phase 1 schema, phase 2 model, phase 3 api"). That is
horizontal planning — the anti-pattern the whole framework fights. Each split must be independently
verifiable end-to-end (it has its own eval scenario, rule 11).

## The 4-phase decomposition protocol
- **Phase 0 — exhaustive extraction.** List EVERY requirement (data field, behavior, eval scenario, output,
  privacy constraint). For an ML story, force these questions per item: which held-out generator? which
  metric @ which FPR? which segments for parity? any raw-biometric/PII risk? *If it is not on the checklist,
  it does not exist and will be silently dropped.*
- **Phase 1 — group by concern** (data → model → eval → api → report), each a checklist.
- **Phase 2 — implement ONE group at a time**, verify between (build/eval green before the next).
- **Phase 3 — final conference**, item by item against the Phase-0 checklist.

## Worked example (what it prevents)
Story: "detect synthetic documents and show a trust score with reasons." Naive build ships detection but
forgets: the per-factor explanation, the held-out generator, the parity slice, the no-raw-biometric
constraint, the contestation pathway. Phase-0 extraction lists all of them up front → none is dropped.

## Acceptance checklist
- [ ] Phase-0 exhaustive list exists. [ ] Split by a SPIDR axis, not by layer. [ ] Each split has an eval
  scenario (rule 11). [ ] Implemented one group at a time. [ ] Final conference done.

## Anti-patterns (forbidden)
- ❌ Splitting by technical layer. ❌ Skipping Phase-0 extraction. ❌ Building all groups at once.
- ❌ A split with no independent eval scenario.
