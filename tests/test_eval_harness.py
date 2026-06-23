import random, pytest
from shield_id.eval.splits import SplitsManifest, CrossGeneratorViolation, load_manifest
from shield_id.eval.cross_generator import run_cross_generator, NoCrossGeneratorError
from shield_id.eval.metrics import precision_recall_at_fpr

def test_manifest_refuses_held_out_in_train():
    with pytest.raises(CrossGeneratorViolation):
        SplitsManifest(train_generators=["A", "C"], held_out_generator="C", seed=42)

def test_manifest_ok():
    m = load_manifest({"train_generators": ["A", "B"], "held_out_generator": "C", "seed": 42})
    assert m.held_out_generator == "C"

def _toy(rng, sep):
    # synthetic: attacks score high, legit low; sep controls separability
    scores, labels = [], []
    for _ in range(200):
        labels.append(1); scores.append(min(1.0, rng.gauss(0.5 + sep, 0.15)))
    for _ in range(200):
        labels.append(0); scores.append(max(0.0, rng.gauss(0.5 - sep, 0.15)))
    return scores, labels

def test_cross_generator_reports_delta_not_point():
    rng = random.Random(42)
    m = SplitsManifest(["A", "B"], "C", 42)
    sa, la = _toy(rng, 0.30); sb, lb = _toy(rng, 0.30); sc, lc = _toy(rng, 0.10)  # C harder (unseen)
    rep = run_cross_generator(m, {"A": sa, "B": sb, "C": sc}, {"A": la, "B": lb, "C": lc}, 0.05, 200)
    assert rep["headline"] == "cross-generator"
    assert "recall_ci95" in rep["cross_generator"]      # a curve/interval, not a bare point
    assert rep["robustness_delta_pp"] <= 0              # harder unseen generator degrades recall

def test_refuses_headline_without_held_out():
    m = SplitsManifest(["A", "B"], "C", 42)
    with pytest.raises(NoCrossGeneratorError):
        run_cross_generator(m, {"A": [0.9], "B": [0.8]}, {"A": [1], "B": [1]}, 0.05, 10)  # no C
