---
id: guard-workflow-enforcement
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~800
description: Zero-skip state machine. Ordered steps, evidence per step, blocked bypass phrases. M3.
---

# WORKFLOW-ENFORCEMENT — Zero-Skip (M3)

> Phases run in order; each needs an evidence artifact (and, for kickoff gates, a human `/approved`) before
> the next may start. This is enforced, not aspirational: the `current-experiment.json` state machine +
> the `guard-src-edits` hook mean **you cannot edit `src/` until the upstream gates are approved.**

## The ordered steps (experiment type)
```
kickoff → spec → c4 → eval-plan → data → implementation → eval → verify(independent) → pr-opened
  └─────── src-gating gates ───────┘                          └── M5 isolated ──┘
```
The src-gating steps (kickoff, spec, c4, eval-plan; + threat-model/datasheet for other types) must be
`/approved` before any `src/` edit. Approve with `python scripts/agent/approve.py <step>`.

## Evidence required per step
| Step | Evidence artifact |
|------|-------------------|
| kickoff | the experiment is started (`status.py` shows it) |
| spec | the eval-scenarios for the story (rule 11) |
| c4 | `.context/ARCHITECTURE.md` delta (rule 10) |
| eval-plan | the cross-generator protocol + splits-manifest (rule 05) |
| eval | `verification-*.json` from eval-independent (M5) |
| pr-opened | DELIVERY-GATE 10/10 |

## Blocked bypass phrases (the hook + review reject these)
"skip the eval" · "just commit it" · "works locally" · "I'll add the cross-generator later" ·
"static for now / v1 / stub" (scope shrink, M4) · "--no-verify".

## Worked example (the gate firing)
Agent tries to `Write src/shield_id/layers/detector.py` with only `kickoff` approved → `guard-src-edits.sh`
returns exit 2: "Pending: ['spec','c4','eval-plan']". The edit is blocked until those are `/approved`.
(Proven in the smoke test.)

## Anti-patterns
- ❌ Editing `src/` before the gates. ❌ Approving your own gate to unblock yourself (the human approves).
- ❌ Re-ordering steps to skip eval. ❌ Any bypass phrase.
