---
id: index
version: 1.0.0
last_updated: 2026-06-17
next_review: 2026-08-16
trigger: on_demand
priority: HIGH
tokens: ~700
description: Canonical navigation map of the SHIELD-ID .agent framework. Read after AGENTS.md.
---

# .agent INDEX — Navigation Map

> Adding/removing a file under `rules/ agents/ guards/ workflows/` **requires** updating this
> INDEX and `SINGLE-SOURCE-OF-TRUTH.md`. Enforced by `scripts/guards/index_drift.py` (pre-push).

## Read order for a fresh session
`AGENTS.md → CONSTITUTION.md → SINGLE-SOURCE-OF-TRUTH.md → BOOTSTRAP.md (route by task) → rules/00 → guards/DELIVERY-GATE.md`

## Core docs (`.agent/`)
| File | When to read |
|------|--------------|
| `CONSTITUTION.md` | Always. The 6 mandates + 5 hard invariants. |
| `SINGLE-SOURCE-OF-TRUTH.md` | Before writing any doc — find the one owner of a topic. |
| `BOOTSTRAP.md` | Start of every task — load only what your task type needs. |
| `AGENT-CARD-SCHEMA.md` | Before creating/editing an agent. |
| `CHEATSHEET-COMPACT.md` | Trivial 1–5 line tasks fast path (~400 tokens). |
| `CHANGELOG.md` | Framework evolution history. |

## Agents (`.agent/agents/`) — A2A cards, routed by `depends_on`
ORCHESTRATOR · detection-ml · data-redteam · eval-independent · fairness-auditor ·
aita-policy · privacy-ethics-review · security-auditor · learning-curator

## Rules (`.agent/rules/`) — numbered, injectable
00-general · 01-python-fastapi · 02-ml-experiments · 03-data-governance · 04-privacy-biometrics ·
05-evaluation · 06-fairness · 07-reproducibility · 08-git · 09-agent-spec · 10-c4-architecture ·
11-eval-scenarios · 12-mlops · 13-security · 14-story-decomposition · 15-no-self-reported-metrics ·
16-observability · 20-documentation · 28-rule-lifecycle · 29-glossary-discipline · 32-no-hardcoded-defaults · 34-constitution-link

## Guards (`.agent/guards/`) — documented gates (execution lives in scripts/)
DELIVERY-GATE · EVAL-GATE · FAIRNESS-GATE · PRIVACY-GATE · WORKFLOW-ENFORCEMENT · PREFLIGHT · CODE-REVIEW-CHECKLIST

## Workflows (`.agent/workflows/`)
MANDATORY-CHECKLIST · new-experiment · plan-phase · execute-phase · run-eval · generate-redteam ·
draft-aita · verify · review · pre-mortem · retrospect · fix-bug

## Templates (`.agent/templates/`)
model-card · ai-spec · eval-plan · datasheet · adr · threat-model · user-story · epic · task · c4-diagram

## Skills (`.agent/skills/`) — SKILL.md progressive disclosure
generate-redteam-batch · run-eval-and-report · audit-demographic-parity

## Epics (`.agent/epics/`)
EPIC-STATUS.md (portfolio index) → EPIC-EVAL-HARNESS · EPIC-DETECTION-API · EPIC-REDTEAM-DATASET · EPIC-AITA-V1 · EPIC-PILOT-PATHWAY

## State (`.agent/state/`)
current-experiment.json (git-ignored, ephemeral) · approval-log.jsonl (checked-in, append-only) · archived/

## Memory (`.context/`)
ARCHITECTURE.md (C4) · DECISION-LOG.md (D1–D9) · GLOSSARY.md · LESSONS-LEARNED.md · METRICS.md · knowledge/{layer1-detection,layer2-behavioral,aita-policy,fairness}.md

## CLI orchestration (`.agent/cli/` + `.claude/commands/`)
Camada de prompts pro Claude Code CLI: `cli/CONTROL.md` (doc vivo) · `cli/tasks/*.task.md` (prompts-filhos) ·
`.claude/commands/{orchestrate,next,status}.md` (slash commands). Uso: `cli/README.md`. Loop: `/orchestrate`.
