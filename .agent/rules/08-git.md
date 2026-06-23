---
id: rule-08-git
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-12-15
trigger: always_on
priority: HIGH
tokens: ~600
description: Git flow, micro-commits, tags, DoD=pushed. M6. With examples.
---

# 08 — Git (M6)

## The rules
1. **Branch per unit:** `feat/<slug>`, `exp/<slug>`, `fix/<slug>`. Never commit to a shared branch directly.
2. **Conventional Commits, scoped:** `feat(layer1): fine-tune document detector`, `fix(eval): seed the harness`.
3. **One atomic task = one compiling commit.** A commit must build/import; never commit a broken tree.
4. **Annotated semantic tag per green milestone** for rollback: `git tag -a v-eval-harness-m0 -m "..."`.
5. **DoD includes `pushed`** — verified by `git log origin/<branch>..HEAD` being empty.
6. **Never `--no-verify`** — it bypasses the gates (M6) and is blocked by `guard-bash-bypass.sh` (exit 2).

## Worked example
```
feat(eval): cross-generator harness skeleton        # T-001-b, compiles, tests green
feat(eval): robustness-delta metric                  # T-001-c
git tag -a v-eval-harness-m0 -m "harness + cross-generator protocol frozen"
git push && git push --tags
```

## Acceptance checklist
- [ ] On a feature branch. [ ] Conventional + scoped messages. [ ] Each commit compiles. [ ] Tag on green milestone. [ ] Pushed.

## Anti-patterns
- ❌ Commit to main/develop directly. ❌ `--no-verify`. ❌ A commit that doesn't build. ❌ "WIP" blobs.
