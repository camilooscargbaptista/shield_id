import random
from shield_id.eval.fairness import audit_parity, two_proportion_p, disaggregated_fpr

def _data(rng, seg_fprs, n_per=400):
    """Build legit(0)+attack(1) samples per segment; seg_fprs maps segment->target legit FPR."""
    scores, labels, segs = [], [], []
    for seg, target in seg_fprs.items():
        for _ in range(n_per):  # legit: score high (>=0.5) with prob = target FPR
            labels.append(0); segs.append(seg); scores.append(0.9 if rng.random() < target else 0.1)
        for _ in range(n_per):  # attacks: mostly detected
            labels.append(1); segs.append(seg); scores.append(0.9 if rng.random() < 0.9 else 0.1)
    return scores, labels, segs

def test_parity_pass_when_balanced():
    rng = random.Random(42)
    s, l, sg = _data(rng, {"A": 0.02, "B": 0.02, "C": 0.025})
    r = audit_parity(s, l, sg, threshold=0.5, alpha=0.01)
    assert r["verdict"] == "PASS", r
    assert r["primary_metric"] == "disaggregated_fpr"

def test_parity_block_when_segment_disparate():
    rng = random.Random(42)
    # segment C has a much higher FPR — the global average could still look OK
    s, l, sg = _data(rng, {"A": 0.01, "B": 0.01, "C": 0.20})
    r = audit_parity(s, l, sg, threshold=0.5, alpha=0.01)
    assert r["verdict"] == "BLOCK", r
    assert "C" in r["significant_segments"], r

def test_disaggregated_has_per_segment():
    rng = random.Random(1)
    s, l, sg = _data(rng, {"A": 0.02, "B": 0.02})
    per = disaggregated_fpr(s, l, sg, 0.5)
    assert set(per) == {"A", "B"} and all("fpr" in v for v in per.values())
