# Experiment — detector v9 (métrica em forma de FRAÇÃO, in-distribution)

**Seed:** 7 · **Notebook:** `notebooks/eval_v9.ipynb`

## Reported outcome (in-distribution only)
- recall = 0.96
- precision = 0.94

Número reportado como manchete, medido só na própria distribuição de treino (sem gerador
segurado fora do treino). O guard antigo era cego a métricas em forma de fração.
