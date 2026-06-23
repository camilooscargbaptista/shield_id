# .agent Framework Changelog

All notable changes to the SHIELD-ID agent framework. Semver per rule 28.
Major bumps require an ADR in `.context/DECISION-LOG.md`.

## [1.0.0] — 2026-06-17
### Added
- Initial framework: bootstrap, SSOT, constitution (M1–M6 + 5 SHIELD-ID invariants).
- 9 agent cards (A2A schema) with the builder≠judge split (eval-independent isolated).
- 22 numbered rules (ML/Python-native), 7 guards, workflows, templates, 3 skills.
- Real enforcement: `.claude/hooks/` + `scripts/guards/` (no-raw-biometric, no-real-pii,
  metric-honesty, src-edit gate, index-drift) + active-experiment state machine.
- 5 Phase-2 epics (eval-harness, detection-api, redteam-dataset, aita-v1, pilot-pathway).
### Lineage
- Enforcement spine adapted from zeca_site/.agent ("Antigravity" v4); methodology
  (goal-backward, SPIDR, eval-driven, ai-spec) adapted from get-shit-done. All content
  rewritten for Python/ML; bound to decisions D1–D9.
