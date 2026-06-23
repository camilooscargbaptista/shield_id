# US-007 — Rodar o detector de texto-LLM na GPU (D11)

> Eu (agente) escrevi o **código real**; este ambiente não tem GPU/rede pra modelos, então **o treino roda
> aqui, na sua nuvem.** Honra rule 05 (fine-tune, não do zero), I4/D8 (cross-generator), rule 15 (builder não
> reporta métrica — o `eval-independent` certifica).

## 1. Dados (escolha um)
- **Recomendado (rápido + crível):** usar um dataset aberto multi-gerador de texto-LLM — **RAID**, **M4** ou
  **HC3** — que já tem estrutura cross-generator + controle humano público (sem PII, I2). Converta para o JSONL:
  `{"text": "...", "label": 0|1, "generator": "human"|"gpt-4o"|"claude"|"llama", "segment": "<seg>"}`.
- **Alternativa:** gerar via `src/shield_id/data/text_redteam.py` (chama as APIs dos LLMs — **chaves por env**,
  nunca no código, rule 13) + um corpus público de texto de documento como controle humano.
> Garanta que o **gerador held-out (`config.held_out_generator`, ex. "llama") nunca aparece no treino.**

## 2. Colab (caminho mais rápido)
```bash
# Runtime → Change runtime type → GPU
git clone <seu-repo>/shield_id && cd shield_id
pip install -r requirements-gpu.txt
# coloque seus dados em data/text-redteam.jsonl
python -m src.shield_id.training.train_text_detector --data data/text-redteam.jsonl --out artifacts/text-detector
```

## 3. AWS (EC2 GPU ou SageMaker)
- EC2 **g5.xlarge** ou **g4dn.xlarge** (Deep Learning AMI, CUDA pronto), ou um SageMaker training job.
- Mesmos passos do Colab. Modelo + `predictions.jsonl` + `model-card.json` saem em `artifacts/text-detector/`.

## 4. Certificação (M5/D4 — separado do build)
O treino **não reporta acurácia** (rule 15). Depois do treino:
```bash
# o eval-independent re-roda o protocolo cross-generator + fairness sobre as predições do held-out:
python scripts/agent/verify_eval.py artifacts/text-detector/predictions.jsonl   # (adaptar p/ ler JSONL)
```
Veredito (PASS/FAIL) com **robustness delta cross-generator** como manchete + FPR desagregado (fairness).

## 5. Ajustes comuns (em `layers/layer1_detection/config.py` — rule 32)
`base_model` (roberta-base → um detector mais forte), `epochs`, `batch_size`, `lr`, `train_generators`,
`held_out_generator`, `fpr_target`. Nada de hardcode no código.

## AWS (passo-a-passo detalhado)
Ver **RUN_ON_AWS.md** (subir instância, treinar, baixar, desligar + modo hands-off via Claude Code).
