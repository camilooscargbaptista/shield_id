# SHIELD-ID — Auditoria e Hardening do Framework de Agentes (PORT-1.1)

**Data:** 21/07/2026
**Contexto:** aplicação, no shield_id, das classes de falha encontradas na auditoria do
`.agent/` do credit_analyser — com correção dos problemas encontrados aqui e criação de
enforcement para que **não possam recorrer**. Nenhum commit foi feito (por instrução);
todas as mudanças estão no working tree.

---

## 1. Resultado da auditoria do shield_id

A base é sólida (entry points, versionamento, hooks, guards, state) — mas a auditoria
encontrou 7 problemas reais:

| # | Sev. | Achado | Estado |
|---|---|---|---|
| 1 | ALTO | **`.githooks/pre-push` era fail-open**: `git diff --cached` está vazio no momento do push (metric_honesty nunca escaneava nada) e `[ -n "$MD" ] && guard … \|\| true` engolia falhas do guard. O gate "fail-closed" nunca bloqueou nada. | **CORRIGIDO** |
| 2 | ALTO | **Meta-guard e CI não versionados**: `scripts/guards/framework_selfcheck.py`, `.github/workflows/framework-selfcheck.yml`, `scripts/agent/agent_run.py` e `EPIC-FRAMEWORK-EVOLUTIONS/` untracked — o EPIC-STATUS afirmava "wired pre-push+CI" sem lastro (a própria classe E "label honesty" do selfcheck, violada pelo repo). | **DETECTADO pelo novo F2 — commit pendente (humano)** |
| 3 | ALTO | **Repo sem remote git** — todo o framework, código e approval-log existem numa única máquina; o workflow de CI nunca rodou nem pode rodar. | **DETECTADO pelo novo F2 — remote pendente (humano)** |
| 4 | MÉDIO | **`pre-commit` frágil**: `$FILES` sem aspas quebrava com filenames contendo espaço; staging vazio passava silenciosamente. | **CORRIGIDO** |
| 5 | MÉDIO | **`.claude/settings.json`** com `matcher` em `UserPromptSubmit` — campo não suportado nesse evento (só em hooks de ferramenta); config mentia sobre o comportamento (o filtro real já vive no router script). | **CORRIGIDO** |
| 6 | MÉDIO | **`guard-bash-bypass.sh` não cobria tampering de `core.hooksPath`** — `git config --unset core.hooksPath` ou `git -c core.hooksPath=/dev/null …` desativaria todos os gates sem ser bloqueado. | **CORRIGIDO** |
| 7 | MÉDIO | **`metric_honesty` gerava só falso positivo no framework**: ao consertar o pre-push (achado 1), o primeiro scan real flagrou 14 arquivos — todos thresholds de política (`rules/28`, exemplo: "80%→90% coverage") e exemplos de ensino (fairness: "FPR 0.09%…"), nunca resultados medidos. Falso positivo sistêmico ensina humanos a ignorar o gate. | **CORRIGIDO (escopo pedagógico)** |

Achado menor: `trace.jsonl` contém entradas de teste com caminhos `/tmp` (poluição do
log do PORT-3); já está gitignored — sem ação.

---

## 2. Correções aplicadas (arquivo a arquivo)

### `.githooks/pre-push` — reescrito, fail-closed de verdade
Lê o contrato stdin do pre-push (`local_ref local_sha remote_ref remote_sha`), calcula o
diff real do range enviado — incluindo branch nova via `rev-list --not --remotes` e
`diff-tree --root` (commit-raiz) —, roda `metric_honesty --require-cross-generator` nos
md/json do push com hand-off NUL-safe, e **qualquer falha bloqueia** (zero `|| true`).
Depois: `index_drift` + `framework_selfcheck`.

### `.githooks/pre-commit` — reescrito, robusto
Arquivos staged coletados com `-z` (NUL-separado — filenames com espaço/acento não
quebram mais); staging vazio reportado explicitamente; `set -euo pipefail`.

### `.claude/settings.json`
Removido o `matcher` inválido de `UserPromptSubmit` (o router filtra internamente
`/approved|/status` — comportamento inalterado, config agora verdadeira).

### `.claude/hooks/guard-bash-bypass.sh`
Novo bloqueio: qualquer uso de `core.hooksPath` que não seja exatamente a instalação
canônica (`git config core.hooksPath .githooks`) → exit 2. Cobre `--unset` e
`git -c core.hooksPath=…`.

### `scripts/guards/metric_honesty.py`
1. **Escopo pedagógico**: `.agent/` e `.context/` são política/ensino — por SSOT/rule 15,
   resultados medidos vivem em docs/reports + artefatos do `verify_eval.py`. Fora dessas
   árvores o scan segue estrito (validado: relatório desonesto sintético continua
   bloqueando com exit 1).
2. **Isenção por adjacência estendida**: além de `target|aspirational`, aceita
   `example|illustrative|hypothetical|estimate` — mesma janela apertada de 12 chars do
   hardening LC-004 (um resultado real não se "lava" com palavra distante).
3. Linhas pedagógicas de 4 arquivos anotadas com marcadores adjacentes
   (fairness-auditor, learning-curator ×2, security-auditor, RUN_ON_AWS).

### `scripts/guards/framework_selfcheck.py` — **classe F: framework hygiene** (nova)
Codifica as classes de falha do credit_analyser para que não possam recorrer aqui:

- **F1 — entry points íntegros**: `AGENTS.md` existe; `CLAUDE.md` e `GEMINI.md` são
  symlinks apontando para ele; `.cursorrules` existe. (Anti "framework inerte".)
- **F2 — tudo versionado**: nenhum arquivo do framework (`.agent/`, `.claude/`,
  `.githooks/`, `scripts/guards|agent|lib`, entry points, workflow de CI) pode estar
  untracked; e **um remote git deve existir** (fora de CI). (Anti "existe só nesta máquina".)
- **F3 — enforcement instalado**: `core.hooksPath = .githooks` (fora de CI), hooks
  executáveis (`.githooks/` e `.claude/hooks/`), e **proibido padrão fail-open** — linha
  de guard terminando em `|| true` dentro dos git hooks é FAIL. (Anti "regra sem dente";
  teria pegado o achado 1 automaticamente.)
- **F4 — zero referências fantasma**: todo caminho citado em `AGENTS.md`, `INDEX.md`,
  `CONSTITUTION.md` e `BOOTSTRAP.md` deve existir. (Anti "documentação que mente".)

Roda no pre-push e no CI (F2-remote e F3-hooksPath são pulados quando `CI` está setado,
onde não fazem sentido).

### Documentação
- `.agent/CHANGELOG.md` → entrada **[1.1.0]** com tudo acima + dívida conhecida.
- `.agent/epics/EPIC-STATUS.md` → PORT-1.1 registrado; nota antiga "wired pre-push+CI"
  substituída por status honesto (pendências humanas explícitas).
- `.githooks/INSTALL.txt` → agora inclui o passo de verificação via selfcheck.

---

## 3. Evidência de verificação (tudo executado)

| Teste | Resultado |
|---|---|
| `guard-bash-bypass`: `--no-verify` | **exit 2 (bloqueado)** ✓ |
| `guard-bash-bypass`: `--unset core.hooksPath` e `-c core.hooksPath=/dev/null` | **exit 2** ✓ |
| `guard-bash-bypass`: `git config core.hooksPath .githooks` e comando comum | exit 0 ✓ |
| `pre-commit` sem staging | mensagem explícita, exit 0 ✓ |
| `pre-push` simulado (branch nova, stdin real) | metric_honesty OK → index_drift OK → selfcheck **bloqueia só pelos F2 legítimos** ✓ |
| `metric_honesty` em todos os md/json versionados | OK ✓ |
| `metric_honesty` em relatório desonesto sintético | **exit 1 (bloqueia)** ✓ |
| `framework_selfcheck` com `CI=1` | pula remote/hooksPath, mantém F2-untracked ✓ |
| `bash -n` nos 3 shells + `json.load` no settings | sintaxe OK ✓ |

Estado final do selfcheck: **5 FAILs, todos verdadeiros e de resolução humana** (4
arquivos a commitar + remote ausente). É o comportamento desejado: o gate não deixa o
problema ser esquecido.

---

## 4. Pendências que só você pode resolver (o gate vai cobrar)

```bash
cd ~/girardelli_tecnologia/SHIELD-ID/repository/shield_id

# 1. Versionar o framework completo (resolve 4 FAILs F2)
git add .agent .claude .githooks .github scripts AGENTS.md AGENTS.pt-BR.md .cursorrules .gitignore
git commit -m "feat(framework): PORT-1.1 — fail-closed hooks + hygiene class F no selfcheck"

# 2. Configurar remote e subir (resolve o F2-remote e liga o CI pela primeira vez)
git remote add origin <url-do-repo>
git push -u origin exp/port-framework-evolutions

# 3. Conferir: deve imprimir "framework_selfcheck: OK"
python3 scripts/guards/framework_selfcheck.py
```

Nota: o working tree também contém código novo untracked fora do framework
(`src/shield_id/api/`, `tests/test_api.py`, `tests/fixtures/`) — decida se entram no
mesmo commit ou num commit próprio do épico correspondente.

---

## 5. Sobre o credit_analyser

As mesmas correções estruturais de lá (entry points AGENTS.md/CLAUDE.md, versionar
`.agent/`, corrigir dados falsos do scan, DATABASE-ENGINEER para MongoDB, thresholds
target 85%, remover PCI-DSS) continuam pendentes — mapeadas em
`credit_analyser/AUDITORIA_ESTRUTURA_AGENT_2026-07-21.md`. Quando for portar, a classe F
deste selfcheck é reaproveitável quase sem mudança (os caminhos são os mesmos por design).
