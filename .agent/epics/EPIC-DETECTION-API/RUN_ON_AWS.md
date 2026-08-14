# US-007 — Rodar o detector na AWS GPU (passo-a-passo)

> Decisão: AWS (SSH-ável → um **Claude Code no seu Mac** pode executar tudo isto pra você, hands-off).
> Eu (agente Cowork) **não tenho acesso à sua AWS** — aqui está o roteiro + comandos prontos.

## 0. Pré-requisitos
- Conta AWS + um **key pair** SSH (`.pem`) na região escolhida (ex. `us-east-1` ou `sa-east-1` São Paulo).
- O **dataset** em JSONL `{text,label,generator,segment}` com **≥2 geradores** (o gargalo real — ver `RUN_ON_GPU.md` §1).
- (Opcional, pro modo hands-off) **AWS CLI** configurada no seu Mac (`aws configure`).

## 1. Instância recomendada
| Instância | GPU | US$/h (on-demand) | Quando |
|---|---|---|---|
| **g4dn.xlarge** | T4 16GB | ~0,53 | **padrão** — sobra pro roberta-base |
| g5.xlarge | A10G 24GB | ~1,01 | se quiser mais rápido / modelo maior |
> **Spot instance** corta ~60–70% (estimate; use se não se importar de poder ser interrompida). Disco: **100 GB gp3**.
> AMI: **"Deep Learning OSS Nvidia Driver AMI (Ubuntu)"** — já vem CUDA + PyTorch.

## 2A. Subir via Console (cliques)
EC2 → Launch instance → AMI: busque **"Deep Learning OSS"** → tipo **g4dn.xlarge** → seu key pair →
Security group: **SSH (22) só do SEU IP** → Storage **100 GB gp3** → Launch.

## 2B. Subir via AWS CLI (scriptável — Claude Code roda)
```bash
# pega a AMI mais recente do Deep Learning (Ubuntu, Nvidia) na sua região:
AMI=$(aws ec2 describe-images --owners amazon \
  --filters "Name=name,Values=Deep Learning OSS Nvidia Driver AMI*Ubuntu*" \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)
aws ec2 run-instances --image-id $AMI --instance-type g4dn.xlarge \
  --key-name SEU_KEYPAIR --security-group-ids sg-XXXX \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=shield-id-train}]'
```

## 3. Conectar + preparar
```bash
ssh -i SEU_KEYPAIR.pem ubuntu@<IP_PUBLICO>
source activate pytorch          # ambiente do DLAMI (CUDA + torch prontos)
git clone <seu-repo>/shield_id && cd shield_id    # ou scp dos arquivos src/ + requirements
pip install -r requirements-gpu.txt
# suba seus dados:  scp -i KEY.pem data.jsonl ubuntu@<IP>:~/shield_id/data/text-redteam.jsonl
```

## 3.5. Gerar o dataset RAID no box (T-DATA-01 — recomendado em vez do scp)
> O conversor já está escrito (`src/shield_id/data/load_open_dataset.py`, config-driven, rule 32).
> A sessão do agente NÃO consegue baixar o RAID (~10M linhas, CSV multi-GB ordenado por domínio) —
> por isso a **materialização roda aqui no box** (decisão do lead 22/jun: rodar na AWS, alinhado a D11).
```bash
# datasets==4.5.0 já foi instalado via `pip install -r requirements-gpu.txt` no §3 (pin único,
# alinhado ao RaidLoaderConfig / PINNED_DATASETS_VERSION — rule 02). NÃO reinstalar aqui.
python -m src.shield_id.data.load_open_dataset   # streaming + reservoir sampling → data/text-redteam.jsonl
# valide a privacidade ANTES de treinar (I2):
python3 scripts/guards/no_real_pii.py data/text-redteam.jsonl   # precisa sair 0
# confira as contagens por gerador/label impressas; o held-out (gpt4) NÃO pode aparecer no treino (I4)
```
> Split atual (em `src/shield_id/config.py`): treino = `chatgpt, mistral-chat, mpt-chat`;
> held-out = `gpt4`. No arquivo completo do RAID os 11 geradores existem → o split é satisfazível.
> Se `no_real_pii.py` sair 1 (ex.: domínios `news/reddit/reviews`), **PARE** e reporte — não limpe à mão.

## 4. Treinar + avaliar
```bash
python -m src.shield_id.training.train_text_detector \
  --data data/text-redteam.jsonl --out artifacts/text-detector
# saída: modelo + predictions.jsonl + model-card.json  (builder NÃO reporta métrica — rule 15)
# certificação (M5/D4): o eval-independent re-roda cross-generator + fairness sobre predictions.jsonl
```

## 5. Baixar o modelo + **DESLIGAR** (importante!)
```bash
# no seu Mac:
scp -i KEY.pem -r ubuntu@<IP>:~/shield_id/artifacts/text-detector ./artifacts/
# DESLIGUE pra não pagar à toa:
aws ec2 terminate-instances --instance-ids i-XXXX     # (ou "stop" se for reusar)
```

## 6. Guardrails de custo (faça uma vez)
- **AWS Budgets**: crie um alerta de US$ 20/mês → email se passar.
- **Spot** pra treinos longos; **terminate** sempre que acabar (a conta cara é GPU esquecida ligada).
- Lembrete: nossos dados são **sintéticos (I2)** → ok usar instância comum.

## Modo hands-off (o "roda lá" que você queria)
Com a **AWS CLI configurada no seu Mac**, peça ao **Claude Code** (no terminal do Mac):
*"suba uma g4dn.xlarge spot com o DLAMI, copie este repo + data.jsonl, rode o train_text_detector,
baixe artifacts/ e termine a instância."* — ele executa os passos 2B→5 de ponta a ponta.
