---
id: rule-32-no-hardcoded-defaults
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~700
description: Zero silent defaults in detection/eval/threshold logic. Executable. Exception protocol.
---

# 32 — No Hardcoded Defaults

> Zero silent defaults in detection/eval/threshold logic. Enforced by `scripts/guards/no_hardcoded.py`.

## The rules
1. **Banned:** `or <default>` / `default=` / `??`-style silent defaults for thresholds, FPR targets,
   model paths, decision cutoffs in business/detection logic.
2. **Banned:** magic numbers outside enums/validators/config (a detection threshold literal in code).
3. **Detection cutoffs, FPR targets, parity thresholds: config-driven** (rule 02), validated at startup.

## Why it is CRITICAL (a real failure mode)
A silent `threshold = score or 0.5` or `fpr_target = cfg.get("fpr", 0.001)` hides the most important
decision of a fraud system in a default nobody reviewed. In a financial-security system, an unreviewed
default cutoff is a direct path to either mass false-positives (harming the protected population — rule 06)
or missed fraud.

## Exception protocol (3 artifacts — non-retroactive)
A sanctioned legacy exception needs ALL of:
1. Justification in the experiment's `01-context`.
2. An append to `.agent/state/no-hardcoded-exceptions.jsonl` (the append-only whitelist).
3. A compensating tech-debt item in the backlog.

## Worked example
❌ `threshold = cfg.threshold or 0.5`. ✅ `threshold = cfg.detection.threshold` (validated at startup; no
silent fallback — if missing, fail loudly).

## Anti-patterns
- ❌ Any silent default in a cutoff. ❌ A magic threshold literal. ❌ An exception without the 3 artifacts.
