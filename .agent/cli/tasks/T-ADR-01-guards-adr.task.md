# T-ADR-01 — ADR das mudanças em guards CRÍTICOS + lições   (governança / rule 28)

**Leia primeiro:** `AGENTS.md` · `.agent/rules/28-rule-lifecycle.md` · `.agent/templates/adr.template.md` ·
`.agent/cli/CONTROL.md` (Log de 2026-06-22) · bundles `.agent/cli/evidence/T-FIX-02.md` e `T-FIX-03.md`
(pré-requisito: T-FIX-02 e T-FIX-03 concluídas) · `../../docs/06-governance/adr/README.md`

**Objetivo (1 frase):** quitar a dívida de rule 28 aberta desde 22/jun documentando TODAS as mudanças
de comportamento em guards críticos num ADR único, e registrar as lições no ciclo learning-curator.

**Faça:**
1. Crie `../../docs/06-governance/adr/ADR-0010-guard-hardening-and-falsepositive-scope.md` (template
   oficial) cobrindo, com contexto/decisão/consequências:
   a. 2026-06-22: `no_raw_biometric` passa a ignorar `.md` + própria pasta guards; `no_hardcoded`
      escopo restrito a `.py` de produção (motivo: falso positivo sistêmico ensina humano a ignorar gate).
   b. 2026-07-21 (PORT-1.1): isenção pedagógica `.agent/`/`.context/` no `metric_honesty` + adjacência
      de 12 chars (LC-004).
   c. Esta sprint: correção fail-open `no_raw_biometric` (T-FIX-03) + hardening `metric_honesty`
      (T-FIX-02: frações, 1 dígito, circularidade, threshold-sweep) — inclua o achado de que o fixture
      de defeito passava o gate determinístico.
   d. Risco residual documentado: a isenção pedagógica cobre `.agent/epics/*/state/` onde vivem
      certificações com números — decisão explícita (aceitar ou estreitar) fica marcada como
      QUESTION para o lead no próprio ADR.
2. Atualize `../../docs/06-governance/adr/README.md` (índice) com a ADR-0010.
3. Registre lições em `.context/LESSONS-LEARNED.md` no formato LC existente: LC-005 (vazamento de
   controle: "split disjunto é propriedade construída, não assumida") e LC-006 ("guard sem prova
   bidirecional automatizada é folclore — o defeito plantado passou 22 dias verde").
4. Atualize `.context/METRICS.md` (contagens reais: 8 guards py, 6 epics — hoje diz 7/5).

**Restrições (rules aplicáveis):** 20 · 28 · 29
**Saída (artefato + caminho):** ADR-0010 + índice ADR + LESSONS-LEARNED (LC-005/LC-006) + METRICS.md
**Done quando (verificável + evidência colada — M1):** ADR segue o template completo · índice
atualizado · LCs numeradas sem colisão · diff dos 4 arquivos no bundle.
**Anti-padrões (proibidos):** ADR genérico sem os 4 blocos de mudança · criar rule nova · tocar em
qualquer guard (esta task é só documentação).
**Atualizar:** CONTROL.md (T-ADR-01 `READY_FOR_ORACULO`, remover a pendência do Log de 22/jun) ·
bundle em `.agent/cli/evidence/T-ADR-01.md`.
