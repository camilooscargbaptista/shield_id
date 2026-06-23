"""T-001-b — Cross-generator protocol (rule 05 / I4 / D8). Computes the in-distribution vs
held-out-generator metrics and the ROBUSTNESS DELTA (the headline). REFUSES to produce a headline
if no held-out generator is present (the circularity guard, in code)."""
from typing import Dict, List
from .splits import SplitsManifest
from .metrics import precision_recall_at_fpr, roc_points, bootstrap_recall_ci

class NoCrossGeneratorError(RuntimeError):
    """Raised if asked for a headline without a held-out generator (rule 05 / I4)."""

def run_cross_generator(manifest: SplitsManifest,
                        scores_by_gen: Dict[str, List[float]],
                        labels_by_gen: Dict[str, List[int]],
                        fpr_target: float, bootstrap_n: int) -> dict:
    held = manifest.held_out_generator
    if held not in scores_by_gen:
        raise NoCrossGeneratorError(
            f"held-out generator '{held}' has no eval data — cannot report a cross-generator headline (rule 05/I4)."
        )
    # in-distribution = pooled train generators; cross-generator = held-out C
    in_s = sum((scores_by_gen[g] for g in manifest.train_generators), [])
    in_y = sum((labels_by_gen[g] for g in manifest.train_generators), [])
    cg_s = scores_by_gen[held]; cg_y = labels_by_gen[held]
    in_pr = precision_recall_at_fpr(in_s, in_y, fpr_target)
    cg_pr = precision_recall_at_fpr(cg_s, cg_y, fpr_target)
    ci = bootstrap_recall_ci(cg_s, cg_y, fpr_target, bootstrap_n, manifest.seed)
    robustness_delta_pp = round((cg_pr["recall"] - in_pr["recall"]) * 100, 2)  # negative = degradation
    return {
        "headline": "cross-generator",          # NOT the in-distribution number
        "held_out_generator": held,
        "in_distribution": in_pr,
        "cross_generator": {**cg_pr, "recall_ci95": ci},
        "robustness_delta_pp": robustness_delta_pp,
        "roc_cross_generator": roc_points(cg_s, cg_y),
        "fpr_target": fpr_target,
        "note": "Report the cross-generator recall + delta + curve; never the in-distribution point.",
    }
