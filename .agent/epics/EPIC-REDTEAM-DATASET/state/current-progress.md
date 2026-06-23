# EPIC-REDTEAM-DATASET — Live progress
State: em-andamento (pipeline + baseline + datasheet construídos; geradores reais pendentes de compute)
US: US-003 pipeline ✓ · US-004 splits cross-gen ✓ · US-005 datasheet+demográfico ✓ · US-006 baseline ✓ (procedural)
Artefatos: src/shield_id/data/redteam.py · DATASHEET.md · datasheet.json · splits-manifest.json · tests
Verificação: guards verdes (no_raw_biometric/no_hardcoded/no_real_pii); 5/5 testes; splits recusam C-no-treino.
Baseline (procedural): cross-gen recall ≈0.63 vs in-dist ≈0.98 (delta ≈−35pp); fairness PASS (gap ≈1pp).
Pendente: geradores reais (compute) no EPIC-DETECTION-API; validador T-002-b integrado à FAIRNESS-GATE.
