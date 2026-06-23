# US-<NNN> — <title>

**Epic:** <EPIC-ID> · **Workstream:** WS-<A|B|C|D> · **Estimate:** <S|M|L> · **Owner agent:** <agent-id>

## Story (Connextra)
Como <role>, quero <capability>, para <outcome>.

## Acceptance criteria — EVALUATION scenarios (rule 11, not UI BDD)
- **Held-out:** on unseen test split, <metric> ≥ <X> @ fixed FPR (curve reported).
- **Cross-generator (D8):** trained on {A,B}, tested on held-out C → robustness delta reported.
- **Parity:** no statistically significant disaggregated gap across segments.
- **Privacy:** automated test fails if any raw-biometric field is persisted.

## Tasks
| Task | Description | Owner agent | Est |
|------|-------------|-------------|-----|
| T-<NNN>-a | ... | detection-ml | ... |

## Definition of Done
- DELIVERY-GATE 10/10 · eval-independent verdict PASS · cross-generator present · no raw biometric/PII.

## must_haves (goal-backward, for eval-independent)
truths: [ ... ] · artifacts: [ paths ] · key_links: [ ... ]

## References
eval-plan: ... · datasheet: ... · model-card: ... · knowledge: .context/knowledge/<domain>.md
