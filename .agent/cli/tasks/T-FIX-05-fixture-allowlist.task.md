# T-FIX-05 — Allowlist estreita de `tests/fixtures/` no pre-push   (governança / EPIC-FRAMEWORK-EVOLUTIONS)

**Leia primeiro:** `AGENTS.md` · `.agent/CONSTITUTION.md` · `.githooks/pre-push` ·
`.agent/cli/evidence/T-FIX-02.md` (a interação fixtures × pre-push) · `../../docs/06-governance/adr/ADR-0010-guard-hardening-and-falsepositive-scope.md`

**Objetivo (1 frase):** impedir que os fixtures de guard desonestos-por-design (`tests/fixtures/**`)
bloqueiem um `git push` legítimo, sem alargar nenhuma isenção de guard.

**Contexto (autorizado pelo lead, 2026-08-13):** os fixtures de defeito do `metric_honesty`
(`tests/fixtures/guards/mh_*_defect.md`) têm conteúdo desonesto POR DESIGN — o gate pre-push
(`metric_honesty` sobre `.md`/`.json` do push) os flagra e bloqueia o push. O lead SUSPENDEU a
condição de STOP de tocar `.githooks/` EXCLUSIVAMENTE para esta task, com escopo estrito abaixo.

**Faça:**
1. No `.githooks/pre-push`, ao montar a lista `MD`, EXCLUIR apenas caminhos com prefixo
   `tests/fixtures/` (allowlist estreita, comentada, citando ADR-0010 + o aprovado do lead).
2. Nada mais: precedente de exclusão-narrow já existe (`no_raw_biometric` exclui a própria pasta
   `scripts/guards/`; `framework_selfcheck` exclui os próprios fixtures).

**Restrições (rules aplicáveis):** 13 · 28 (o pre-push é infra de guard; mudança documentada em ADR-0010)
**Saída (artefato + caminho):** `.githooks/pre-push` (só o bloco de montagem da lista MD)
**Done quando (verificável + evidência colada — M1):** prova bidirecional no bundle: (a) simulação
do gate contra o range `d9d0130..HEAD` → **exit 0**; (b) um `.md` desonesto plantado FORA de
`tests/fixtures/` no range simulado → **exit 1** (depois remover o plantado). Suíte pytest completa verde.
**Anti-padrões (proibidos):** alargar `PEDAGOGICAL_PREFIXES` · tocar `metric_honesty.py` ou QUALQUER
outro guard/hook · exclusão ampla (só `tests/fixtures/`, nada além) · `--no-verify`.
**Atualizar:** CONTROL.md (status `READY_FOR_ORACULO` + Log) · bundle em `.agent/cli/evidence/T-FIX-05.md`.
