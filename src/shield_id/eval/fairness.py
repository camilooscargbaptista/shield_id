"""US-002 / T-002-a — Disaggregated fairness audit (rule 06).
Disaggregated FPR is the PRIMARY metric; the global FPR is secondary. Target = FPR-under-parity.
A flat global FPR can hide a high per-segment FPR — for SHIELD-ID that is an ethical failure disguised
as a metric success. Pure stdlib. Thresholds/alpha are PARAMETERS (rule 32 — no hardcoded defaults)."""
import math
from typing import Dict, List, Tuple

def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def fpr(scores: List[float], labels: List[int], threshold: float) -> Tuple[float, int, int]:
    """FPR on legitimate samples (label 0). Returns (fpr, fp, n_legit)."""
    fp = sum(1 for s, y in zip(scores, labels) if y == 0 and s >= threshold)
    n = sum(1 for y in labels if y == 0)
    return ((fp / n) if n else 0.0, fp, n)

def two_proportion_p(fp1: int, n1: int, fp2: int, n2: int) -> float:
    """Two-proportion z-test p-value (segment vs rest). 1.0 if undefined."""
    if n1 == 0 or n2 == 0:
        return 1.0
    p1, p2 = fp1 / n1, fp2 / n2
    pool = (fp1 + fp2) / (n1 + n2)
    denom = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    if denom == 0:
        return 1.0
    z = (p1 - p2) / denom
    return 2.0 * (1.0 - _phi(abs(z)))

def disaggregated_fpr(scores: List[float], labels: List[int], segments: List[str],
                      threshold: float) -> Dict[str, dict]:
    """Per-segment FPR + counts."""
    out = {}
    segs = sorted(set(segments))
    for seg in segs:
        s = [sc for sc, sg in zip(scores, segments) if sg == seg]
        y = [lb for lb, sg in zip(labels, segments) if sg == seg]
        f, fp, n = fpr(s, y, threshold)
        out[seg] = {"fpr": round(f, 4), "fp": fp, "n_legit": n}
    return out

def audit_parity(scores: List[float], labels: List[int], segments: List[str],
                 threshold: float, alpha: float) -> dict:
    """PRIMARY fairness audit. Verdict BLOCK if any segment's FPR differs significantly (p<alpha)
    from the rest. Returns the disaggregated table + verdict (rule 06 / FAIRNESS-GATE)."""
    per = disaggregated_fpr(scores, labels, segments, threshold)
    glob_fpr, _, _ = fpr(scores, labels, threshold)
    findings = []
    for seg, d in per.items():
        fp_rest = sum(v["fp"] for k, v in per.items() if k != seg)
        n_rest = sum(v["n_legit"] for k, v in per.items() if k != seg)
        p = two_proportion_p(d["fp"], d["n_legit"], fp_rest, n_rest)
        sig = p < alpha
        d["p_value_vs_rest"] = round(p, 4)
        d["significant"] = sig
        if sig:
            findings.append(seg)
    fprs = [d["fpr"] for d in per.values()]
    return {
        "primary_metric": "disaggregated_fpr",
        "global_fpr_secondary": round(glob_fpr, 4),
        "per_segment": per,
        "max_gap_pp": round((max(fprs) - min(fprs)) * 100, 2) if fprs else 0.0,
        "significant_segments": findings,
        "verdict": "BLOCK" if findings else "PASS",
        "alpha": alpha,
        "note": "FPR-under-parity is the target; the global FPR is secondary (rule 06).",
    }
