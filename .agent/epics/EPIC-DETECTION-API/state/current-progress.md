# EPIC-DETECTION-API — Live progress
State: em-andamento (US-007 código escrito; treino pendente de GPU — D11)
US-007 (Layer 1 — detector texto-LLM): CÓDIGO REAL pronto e compilando:
  - src/shield_id/layers/layer1_detection/{config,text_detector}.py (fine-tune de transformer pré-treinado, rule 05)
  - src/shield_id/training/train_text_detector.py (split cross-generator; emite predictions.jsonl; builder sem métrica, rule 15)
  - src/shield_id/data/text_redteam.py (spec de dados; sem PII real, I2)
  - requirements-gpu.txt · RUN_ON_GPU.md
Verificação: py_compile OK; guards verdes (no_hardcoded/no_raw_biometric/no_real_pii).
PENDENTE (do lead, na GPU): dados (RAID/M4/HC3 ou geração) → treino → certificação eval-independent.
Próximas US: US-008 (Layer 2, especificada/simulada — D7) · US-009 (FastAPI /verify) · US-010 (Layer 3 spec).
