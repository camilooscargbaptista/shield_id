# .agent — SHIELD-ID Agent Governance Framework

A filesystem-native, self-feeding (retroalimentado) multi-agent governance system for an
ML/Python research product. Policy here; enforcement in `scripts/` + `.claude/hooks/`;
state in `state/`; product memory in `.context/`.

**Design principles** (lifted from zeca_site/.agent maturity + get-shit-done methodology,
rewritten for ML):

- **Reliability is architecture** — deterministic guards (exit 0/1/2), not adjectives.
- **Builder ≠ judge** (D4/M5) — independent evaluator in an isolated session.
- **Small, injectable, sub-modular** — numbered rules, single-purpose guard scripts, SKILL.md
  progressive disclosure, agent cards routed by `depends_on`.
- **Self-feeding loop** — `/retrospect` → lesson → executable guard → CI → never recurs.
- **Single source of truth** — each topic one owner; everyone else links.
- **Context economy** — BOOTSTRAP routes you to only what your task needs.

Start at `../AGENTS.md`. Navigate with `INDEX.md`. Governing law: `CONSTITUTION.md`.
