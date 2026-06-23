---
id: rule-29-glossary-discipline
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: HIGH
tokens: ~450
description: Ubiquitous language. New term → GLOSSARY or PR rejected.
---

# 29 — Glossary Discipline

Every domain term → `.context/GLOSSARY.md` (canonical form, definition, EN/PT, state flow if any,
non-confusables). **One term per code object — no synonyms.** A PR that introduces a term without a glossary
entry is rejected; learning-curator audits orphans monthly.

## Why
Synonym drift ("trust score" vs "confidence score" vs "risk score" for the same thing) silently fractures
the codebase and the policy docs. Ubiquitous language keeps code, eval, and AITA writing aligned.

## Worked example
The Layer-2 output is `trust_score` — **always**. Not "confidence" in one module and "risk" in another.
The glossary fixes the canonical term; code, logs, and docs use it verbatim.

## Acceptance checklist
- [ ] Every new domain term has a glossary entry. [ ] One canonical term per concept. [ ] No orphans.

## Anti-patterns
- ❌ Two names for one concept. ❌ A term in code that isn't in the glossary.
