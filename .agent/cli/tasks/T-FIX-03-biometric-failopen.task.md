# T-FIX-03 — Corrigir fail-open do `no_raw_biometric`   (governança / EPIC-FRAMEWORK-EVOLUTIONS)

**Leia primeiro:** `AGENTS.md` · `.agent/CONSTITUTION.md` · `scripts/guards/no_raw_biometric.py` ·
`scripts/guards/no_hardcoded.py` (referência do padrão CORRETO) · `scripts/guards/no_real_pii.py` ·
`scripts/guards/secret_scan.py`

**Objetivo (1 frase):** eliminar o fail-open por precedência de operador na seleção de arquivos do
guard I1 e varrer os guards irmãos pelo mesmo padrão.

**O defeito (verificado pelo Oráculo em 2026-08-13, por execução a partir de /tmp):**
L41: `files = sys.argv[1:] or [...] if Path("src").exists() else []` — o `if/else` engole a expressão
inteira: sem `src/` no cwd, `files = []` MESMO com arquivos passados por argumento → guard imprime OK
e sai 0 sem escanear nada. `no_hardcoded.py` tem a mesma linha corretamente parentetizada — é descuido.

**Faça:**
1. Parentetize: `files = sys.argv[1:] or ([...] if Path("src").exists() else [])`.
2. Endureça fail-closed: se `sys.argv[1:]` vazio E fallback vazio → imprimir aviso e `exit 0` é
   aceitável APENAS quando de fato não há nada a escanear no repo; mas arquivo passado por argumento
   que não existe → warning explícito no stderr (não silêncio).
3. Inspecione `no_real_pii.py` e `secret_scan.py` pela mesma classe de defeito (precedência na seleção
   de arquivos); corrija se presente, declare "verificado, ausente" no bundle se não.
4. Teste de regressão `tests/test_guard_failclosed.py`: via `subprocess`, rode cada guard a partir de
   um cwd temporário SEM `src/`, passando por argumento um arquivo com violação plantada (ex.: um `.py`
   com `raw_face = open(...).read()` persistido) → exit DEVE ser 1. Rode também o caso limpo → exit 0.

**Restrições (rules aplicáveis):** 04 (I1) · 13 · 28 (correção de guard CRÍTICO → ADR via T-ADR-01)
**Saída (artefato + caminho):** `scripts/guards/no_raw_biometric.py` (± irmãos) ·
`tests/test_guard_failclosed.py`
**Done quando (verificável + evidência colada — M1):** prova bidirecional no bundle (violação de
qualquer cwd → exit 1 · limpo → exit 0) · suíte completa verde · `bash .githooks/pre-commit` num
commit de teste continua verde.
**Anti-padrões (proibidos):** mudar padrões de detecção do guard (escopo é SÓ seleção de arquivos) ·
qualquer `|| true` · exceção engolida.
**Atualizar:** CONTROL.md (status `READY_FOR_ORACULO` + Log) · bundle em `.agent/cli/evidence/T-FIX-03.md`.
