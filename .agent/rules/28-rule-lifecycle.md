---
id: rule-28-rule-lifecycle
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~800
description: Rules expire: semver + next_review + ADR for major. Anti-bitrot. SSOT owner.
---

# 28 — Rule Lifecycle (SSOT owner: lifecycle / anti-bitrot)

> **Rules expire.** A framework that never prunes becomes an "old bible" nobody trusts. Every file under
> `rules/ agents/ guards/ workflows/ templates/` carries frontmatter: `version` (semver) · `last_updated`
> · `next_review`.

## Review cadence
| Class | Cadence |
|-------|---------|
| rules / agents / guards | 90 days |
| workflows / templates / skills | 180 days |
| INDEX / SSOT / CHEATSHEET / CONSTITUTION | 60 days |

## Process (learning-curator, monthly)
`grep "next_review:" .agent -r | filter expired` → for each, the owner re-evaluates (still valid? needs a
diff? deprecate?) → bump semver.

## Semver policy
- **patch** — typo / clarification.
- **minor** — add an example / check / section (backward-compatible).
- **major** — change a requirement (e.g. 80%→90% coverage), remove, invert, or rewrite. **Every major bump
  requires an ADR** in `.context/DECISION-LOG.md`.

## Deprecation
Mark `status: deprecated`, add a top pointer to the successor, **keep 6 months as a redirect, never delete
early.** (Consumers may still link to it.)

## Worked example
This very file was deepened from v1.0.0 → v2.0.0 (a content rewrite). Because that is a major-class change
to a CRITICAL rule, it is recorded as ADR-candidate in DECISION-LOG.

## Blocks merge
- Rule without `next_review`. - "updated" without a version bump (history-cheating).
- Major bump without an ADR. - >30 days past review with no action → escalate to Camilo.

## Anti-patterns
- ❌ Editing a rule and leaving the version. ❌ Deleting a deprecated rule immediately. ❌ Major change, no ADR.
