"""Detector config — ALL hyperparameters/thresholds here (rule 32, no hardcoded defaults in logic)."""
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class TextDetectorConfig:
    # rule 05: fine-tune a PRETRAINED encoder — NEVER train from scratch.
    base_model: str = "roberta-base"          # swap for a stronger/cheaper base on GPU
    max_length: int = 512
    lr: float = 2e-5
    epochs: int = 3
    batch_size: int = 16
    seed: int = 42
    decision_threshold: float = 0.5           # operating cutoff (D5: a target to TEST)
    fpr_target: float = 0.001                 # rule 06: protect access
    # rule 32: fração determinística dos CONTROLES (label=0) que vai para o TREINO; o restante vai
    # para o held-out. O split é feito por sha256(text) (rule 07: sem RNG — estável entre execuções
    # e máquinas), garantindo que NENHUM negativo apareça no treino E no held-out ao mesmo tempo.
    # Sem isso, o FPR cross-generator seria medido sobre negativos já vistos no treino (I4/D8).
    control_train_fraction: float = 0.7
    # cross-generator (I4/D8): which LLM "generators" train vs held-out.
    # SSOT: estes nomes são REAIS do RAID (liamdugan/raid) e DEVEM ficar em sincronia
    # com config.py::EvalConfig e data/load_open_dataset.py::RaidLoaderConfig. Os
    # placeholders antigos (gpt-4o/claude/llama) NÃO existem no JSONL real e quebravam
    # o split (zero amostras de treino). Se um destes mudar, atualize os três juntos.
    train_generators: List[str] = field(
        default_factory=lambda: ["chatgpt", "mistral-chat", "mpt-chat"]
    )
    held_out_generator: str = "gpt4"  # existe no RAID, NUNCA em train_generators (I4/rule 05)
