"""Experiment config (rule 32: NO hardcoded thresholds/targets in logic — they live here).
Loaded from a dict; in production read a frozen yaml per experiment (rule 02)."""
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class EvalConfig:
    fpr_target: float = 0.001          # D5: a target to TEST, not a promise
    # I4 / rule 05: nomes REAIS de geradores do RAID (liamdugan/raid).
    # Geradores vistos no treino; o held-out NUNCA aparece aqui.
    train_generators: List[str] = field(
        default_factory=lambda: ["chatgpt", "mistral-chat", "mpt-chat"]
    )
    held_out_generator: str = "gpt4"   # rule 05 / I4: existe no RAID, nunca no treino
    seed: int = 42                     # determinism (rule 02)
    bootstrap_n: int = 1000

DEFAULT = EvalConfig()
