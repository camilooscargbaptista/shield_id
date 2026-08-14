---
id: agent-card-schema
version: 1.1.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: on_demand
priority: HIGH
tokens: ~1400
description: Schema for agent cards (inspired by Google A2A). Makes routing deterministic. With field reference, examples, lifecycle, and validation.
---

# Agent Card Schema (A2A-inspired)

Every file in `.agent/agents/` carries an `agent_card` YAML block. The orchestrator routes by reading
`capabilities / inputs / outputs / depends_on / role / can_write_code` — **deterministic routing, not
prose-reading.** This is adapted from Google's Agent-to-Agent (A2A) protocol: agents are typed services
with declared interfaces, not free-form personas.

## 1. Mandatory frontmatter
```yaml
agent_card:
  id: kebab-case-id            # unique; matches the filename
  name: HUMAN NAME
  role: coordination | builder | validation | audit | governance | policy
  kind: process | prompt-module # process = spawned as its OWN isolated session; prompt-module = a persona composed INTO a session, not independently spawned. ORTHOGONAL to can_write_code.
  can_write_code: true|false   # validators/auditors/coordination MUST be false (M5)
  capabilities: [ verb-noun ... ]   # what it can DO (used for routing match)
  inputs: [ artifact ... ]          # what it consumes (paths/types)
  outputs: [ artifact ... ]         # what it produces (with paths)
  depends_on: [ agent-id ... ]      # agents that MUST run before; [] if none
  model_hint: opus | sonnet | haiku # cost routing (session-start hook reads this)
```

## 2. Field reference (semantics)
| Field | Meaning | Routing use |
|-------|---------|-------------|
| `role` | the agent's class | decides whether it can be in a parallel read-only fan-out |
| `can_write_code` | may it edit `src/`? | **validators/auditors = false** — enforces M5 at the capability level |
| `capabilities` | matchable verbs | the orchestrator matches request keywords → capabilities |
| `depends_on` | ordering DAG | the orchestrator topologically orders BLOCKS from this |
| `model_hint` | cost tier | architectural/critical = opus; build = sonnet; admin = haiku |

## 3. Optional extensions
```yaml
  communication:
    receives_from: [ ... ]
    sends_to: [ ... ]
    artifact_path: .context/analysis/<AGENT>-ANALYSIS.md   # how it talks (NOT chat relay)
    blocker_protocol: writes .context/BLOCKER-<AGENT>.md
  blocks: [ all-agents ]        # protection agents only (privacy-ethics-review)
  delegates_to: [ ... ]         # orchestrator only
  verdict_schema: { ... }       # validation agents only (eval-independent, fairness-auditor)
  enforcement_status: { capability: "ATIVO via scripts/guards/<x>.py (sprint N)" }  # ties claim→mechanism
```

## 4. Body sections (after frontmatter)
`## Identity` · `## When to dispatch` · `## Inputs` · `## Process` (numbered, concrete) ·
`## Outputs` · `## Authority (what it can BLOCK)` · `## Restrictions` (esp. M5 for builders) ·
`## Anti-patterns` · `## Hand-off` (the completion marker it returns).

## 5. The builder ↔ validator firewall (the schema's reason to exist)
The single most important property the schema enforces: **`can_write_code: false` on every validation/
audit role.** This makes M5 (who builds does not validate) a *capability-level* fact, not a request the
agent might forget. A validator literally has no tool to edit the thing it judges.

**`kind` is ORTHOGONAL to `can_write_code`.** `kind: process` means the agent is spawned as its **own
isolated session** (the independent evaluator, `eval-independent`, is the only `process` today — its
isolation is *the* reason its numbers are credible, D4/M5). `kind: prompt-module` means the agent is a
persona **composed into** an existing session (the orchestrator and the 7 other roles), never spawned
independently. A `process` may still be `can_write_code: false` — `eval-independent` is `process` AND
read-only. The taxonomy is enforced by `scripts/guards/framework_selfcheck.py` (every card must declare
one of the two).

| Builders (can_write_code: true) | Validators/auditors (false) |
|----|----|
| detection-ml, data-redteam, aita-policy | eval-independent, fairness-auditor, security-auditor, privacy-ethics-review, learning-curator, orchestrator |

## 6. Routing table (the orchestrator's deterministic dispatch — SSOT for routing)
| Request contains | Agents dispatched | Order |
|------------------|-------------------|-------|
| `detection / layer1 / layer2 / model` | detection-ml → eval-independent → fairness-auditor | sequential |
| `dataset / red-team / synthetic` | data-redteam → eval-independent | sequential |
| `eval / metric / benchmark` | eval-independent + fairness-auditor | parallel (read-only) |
| `api / endpoint / fastapi` | detection-ml → security-auditor → eval-independent | sequential |
| `aita / policy` | aita-policy | single |
| biometric/PII-touching code | privacy-ethics-review (gate) | gate before merge |
| post-merge / incident | learning-curator | single |

## 7. Lifecycle (creating / changing an agent — rule 28)
1. Create file with `agent_card` frontmatter; set `can_write_code` honestly (M5).
2. Register in ORCHESTRATOR `delegates_to`. 3. Add to INDEX + this routing table.
4. Define `artifact_path`. 5. Confirm the orchestrator can route to it (a keyword maps to a capability).
6. `version`/`next_review` per rule 28; a role change (e.g. flipping `can_write_code`) is a **major** bump → ADR.

## 8. Validation (what `index_drift.py` + `framework_selfcheck.py` + review checks)
- Every `agents/*.md` is referenced in INDEX. - Every validator has `can_write_code: false`.
- Every card has `depends_on` (even if `[]`). - Every `delegates_to` target exists as a card.
- **Every card declares `kind: process | prompt-module`** (mandatory; `framework_selfcheck.py` §B).
- The invariant→guard map, single-reviewer path, DAG integrity and label honesty are all asserted
  fail-closed by `scripts/guards/framework_selfcheck.py` (pre-push + CI).

## 9. Anti-patterns
- ❌ A validator with `can_write_code: true` (breaks M5). ❌ An agent that spawns peers directly
  (only the orchestrator delegates; exception: a debug-session-manager pattern). ❌ Capabilities written
  as prose paragraphs instead of matchable `verb-noun` tokens. ❌ Inter-agent chat relay instead of
  `artifact_path`.
