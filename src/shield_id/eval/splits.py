"""T-001-a — Splits manifest. Enforces cross-generator-by-construction (rule 05 / I4 / D8):
the held-out generator MUST NOT appear in the training generators."""
from dataclasses import dataclass
from typing import List

class CrossGeneratorViolation(ValueError):
    """Raised if the held-out generator leaks into training (circularity trap — LC-001)."""

@dataclass(frozen=True)
class SplitsManifest:
    train_generators: List[str]
    held_out_generator: str
    seed: int

    def __post_init__(self):
        if self.held_out_generator in self.train_generators:
            raise CrossGeneratorViolation(
                f"held_out_generator '{self.held_out_generator}' is in train_generators "
                f"{self.train_generators} — this is the circularity trap (rule 05/I4). Refusing."
            )

def load_manifest(d: dict) -> SplitsManifest:
    return SplitsManifest(
        train_generators=list(d["train_generators"]),
        held_out_generator=str(d["held_out_generator"]),
        seed=int(d.get("seed", 0)),
    )
