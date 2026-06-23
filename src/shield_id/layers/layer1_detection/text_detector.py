"""US-007 — LLM-generated-text document detector (Layer 1, document consistency).

Approach: fine-tune a PRETRAINED text encoder (rule 05 — NEVER from scratch) as a binary classifier:
  label 0 = human-written document text   |   label 1 = LLM-generated document text (synthetic attack).
The output `artifact_score` (P(synthetic)) feeds the scoring orchestrator + the cross-generator eval harness.

Runs on a cloud GPU (decision D11). torch/transformers are imported LAZILY so that non-GPU tooling
(guards, eval plumbing, packaging) can import this module without the heavy deps installed.

Rules honored: 05 (fine-tune, not from scratch) · 32 (config-driven) · 15 (this BUILDER reports NO metric;
`eval-independent` certifies) · 02 (seeded/deterministic). No biometrics involved (text only).
"""
from __future__ import annotations
from typing import List, Sequence
from .config import TextDetectorConfig


def _torch():
    import torch  # noqa: PLC0415
    return torch


class TextForgeryDetector:
    """Fine-tunable LLM-text detector. Build → fit() on GPU → predict_proba()."""

    def __init__(self, cfg: TextDetectorConfig, device: str | None = None):
        self.cfg = cfg
        torch = _torch()
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification  # noqa: PLC0415
        self.tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
        # num_labels=2: human vs LLM-generated. Loads PRETRAINED weights (rule 05).
        self.model = AutoModelForSequenceClassification.from_pretrained(
            cfg.base_model, num_labels=2
        ).to(self.device)

    def _encode(self, texts: Sequence[str]):
        return self.tokenizer(
            list(texts), truncation=True, max_length=self.cfg.max_length,
            padding=True, return_tensors="pt",
        )

    def fit(self, texts: List[str], labels: List[int]) -> "TextForgeryDetector":
        torch = _torch()
        from torch.utils.data import DataLoader, TensorDataset  # noqa: PLC0415
        torch.manual_seed(self.cfg.seed)
        enc = self._encode(texts)
        ds = TensorDataset(enc["input_ids"], enc["attention_mask"], torch.tensor(labels))
        dl = DataLoader(ds, batch_size=self.cfg.batch_size, shuffle=True)
        opt = torch.optim.AdamW(self.model.parameters(), lr=self.cfg.lr)
        self.model.train()
        for _epoch in range(self.cfg.epochs):
            for input_ids, attn, y in dl:
                opt.zero_grad()
                out = self.model(
                    input_ids=input_ids.to(self.device),
                    attention_mask=attn.to(self.device),
                    labels=y.to(self.device),
                )
                out.loss.backward()
                opt.step()
        return self

    def predict_proba(self, texts: Sequence[str]) -> List[float]:
        """P(text is LLM-generated) for each input — the `artifact_score`."""
        torch = _torch()
        self.model.eval()
        enc = self._encode(texts)
        with torch.no_grad():
            logits = self.model(
                input_ids=enc["input_ids"].to(self.device),
                attention_mask=enc["attention_mask"].to(self.device),
            ).logits
            probs = torch.softmax(logits, dim=-1)[:, 1]
        return [float(p) for p in probs.cpu()]

    def save(self, path: str) -> None:
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
