# Datasheet — SHIELD-ID Red-Team Document Dataset (procedural placeholder v0)

> **Nota de honestidade (M1/D5):** amostras **sintéticas procedurais (stand-ins)**, **NÃO** deepfakes de
> gerador de fronteira. Propósito: validar o loop WS-B (dados → baseline → harness cross-generator → fairness)
> de forma reprodutível. Geradores reais (GPT-4o/Stable Diffusion/ElevenLabs) entram no EPIC-DETECTION-API + compute.

## Composição
- Modalidade: **documento** (D9). Sintético-only (I2), **sem PII real** (`no_real_pii.py` verde).
- 2000 amostras: 1500 ataque (geradores A/B/C, 500 cada) + 500 controle legítimo.
- Rótulos por amostra: gerador · label (1 ataque / 0 legítimo) · segmento · modalidade · tier de dificuldade · artifact_score (feature procedural).

## Geradores & split cross-generator (I4/D8)
- **Treino:** {A, B} · **Held-out:** **C** (nunca no treino — recusado por construção em `split_for_cross_generator`).
- Perfis de artefato: A=0.75, B=0.70, **C=0.45 (mais difícil — artefatos sutis)** → expõe o gap de generalização.

## Distribuição demográfica (validada — rule 03/06)
seg-1 ≈ 39% · seg-2 ≈ 32% · seg-3 ≈ 19% · seg-4 ≈ 10% (documentada para que a auditoria meça o detector, não o viés do gerador).

## Baseline (US-006) — NÃO é o detector do produto
Baseline trivial (o próprio artifact_score) via o harness cross-generator, só para benchmark do dataset:
in-distribution recall ≈ 0.98 vs **cross-generator (C) recall ≈ 0.63 — robustness delta ≈ −35pp** (a manchete).
Demonstra por que o cross-generator é obrigatório (rule 05). Fairness baseline: PASS (gap ≈ 1pp).

## Geração reprodutível
`src/shield_id/data/redteam.py` · seed fixo (42) · regenera idêntico de config+seed (rule 02).
Nunca commitar dado cru (`data/` gitignored). Manifest: `splits-manifest.json` · datasheet máquina: `datasheet.json`.

## Licença & ética
Open-source permissiva (pretendida). Sintético-only; sem PII real; uso proibido para vigilância em massa (licença do core).

## Limitações
Artefatos são procedurais, não fingerprints reais de modelos generativos. Substituir pelos geradores reais
sob EPIC-DETECTION-API. A diversidade demográfica de um dataset gerado por modelo real deve ser revalidada (rule 06).
