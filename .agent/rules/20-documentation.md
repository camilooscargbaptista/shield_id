---
id: rule-20-documentation
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: on_demand
priority: MEDIUM
tokens: ~450
description: docs/ structure + status frontmatter; cards/datasheets mandatory.
---

# 20 — Documentation

## The rules
1. Feature docs in `docs/features/<feature>/` with YAML status frontmatter (`status, owner, last_updated`).
2. **Document the WHY, not the what.** The code says what; the doc says why this trade-off.
3. **Every public artifact ships its card:** model → model-card, dataset → datasheet, API → threat-model + OpenAPI.
4. AITA writing follows templates/adr + the glossary (rule 29). Decisions → DECISION-LOG (D-series / ADR).

## Acceptance checklist
- [ ] Feature doc with status frontmatter. [ ] Model-card / datasheet present for shipped artifacts.
- [ ] WHY documented, not just what. [ ] Glossary terms linked (rule 29).

## Anti-patterns
- ❌ A shipped model without a card. ❌ Docs that restate the code. ❌ A new term with no glossary entry.
