"""US-003..006 — Red-team synthetic data pipeline (WS-B).

HONESTY NOTE (M1/D5): this environment has no frontier generator / GPU / network. This module produces
**procedural synthetic placeholder records** (structured feature vectors with per-"generator" artifact
profiles) — clearly NOT diffusion/LLM/TTS deepfakes. Its purpose is to exercise the WS-B loop end-to-end
(data -> baseline -> cross-generator harness -> fairness) reproducibly and honestly. The real generators
(GPT-4o/Stable Diffusion/ElevenLabs) are a Phase-2 compute task under EPIC-DETECTION-API.

Invariants honored: synthetic-only, NO real PII (I2); cross-generator splits by construction (I4/D8);
documents-first (D9); datasheet with validated demographic distribution (rule 03/06). stdlib-only.
"""
import random, json, hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Dict

# Per-"generator" artifact profile: mean artifact intensity for synthetic (attack) docs.
# Different generators imprint different artifact strengths -> cross-generator generalization is testable.
GENERATOR_PROFILES = {"A": 0.75, "B": 0.70, "C": 0.45}   # C (held-out) is HARDER (subtler artifacts)
SEGMENTS = ["seg-1", "seg-2", "seg-3", "seg-4"]           # abstract demographic/geographic segments

@dataclass
class Sample:
    sample_id: str
    generator: str            # A/B/C for attacks; "control" for legitimate
    label: int                # 1 = synthetic attack, 0 = legitimate
    segment: str
    modality: str             # "document" (D9)
    difficulty_tier: str      # easy/standard/stress
    artifact_score: float     # procedural feature (NOT a real biometric — synthetic stand-in)

def generate_batch(generators: List[str], n_per_gen: int, seg_dist: Dict[str, float],
                   seed: int) -> List[Sample]:
    """Generate attacks (per generator) + a matched legitimate control set. Reproducible from seed."""
    rng = random.Random(seed)
    segs, weights = list(seg_dist.keys()), list(seg_dist.values())
    out: List[Sample] = []
    i = 0
    for g in generators:
        mean = GENERATOR_PROFILES[g]
        for _ in range(n_per_gen):
            seg = rng.choices(segs, weights)[0]
            tier = rng.choices(["easy", "standard", "stress"], [0.3, 0.5, 0.2])[0]
            shift = {"easy": 0.1, "standard": 0.0, "stress": -0.15}[tier]
            score = min(1.0, max(0.0, rng.gauss(mean + shift, 0.12)))
            out.append(Sample(f"s{i:06d}", g, 1, seg, "document", tier, round(score, 4))); i += 1
    # legitimate control set (clean docs, low artifact score), same size as one generator's batch
    for _ in range(n_per_gen):
        seg = rng.choices(segs, weights)[0]
        out.append(Sample(f"s{i:06d}", "control", 0, seg, "document", "standard",
                          round(min(1.0, max(0.0, rng.gauss(0.20, 0.12))), 4))); i += 1
    return out

def baseline_score(s: Sample) -> float:
    """Trivial DATASET baseline (NOT the product detector): the artifact feature itself.
    Exists only to benchmark the dataset and exercise the harness (US-006)."""
    return s.artifact_score

def validate_demographics(samples: List[Sample]) -> Dict[str, dict]:
    """rule 03/06: document the dataset's own demographic distribution (so fairness measures the
    detector, not the generator's bias). Returns per-segment counts + share."""
    total = len(samples)
    out = {}
    for seg in sorted(set(s.segment for s in samples)):
        n = sum(1 for s in samples if s.segment == seg)
        out[seg] = {"count": n, "share": round(n / total, 4) if total else 0.0}
    return out

def _shard_controls(controls: List[Sample], groups: List[str]) -> Dict[str, List[Sample]]:
    """Particiona os controles (label==0) em shards DISJUNTOS, um por grupo de gerador, por
    sha256(sample_id) (rule 07: determinístico, sem RNG). Cada controle cai em exatamente UM grupo,
    então nenhum negativo é compartilhado entre grupos (sem vazamento) e os controles não são
    contados em dobro no pool in-distribution."""
    shards: Dict[str, List[Sample]] = {g: [] for g in groups}
    n = len(groups)
    for s in controls:
        idx = int(hashlib.sha256(s.sample_id.encode("utf-8")).hexdigest()[:16], 16) % n
        shards[groups[idx]].append(s)
    return shards


def split_for_cross_generator(samples: List[Sample], train_generators: List[str], held_out: str):
    """Build the cross-generator eval inputs: cada gerador de treino {A,B} e o held-out C recebe seu
    PRÓPRIO shard disjunto de controle (I4/D8). Dividir os controles em shards por gerador elimina o
    vazamento anterior (os mesmos controles em todos os grupos) E a dupla contagem dos controles no
    pool in-distribution. Returns (scores_by_gen, labels_by_gen) consumable by eval.cross_generator."""
    if held_out in train_generators:
        raise ValueError(f"held_out '{held_out}' in train {train_generators} — circularity (rule 05/I4). Refusing.")
    groups = train_generators + [held_out]
    control_shards = _shard_controls([s for s in samples if s.label == 0], groups)
    scores_by_gen, labels_by_gen = {}, {}
    for g in groups:
        grp = [s for s in samples if s.generator == g] + control_shards[g]
        scores_by_gen[g] = [baseline_score(s) for s in grp]
        labels_by_gen[g] = [s.label for s in grp]
    return scores_by_gen, labels_by_gen

def datasheet(samples: List[Sample], train_generators, held_out, seed) -> dict:
    return {
        "name": "SHIELD-ID Red-Team Document Dataset (procedural placeholder v0)",
        "honesty_note": "Procedural synthetic stand-ins, NOT frontier-generator deepfakes. For pipeline/harness validation.",
        "modality": "document (D9)", "real_pii": False, "synthetic_only": True,
        "generators": {"train": train_generators, "held_out": held_out, "profiles": GENERATOR_PROFILES},
        "composition": {"attacks": sum(1 for s in samples if s.label == 1),
                        "legitimate_control": sum(1 for s in samples if s.label == 0)},
        "demographic_distribution": validate_demographics(samples),
        "labeling": "per sample: generator, label, segment, modality, difficulty_tier",
        "seed": seed, "license": "permissive open-source (intended)",
        "limitations": "artifacts are procedural, not real generative-model fingerprints; replace with real "
                       "generators (GPT-4o/Stable Diffusion/ElevenLabs) under EPIC-DETECTION-API + compute.",
    }
