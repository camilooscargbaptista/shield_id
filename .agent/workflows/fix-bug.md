---
id: wf-fix-bug
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: HIGH
tokens: ~400
description: Bug fix flow; RED test first; lesson → guard.
---

# fix-bug

## Steps
1. Diagnose → locate → **root cause** (not a symptom patch).
2. **Write a failing test that reproduces the bug (RED)** — before the fix.
3. Minimal fix (don't refactor neighbors, don't add features — M4). Make the RED test green.
4. Regression run (the prior suites). Verify existing flows.
5. DELIVERY-GATE. Document as **LESSON-xxx** in `.context/LESSONS-LEARNED.md`.
6. **Curator step:** decide whether the lesson should become an executable guard (retrospect). A recurring
   class of bug → a guard, not just a lesson.

## Worked example
Bug: eval silently used the wrong split. RED test asserting held-out C is loaded → fix → green → LESSON +
consider a guard that asserts the splits-manifest matches the run config.

## Anti-patterns
- ❌ Fixing without a reproducing test. ❌ Refactoring neighbors "while here". ❌ A recurring bug with no guard.
