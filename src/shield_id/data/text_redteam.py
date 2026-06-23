"""US-003/004 (text variant) — LLM-generated document-text data spec + generation skeleton.

NO real PII (I2): the human-control corpus must be PUBLIC/synthetic document text, never real user data.
Cross-generator by construction (I4/D8): the 'generator' field = which LLM wrote it; the held-out LLM
is never in training. Each record (JSONL):
    {"text": "...", "label": 0|1, "generator": "human"|"gpt-4o"|"claude"|"llama", "segment": "<demographic/geo>"}

RECOMMENDED (fastest, most credible): use an OPEN multi-generator LLM-text dataset that already has
cross-generator structure — e.g. RAID, M4, or HC3 — instead of generating from scratch. Map its
generator labels to this schema. That gives you real frontier-generator text + a held-out generator
for free, and a public human-control set (no PII).

If you DO generate (needs API keys on the GPU box; keys via env, never in code — rule 13):
"""
import os, json
from typing import List, Dict

DOC_PROMPTS = [
    "Write the body text of a {doctype} as if issued by an institution.",
    "Draft the textual content of a {doctype}, formal register.",
]
DOCTYPES = ["identity document", "proof of address", "bank statement", "employment letter"]

def generation_plan(generators: List[str], n_per_generator: int) -> Dict:
    """Returns the plan (no API call here). Fill in your provider client on the GPU box."""
    return {
        "generators": generators, "n_per_generator": n_per_generator,
        "prompts": DOC_PROMPTS, "doctypes": DOCTYPES,
        "note": "call each generator's API with these prompts; label=1, generator=<name>. "
                "Human control: sample PUBLIC document-text corpus, label=0, generator='human' (I2).",
        "api_keys": "read from env (OPENAI_API_KEY etc.) — NEVER hardcode (rule 13).",
    }

def write_jsonl(records: List[dict], path: str) -> None:
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
