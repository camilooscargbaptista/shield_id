---
id: skill-subagent-pattern
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
description: When/how to decompose into specialized subagents. The basis of orchestration.
---
# Subagent Pattern
Decompose when work is independent (parallelize), needs isolation (the independent evaluator — M5), or
exceeds one context budget. Invocation template: Context · Task · Constraints · Expected-Output · Files ·
Do-Not. Orchestration: sequential (depends_on) or parallel (read-only agents). Fallbacks:
RETRY → FALLBACK → ESCALATE → PARTIAL → ABORT. The orchestrator stays low-context and delegates.
