"""US-007 training entrypoint — RUN ON A CLOUD GPU (D11).

Pipeline: load JSONL (text/label/generator/segment) -> cross-generator split (train {A,B}, held-out C,
rule 05/I4) -> fine-tune the pretrained encoder -> save model + model-card -> emit predictions.jsonl on
the held-out generator + control set for the INDEPENDENT evaluator to certify (M5/D4).

This BUILDER reports NO accuracy/latency number (rule 15). It prints training progress only and writes
artifacts; `eval-independent` (verify_eval) computes the cross-generator + fairness verdict separately.
"""
import argparse, json, os
from typing import List, Dict
from ..layers.layer1_detection.config import TextDetectorConfig
from ..layers.layer1_detection.text_detector import TextForgeryDetector


def load_jsonl(path: str) -> List[dict]:
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def split_cross_generator(rows: List[dict], cfg: TextDetectorConfig):
    """Train on cfg.train_generators (+ human control); hold out cfg.held_out_generator entirely (I4/D8)."""
    if cfg.held_out_generator in cfg.train_generators:
        raise ValueError("held_out_generator is in train_generators — circularity (rule 05/I4). Refusing.")
    control = [r for r in rows if r["label"] == 0]
    train = [r for r in rows if r.get("generator") in cfg.train_generators] + control
    heldout = [r for r in rows if r.get("generator") == cfg.held_out_generator] + control
    return train, heldout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="JSONL: {text,label,generator,segment}")
    ap.add_argument("--out", default="artifacts/text-detector")
    a = ap.parse_args()
    cfg = TextDetectorConfig()
    rows = load_jsonl(a.data)
    train, heldout = split_cross_generator(rows, cfg)
    print(f"[train] {len(train)} samples ({len(cfg.train_generators)} generators + control)")
    print(f"[held-out] generator '{cfg.held_out_generator}': {sum(1 for r in heldout if r['label']==1)} attacks + control")

    det = TextForgeryDetector(cfg)
    det.fit([r["text"] for r in train], [int(r["label"]) for r in train])
    os.makedirs(a.out, exist_ok=True)
    det.save(a.out)

    # emit predictions on the held-out generator + control for the INDEPENDENT evaluator (M5/D4)
    scores = det.predict_proba([r["text"] for r in heldout])
    preds = [{"score": s, "label": int(r["label"]), "generator": r.get("generator"), "segment": r.get("segment")}
             for s, r in zip(scores, heldout)]
    with open(os.path.join(a.out, "predictions.jsonl"), "w") as f:
        for p in preds:
            f.write(json.dumps(p) + "\n")

    # model-card with EMPTY evaluation section (rule 15 — eval-independent fills it)
    card = {"model": "text-forgery-detector", "base_model": cfg.base_model, "from_scratch": False,
            "modality": "document-text (D9)", "evaluation": "PENDING eval-independent (cross-generator + fairness)",
            "privacy": "text-only; no biometrics; control corpus must be public/synthetic (I2)"}
    with open(os.path.join(a.out, "model-card.json"), "w") as f:
        json.dump(card, f, indent=2)
    print(f"[done] model + predictions.jsonl + model-card.json -> {a.out}")
    print("[builder] NO metric reported (rule 15). Next: scripts/agent/verify_eval.py certifies (M5/D4).")


if __name__ == "__main__":
    main()
