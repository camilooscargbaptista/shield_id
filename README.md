# SHIELD-ID

Detecting Synthetic Identities in Financial Systems through Behavioral AI and
Multilateral Policy. Global Trust Challenge 2026 — Phase 2 (Prototyping).

**Stack:** Python-pure (FastAPI + ML). **Team:** SHIELD-ID Initiative (Camilo Oscar
Girardelli Baptista, IEEE Senior Member). **Classification:** CONFIDENTIAL.

## Working in this repo

This project is governed by an agent framework under `.agent/`. **Any AI agent must read
`AGENTS.md` first.** Governance (policy) lives in `.agent/`; enforcement (hooks that block)
lives in `.claude/hooks/` + `scripts/`; product memory lives in `.context/`.

| Layer | Path | Role |
|-------|------|------|
| Policy | `.agent/` | rules, agents, guards, workflows, templates, epics (markdown) |
| Enforcement | `.claude/hooks/`, `scripts/` | deterministic forcing functions (exit 0/1/2) |
| State | `.agent/state/` | active-experiment machine + append-only approval log |
| Memory | `.context/` | architecture (C4), decisions, glossary, lessons, metrics |

## Quick start (governance)

```bash
python scripts/agent/start_experiment.py <slug> --type <experiment|api|dataset|policy>
python scripts/agent/approve.py <step>          # human gate
python scripts/agent/status.py                  # where are we
```
