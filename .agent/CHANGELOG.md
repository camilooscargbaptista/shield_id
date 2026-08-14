# .agent Framework Changelog

All notable changes to the SHIELD-ID agent framework. Semver per rule 28.
Major bumps require an ADR in `.context/DECISION-LOG.md`.

## [1.1.0] — 2026-07-21 (PORT-1.1 — hardening pós-auditoria credit_analyser)
### Fixed
- `.githooks/pre-push`: era **fail-open** — `git diff --cached` está vazio no momento do
  push (metric_honesty nunca escaneava nada) e `|| true` engolia falhas do guard. Agora
  lê o contrato stdin do pre-push (`local_sha remote_sha`), calcula o diff real do range
  enviado (incl. branch nova via `rev-list --not --remotes`) e QUALQUER falha bloqueia.
- `.githooks/pre-commit`: filenames com espaço quebravam o gate (`$FILES` sem aspas);
  agora hand-off NUL-separado e staging vazio é reportado explicitamente.
- `.claude/settings.json`: removido `matcher` inválido em `UserPromptSubmit` (matcher só
  se aplica a hooks de ferramenta; o filtro real já vive no próprio router script).
- `.claude/hooks/guard-bash-bypass.sh`: passou a bloquear tampering de `core.hooksPath`
  (unset ou redirecionamento para fora de `.githooks` desativaria todos os gates).
- `metric_honesty.py`: (a) escopo pedagógico — `.agent/` e `.context/` contêm thresholds
  de política e exemplos de ensino, nunca resultados medidos (SSOT/rule 15: resultados
  vivem em docs/reports + artefatos do verify_eval); escaneá-los gerava apenas falso
  positivo, o que ensina humanos a ignorar o gate. Fora dessas árvores o scan segue
  estrito (validado com fixture desonesta). (b) isenção por adjacência estendida a
  `example|illustrative|hypothetical|estimate` na mesma janela de 12 chars (LC-004).
  Linhas pedagógicas dos cards fairness-auditor/learning-curator/security-auditor e do
  RUN_ON_AWS anotadas com marcadores adjacentes.
### Added
- `framework_selfcheck.py` **classe F — framework hygiene**, codificando as classes de
  falha da auditoria do credit_analyser (2026-07-21) para que não possam recorrer:
  F1 entry points íntegros (AGENTS.md + symlinks CLAUDE/GEMINI + .cursorrules);
  F2 nenhum arquivo do framework fora do controle de versão (untracked ⇒ FAIL);
  F3 enforcement instalado de fato (hooksPath=.githooks, hooks executáveis, proibido
  padrão fail-open `|| true` em linha de guard); F4 zero referências fantasma nos docs
  núcleo (AGENTS.md, INDEX, CONSTITUTION, BOOTSTRAP).
### Known debt (bloqueado pela própria classe F até resolver)
- Repositório **sem remote** — CI framework-selfcheck.yml nunca executa; configurar
  origin e push é pré-requisito para o gate de CI existir de verdade.
- Arquivos do framework ainda untracked (selfcheck, workflow CI, agent_run.py,
  EPIC-FRAMEWORK-EVOLUTIONS) — commit pendente do humano.

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
