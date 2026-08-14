# EPIC-FRAMEWORK-EVOLUTIONS — Hardening the `.agent/` Framework

**Status:** em-andamento · **Workstream:** WS-B (infra) · **Owner:** Camilo · **Version:** 1.1.0
**Branch:** `exp/port-framework-evolutions` · **Type:** experiment (closest step-set; a tooling epic is a known misfit — no dedicated step-set added for a one-off, per lead)

## What it is
Port the 3 zeca-V5 framework evolutions SHIELD-ID lacks, **in Python** (D1), adapted to shield's
ML/privacy domain, each **proven before the next**. Where the per-invariant guards
(`no_raw_biometric`, `no_real_pii`, `metric_honesty`) protect the **product**, this epic protects
the **framework**: it makes the invariant→guard wiring, the agent-card roster, the single-reviewer
rule and the DAG themselves fail-closed and auditable, and it automates the M5 reviewer.

## The 3 ports (approved scope)
- **PORT-1 — `scripts/guards/framework_selfcheck.py` meta-guard.** Fail-closed selfcheck (exit != 0
  on ANY drift) asserting: (A) each invariant I1–I5 maps to a guard that EXISTS and PASSES on a
  scoped clean run; (B) card coherence — roster parity across files/INDEX/schema, mandatory
  frontmatter incl. the new `kind: process | prompt-module` field, and M5 read-only roles; (C)
  exactly ONE independent-reviewer entrypoint (`scripts/agent/verify_eval.py`); (D) DAG integrity of
  `depends_on` / `delegates_to`; (E) label honesty of `enforcement_status` ATIVO/Completo claims.
  Wired into `.githooks/pre-push` + CI (`.github/workflows/framework-selfcheck.yml`). **DONE.**
- **PORT-2 — UPGRADE `scripts/agent/verify_eval.py` IN PLACE** (not a new file — one reviewer, one
  path; a parallel reviewer would trip PORT-1 assertion C). Turn today's deterministic stub into the
  real **isolated `claude -p` M5 reviewer**: seeded with the `eval-independent.md` card + the shield
  **ML kill-list** + a reinjected playbook; emits a **typed, fail-closed verdict JSON** (invalid =
  error, never "interpreted"); writes the verdict to `current-experiment.json`; and upgrades
  `approve.py` to **REFUSE** a gate without a PASS verdict. Reuses `metric_honesty.py` for kill-list
  #4. Neutral adjudicator that CAN say PASS (adversarial-only saturates); anchors name the ACTUAL
  defect; pre-register the bar; false-alarm sanity check.
- **PORT-3 — `scripts/agent/agent_run.py` + trace.** Generic single-role runner generalizing PORT-2:
  spawn a role **isolated**, validate output vs a **typed JSON Schema** (TYPE+ENUM, fail-closed,
  invalid = distinct error slot), write a flat artifact + **`trace.jsonl`** with real `cost_usd` /
  `duration_ms`.

### Shield ML kill-list (PORT-2)
(1) circularity — train/threshold-tune on the held-out generator (I4/rule 05); (2) train/test
leakage; (3) threshold tuned on the test set; (4) metric without cross-generator + reproducible
artifact (reuse `metric_honesty`); (5) raw-biometric persistence (I1); (6) real PII (I2); (7) metric
as promise not target (I5).

## F2 — NOT ported (rationale)
**F2 = the multi-agent DAG / scheduler** (decompose a task across multiple agents with a dependency
graph). Deliberately NOT ported: it was an evidence-based STOP in zeca — an A/B probe showed
decomposition adds analysis **depth** but **not catch-rate**, at ~1.6× cost. The same prior applies
here → keep SHIELD-ID's **single-orchestrator** flow. Out of scope by design, not omission.

## Build order & proof-per-port (Definition of Done)
`PORT-1 → PORT-2 → PORT-3`, each proven before the next. Each ships:
- **PORT-1:** born-**RED** (run against current state before fixes) → fixes → **GREEN** + CI-wired,
  plus an adversarial bite test. ✅ done.
- **PORT-2:** **bidirectional** proof — PASS a clean case AND FAIL a planted-defect case (e.g. a diff
  that trains/tunes on the held-out generator). Not a rubber-stamp.
- **PORT-3:** one real isolated run, paste the `trace.jsonl`.
No self-reported "it works" (M1) — paste real command output with exit codes. **No merge — human gate.**

## Anti-patterns (forbidden)
- ❌ A selfcheck that passes vacuously (asserting nothing that can go red).
- ❌ A **second** independent-reviewer entrypoint (breaks the one-reviewer rule — PORT-1 assertion C).
  PORT-2 upgrades `verify_eval.py` in place for exactly this reason.
- ❌ Porting F2 (the multi-agent DAG/scheduler) — evidence-based STOP.
