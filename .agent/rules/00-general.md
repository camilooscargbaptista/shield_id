---
id: rule-00-general
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~900
description: The golden rules + the read-order + the decision tree. Always-on core.
---

# 00 — General (Golden Rules)

> The always-on core. If you read nothing else, read this and the CONSTITUTION.

## The 9 golden rules
1. **Read before write.** Load the BOOTSTRAP route for your task; read the owning files (SSOT). Reuse,
   never recreate — search existing code/patterns first.
2. **Evidence or silence (M1).** No claim ("works", "passes", "95%") without pasted, tool-verified
   evidence produced this session.
3. **Unknown → STOP (M2).** Never guess in a financial-security/ML system. "I don't know" is valid and required.
4. **Zero-skip (M3).** A phase starts only when the prior is complete + green. Gates before `src/` edits.
5. **Scope is law (M4).** Touch only in-scope files. Out-of-scope → blocker/tech-debt, never silent expansion.
6. **Builder ≠ judge (M5/D4).** You never validate your own metrics — `eval-independent` does, isolated.
7. **The 5 invariants** (CONSTITUTION): no raw biometrics · no real PII · no metric without reproducible
   artifact · cross-generator mandatory · metrics are targets (report what you measure).
8. **Micro-commits + push (M6).** One atomic task = one commit; DoD includes `pushed`.
9. **Quality > velocity** in a security/ML system. The "faster, skip-the-eval" path is forbidden — refuse it.

## The decision tree (what to do when a request arrives)
```
Is it trivial (1-5 lines)? ── yes ─► CHEATSHEET-COMPACT, do it, done.
        │ no
Is it ambiguous / am I assuming something I don't know? ── yes ─► STOP, ask (M2).
        │ no
Does it touch a model/metric/dataset/biometric? ── yes ─► route via ORCHESTRATOR (P0→P5), gates apply.
        │ no
Is it a bug fix? ── yes ─► workflows/fix-bug (RED test first).
        │ no
Default ─► workflows/new-experiment.
```

## Worked example (the reuse rule)
Asked to "add a metric". ❌ Writing a new metrics module. ✅ Grep `src/shield_id/eval/` first — the harness
already computes P/R@FPR; extend it, don't fork it.

## Anti-patterns (forbidden)
- ❌ Coding before reading the route. ❌ A claim without evidence. ❌ Guessing past an unknown.
- ❌ "While I'm here" scope creep. ❌ Self-reporting a metric. ❌ The "skip the gate to go faster" path.
