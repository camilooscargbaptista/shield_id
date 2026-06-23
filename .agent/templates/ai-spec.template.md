# AI-SPEC — <AI feature>

## System type
<detector | behavioral GNN | ensemble>

## Failure modes (enumerate)
- ...

## Eval dimensions (by type)
detection: recall@FPR, cross-generator robustness, calibration · behavioral: cold-start, drift.

## Reference dataset (>= N examples)
<datasheet ref>

## Guardrails (must be in the request path, not stubbed)
- input validation · no-raw-biometric enforcement · contestation/human-review escalation.

## Online vs offline
online guardrails: ... · offline flywheel: red-team retraining cadence (rule 12).
