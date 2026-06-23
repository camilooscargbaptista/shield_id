---
id: wf-retrospect
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~650
description: The self-feeding loop. Always after merge/incident. 'What becomes what' map.
---

# retrospect (the retroalimentação engine)

> Run after every merged PR / incident / >2h debug / >30% rework. Owned by learning-curator. This is how
> the framework improves *structurally*, not just aspirationally.

## The 10 questions (abbrev.)
What went well? What was inefficient? What did we forget? What did we decide and why? What did we learn
about the domain? What pattern repeated? What almost shipped a defect? What guard would have caught it?
What's the kickoff→push time? What's coverage before→after?

## The "what becomes what" map (the core transform)
| Finding | Becomes |
|---------|---------|
| "We forgot to check X" / a defect slipped | an **executable guard** in `scripts/guards/` (→ pre-commit/CI). *A lesson that stays markdown is folklore.* |
| "We chose Y over Z" | an **ADR** + `.context/DECISION-LOG.md` entry |
| "The domain behaves like W" | `.context/knowledge/<domain>.md` update (same PR) |
| "Pattern repeated 3×" | a new **rule** or **template** |
| "A metric was inflated" | tighten `metric_honesty.py` (this is exactly how LC-001 → the cross-generator guard) |

## Rule: at least one finding per incident should become a GUARD, not just a rule.

## Worked example (the loop that compounds)
Incident: an eval reported 96% that was in-distribution. Retrospect → LC-001 → became
`metric_honesty.py --require-cross-generator` (executable, pre-push). The same error now cannot recur.

## Output
LESSON-xxx in `.context/LESSONS-LEARNED.md` with the "became" column filled + the artifacts created.

## Anti-patterns
- ❌ A lesson with no guard/rule/ADR attached. ❌ Skipping retrospect "to save time" (the loop is the moat).
