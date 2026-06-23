# SHIELD-ID — Agent Entry Point (Single Physical Entry)

> **You are an AI coding/research agent working on SHIELD-ID.** This file is the
> ONE physical entry point. `CLAUDE.md` and `GEMINI.md` are symlinks to this file.
> Read this fully, then follow the mandatory reading order below **before any action**.

**Project:** SHIELD-ID — Detecting Synthetic Identities in Financial Systems through
Behavioral AI and Multilateral Policy. Stack: **Python-pure (FastAPI + ML)** (decision D1).
Phase: **Global Trust Challenge 2026 — Phase 2 (Prototyping).**

---

## 0. MANDATORY READING ORDER (do not skip — rule 03 zero-skip)

1. `.agent/INDEX.md` — the navigation map (what exists, when to read it).
2. `.agent/CONSTITUTION.md` — the 6 mandates + the SHIELD-ID hard invariants. **Binding.**
3. `.agent/SINGLE-SOURCE-OF-TRUTH.md` — who owns which topic (never duplicate).
4. `.agent/BOOTSTRAP.md` — the token-economy router: given your task, read ONLY what it lists.
5. `.agent/rules/00-general.md` — the golden rules.
6. `.agent/guards/DELIVERY-GATE.md` — the Definition of Done.

> If you arrived here and have NOT read `.agent/INDEX.md`, STOP and read it now.

---

## 1. The five non-negotiable SHIELD-ID invariants (full text in CONSTITUTION.md)

1. **Never persist raw biometrics.** Derived feature vectors only. (rule 04)
2. **No real personal data** in any dataset. Synthetic-only. (rule 03)
3. **No self-reported metric** is accepted without a reproducible artifact (notebook + seed + data). (rule 07, D4/D5)
4. **Cross-generator evaluation is mandatory** — no headline accuracy from in-distribution-only tests. (rule 05, D8)
5. **Metrics are targets to test, not promises.** Report measured outcomes with methodology, whatever they are. (D5)

These are enforced by hooks (`.claude/hooks/`, `scripts/guards/`), not just documented.

---

## 2. How work flows (full model in INDEX.md → epics)

`Idea → Epic → User Story (US) → Task → atomic commit`, gated end to end.
Builders build; an **independent evaluator validates in an isolated session** (decision D4).
Nobody marks their own homework.

## 3. Multi-runtime

`CLAUDE.md`, `GEMINI.md` → symlinks to this file. `.cursorrules` is a condensed mirror.
All clients funnel to `.agent/` as the single source of truth.

## 4. Authority

If a live instruction from Camilo conflicts with these files, **Camilo wins** — but flag the
conflict so the file is updated (rule 28 lifecycle). Decisions D1–D9 are recorded in
`.context/DECISION-LOG.md` and are binding unless overridden in-session.
