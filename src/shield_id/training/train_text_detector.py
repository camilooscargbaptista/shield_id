"""US-007 training entrypoint — RUN ON A CLOUD GPU (D11).

Pipeline: load JSONL (text/label/generator/segment) -> cross-generator split (train {A,B}, held-out C,
rule 05/I4) -> fine-tune the pretrained encoder -> save model + model-card -> emit predictions.jsonl on
the held-out generator + control set for the INDEPENDENT evaluator to certify (M5/D4).

This BUILDER reports NO accuracy/latency number (rule 15). It prints training progress only and writes
artifacts; `eval-independent` (verify_eval) computes the cross-generator + fairness verdict separately.
"""
import argparse, hashlib, json, os
from typing import List, Dict
from ..layers.layer1_detection.config import TextDetectorConfig
from ..layers.layer1_detection.text_detector import TextForgeryDetector


def load_jsonl(path: str) -> List[dict]:
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def _control_bucket(text: str) -> float:
    """Bucket determinístico em [0,1) derivado de sha256(text) — estável entre execuções e máquinas
    (rule 07: sem RNG). Usado para particionar os controles de forma reproduzível."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) / float(1 << 64)


def _split_controls(controls: List[dict], fraction: float):
    """Particiona os controles (label==0) em subconjuntos DISJUNTOS (train, held-out) por sha256(text)
    (rule 07: determinístico, sem RNG). Um controle atribuído ao treino nunca aparece no held-out —
    assim o FPR cross-generator jamais é medido sobre negativos já vistos no treino (I4/D8)."""
    train_c = [r for r in controls if _control_bucket(r["text"]) < fraction]
    heldout_c = [r for r in controls if _control_bucket(r["text"]) >= fraction]
    return train_c, heldout_c


def split_cross_generator(rows: List[dict], cfg: TextDetectorConfig):
    """Treina nos ataques de cfg.train_generators (+ um shard DISJUNTO de controle); segura os ataques
    de cfg.held_out_generator (+ o shard de controle complementar) inteiros (I4/D8). Os controles são
    divididos deterministicamente por hash, então nenhum negativo é compartilhado entre os dois lados."""
    if cfg.held_out_generator in cfg.train_generators:
        raise ValueError("held_out_generator is in train_generators — circularity (rule 05/I4). Refusing.")
    controls = [r for r in rows if r["label"] == 0]
    train_c, heldout_c = _split_controls(controls, cfg.control_train_fraction)
    train_attacks = [r for r in rows if r["label"] == 1 and r.get("generator") in cfg.train_generators]
    heldout_attacks = [r for r in rows if r["label"] == 1 and r.get("generator") == cfg.held_out_generator]
    train = train_attacks + train_c
    heldout = heldout_attacks + heldout_c
    # Verificação defensiva (I4/D8): os textos de train e held-out precisam ser DISJUNTOS. Se algum
    # texto aparecer nos dois lados, a medição cross-generator está contaminada — recusar, não reportar.
    overlap = {r["text"] for r in train} & {r["text"] for r in heldout}
    if overlap:
        raise ValueError(
            f"train/held-out share {len(overlap)} text(s) — control leakage violates cross-generator "
            f"isolation (rule 05/I4/D8). Refusing to produce a contaminated split."
        )
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
