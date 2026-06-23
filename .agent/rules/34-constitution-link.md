---
id: rule-34-constitution-link
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~250
description: Pointer to CONSTITUTION (do not duplicate).
---

# 34 — Constitution (link only — SSOT is ../CONSTITUTION.md)

The 6 mandates (M1–M6) and the 5 SHIELD-ID hard invariants (I1–I5) live in `../CONSTITUTION.md`. This rule
exists only so the numbered-rules index references them. **Do not duplicate the text here** (SSOT, rule
29/SSOT map). Each mandate/invariant maps to an executable guard — *a mandate without a guard is folklore.*

To change a mandate/invariant: edit CONSTITUTION.md, bump its semver (major → ADR, rule 28), and ensure the
corresponding guard exists or is updated.
