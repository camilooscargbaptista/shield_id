"""T-001-b — Detection metrics. Reports CURVES, not a single point (rule 05).
Pure stdlib. Scores in [0,1]; label 1 = synthetic attack, 0 = legitimate."""
import random
from statistics import mean
from typing import List, Tuple, Dict

def _threshold_for_fpr(scores: List[float], labels: List[int], fpr_target: float) -> float:
    """Pick the threshold whose FPR on legitimate samples is <= fpr_target (closest)."""
    legit = sorted((s for s, y in zip(scores, labels) if y == 0), reverse=True)
    if not legit:
        return 1.0
    k = max(0, min(len(legit) - 1, int(fpr_target * len(legit))))
    return legit[k]

def precision_recall_at_fpr(scores: List[float], labels: List[int], fpr_target: float) -> Dict[str, float]:
    thr = _threshold_for_fpr(scores, labels, fpr_target)
    tp = sum(1 for s, y in zip(scores, labels) if s >= thr and y == 1)
    fp = sum(1 for s, y in zip(scores, labels) if s >= thr and y == 0)
    fn = sum(1 for s, y in zip(scores, labels) if s < thr and y == 1)
    tn = sum(1 for s, y in zip(scores, labels) if s < thr and y == 0)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    return {"threshold": thr, "precision": precision, "recall": recall, "fpr": fpr}

def roc_points(scores: List[float], labels: List[int], steps: int = 20) -> List[Tuple[float, float]]:
    """(fpr, tpr) curve — so we report a curve, not a point."""
    pts = []
    for i in range(steps + 1):
        thr = i / steps
        tp = sum(1 for s, y in zip(scores, labels) if s >= thr and y == 1)
        fp = sum(1 for s, y in zip(scores, labels) if s >= thr and y == 0)
        fn = sum(1 for s, y in zip(scores, labels) if s < thr and y == 1)
        tn = sum(1 for s, y in zip(scores, labels) if s < thr and y == 0)
        tpr = tp / (tp + fn) if (tp + fn) else 0.0
        fpr = fp / (fp + tn) if (fp + tn) else 0.0
        pts.append((round(fpr, 4), round(tpr, 4)))
    return pts

def bootstrap_recall_ci(scores: List[float], labels: List[int], fpr_target: float,
                        n: int, seed: int) -> Tuple[float, float]:
    rng = random.Random(seed)
    idx = list(range(len(scores)))
    recalls = []
    for _ in range(n):
        sample = [rng.choice(idx) for _ in idx]
        s = [scores[i] for i in sample]; y = [labels[i] for i in sample]
        recalls.append(precision_recall_at_fpr(s, y, fpr_target)["recall"])
    recalls.sort()
    lo = recalls[int(0.025 * n)]; hi = recalls[int(0.975 * n) - 1]
    return (round(lo, 4), round(hi, 4))
