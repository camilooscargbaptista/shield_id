# T-US009-01 — FastAPI /api/v1/verify (com detector-mock testável)   (Épico DETECTION / US-009)

**Leia primeiro:** `AGENTS.md` · `.agent/rules/01-python-fastapi.md` · `.agent/rules/04-privacy-biometrics.md` ·
`docs/03-architecture/source/Architecture_C4_v0.1_EN.md` (§5 API Design) · `src/shield_id/layers/layer1_detection/text_detector.py`
**Objetivo:** a API `/api/v1/verify` que recebe entradas KYC e retorna **trust score explicável + token**,
plugável no detector real, mas **testável agora** com um detector-mock (sem GPU).
**Faça:**
1. `src/shield_id/api/` (FastAPI): router `verify`, `health`; schemas `TrustScore`, `ContributingFactor`, `VerificationToken` (pydantic).
2. Envelope `{data, success, trace_id}`; decisão PASS/REVIEW/FLAG; **REVIEW/FLAG → revisão humana** (rule 06).
3. Interface `Detector` + um `MockDetector` (score determinístico) p/ teste; o real (`TextForgeryDetector`) pluga depois.
4. **Sem persistir biometria/texto cru (I1/rule 04);** auditoria mascarada; limiar do config (rule 32).
5. Testes (pytest) do contrato verify + health. Rodar `uvicorn` + um `curl` de exemplo (evidência colada).
**Restrições:** 01 · 04/I1 · 06 · 13 · 32 · 16 (logs sem PII).
**Saída:** `src/shield_id/api/**` + `tests/test_api.py` + exemplo de `curl`.
**Done quando:** `curl POST /api/v1/verify` retorna score+fatores+token (output colado); testes verdes; guards verdes.
**Anti-padrões:** persistir input cru · score opaco (sem fatores) · limiar hardcoded.
**Nota D11:** esta é a API (casca), testável sem GPU. Pode construir; o **modelo real** só pluga após treino certificado.
**Atualizar:** CONTROL → T-US009-01 = concluída.
