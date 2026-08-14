"""T-DATA-01 — Conversor RAID (open multi-generator LLM-text dataset) → JSONL cross-generator.

Lê o dataset RAID (`liamdugan/raid`, ACL 2024) em modo *streaming* (são ~10M linhas — NUNCA
materializar tudo) e mapeia para o schema do red-team de texto:
    {"text": ..., "label": 0|1, "generator": "human"|"<llm>", "segment": "<domain>"}

Invariantes/regras honradas:
- I2 / rule 03: texto público do RAID (humano = fontes web/news/abstracts publicadas; sem PII real
  inserida por nós). A saída passa por `scripts/guards/no_real_pii.py` antes de ser aceita.
- I4 / rule 05: construção cross-generator — o gerador held-out (config) NUNCA entra no treino.
- rule 02: revisão do dataset e versão da lib `datasets` PINADAS; seed na config.
- rule 32: zero defaults silenciosos em lógica — caps, listas de geradores, domínios, seed e
  revisão vivem TODOS no `RaidLoaderConfig` (dataclass frozen); a lógica só lê a config.

Uso:
    python3 -m shield_id.data.load_open_dataset            # usa DEFAULT_LOADER
    python3 src/shield_id/data/load_open_dataset.py
"""
from __future__ import annotations

import json
import random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Versão da lib pinada para reprodutibilidade (rule 02). Verificada em runtime.
# mini-SSOT: DEVE bater com `datasets==4.5.0` em requirements-gpu.txt (o único outro lugar do pin).
PINNED_DATASETS_VERSION = "4.5.0"

# Token humano do RAID (a coluna `model` usa esta string para texto humano).
HUMAN_TOKEN = "human"


@dataclass(frozen=True)
class RaidLoaderConfig:
    """Config-driven (rule 32): nada de hardcode na lógica abaixo.

    Todos os nomes de gerador/domínio devem ser valores REAIS do RAID (datasheet do dataset):
      models  = [chatgpt, gpt4, gpt3, gpt2, llama-chat, mistral, mistral-chat,
                 mpt, mpt-chat, cohere, cohere-chat]  (+ "human" como controle)
      domains = [abstracts, books, code, czech, german, news, poetry, recipes,
                 reddit, reviews, wiki]
    """

    # --- fonte (rule 02: pinning) ---
    hf_dataset: str = "liamdugan/raid"
    hf_config: str = "raid"  # split rotulado (train); raid_test não tem labels
    hf_split: str = "train"
    hf_revision: str = "865cac74188466cb0c3b7574a10204007b57a459"

    # --- nomes de colunas reais do RAID (descobertos, não assumidos) ---
    text_field: str = "generation"
    model_field: str = "model"
    domain_field: str = "domain"
    attack_field: str = "attack"

    # --- seleção cross-generator (I4 / rule 05) ---
    # Geradores de LLM usados no TREINO desta v1 (subconjunto real do RAID).
    train_llm_generators: Tuple[str, ...] = ("chatgpt", "mistral-chat", "mpt-chat")
    # Gerador HELD-OUT: existe no RAID e NÃO está em train_llm_generators.
    held_out_generator: str = "gpt4"
    # Inclui o controle humano (label=0).
    include_human: bool = True

    # --- domínios (segmentos) ---
    # Escolhidos por aparecerem CEDO no stream do RAID (abstracts: rows 0-741k,
    # books: a partir de ~741k) — alcançáveis sem baixar o CSV inteiro. Ambos são
    # texto publicado (abstracts científicos / trechos de livros): baixo risco de PII.
    domains: Tuple[str, ...] = ("abstracts", "books")

    # --- filtragem ---
    # v1 sem ataques adversariais; mantém só gerações "limpas".
    attack_keep: str = "none"

    # --- amostragem balanceada ---
    cap_per_generator: int = 6000  # teto por gerador (LLM); humano segue o mesmo teto
    seed: int = 42

    # --- saída ---
    output_path: str = "data/text-redteam.jsonl"

    # Limite de segurança: nº máximo de linhas a varrer no stream (proteção contra
    # varredura infinita; RAID é ordenado por domínio, então isto deve cobrir os
    # domínios escolhidos com folga). Ajuste na config, nunca na lógica.
    max_stream_rows: int = 4_000_000

    @property
    def selected_generators(self) -> List[str]:
        """Geradores que devem aparecer no JSONL (treino + held-out + humano)."""
        gens: List[str] = list(self.train_llm_generators) + [self.held_out_generator]
        if self.include_human:
            gens.append(HUMAN_TOKEN)
        return gens

    def validate(self) -> None:
        """Falha ALTO (rule 32: sem fallback silencioso) se a config violar invariantes."""
        if self.held_out_generator in self.train_llm_generators:
            raise ValueError(
                f"I4/rule 05 violado: held_out_generator '{self.held_out_generator}' "
                f"está nos train_llm_generators {self.train_llm_generators}."
            )
        if len(self.train_llm_generators) < 2:
            raise ValueError(
                "Protocolo cross-generator exige ≥2 geradores de LLM no treino "
                f"(recebido: {self.train_llm_generators})."
            )
        if not self.domains:
            raise ValueError("Ao menos 1 domínio (segment) é obrigatório.")
        if self.cap_per_generator <= 0:
            raise ValueError("cap_per_generator deve ser > 0.")


DEFAULT_LOADER = RaidLoaderConfig()


def _assert_pinned_datasets() -> None:
    """rule 02: versão da lib `datasets` pinada (sem default silencioso de versão)."""
    import datasets  # import tardio: a lib é pesada

    if datasets.__version__ != PINNED_DATASETS_VERSION:
        raise RuntimeError(
            f"rule 02: `datasets` versão {datasets.__version__} != pinada "
            f"{PINNED_DATASETS_VERSION}. Fixe a versão antes de gerar o dataset."
        )


def _label_for(generator: str) -> int:
    """label=0 sse humano; senão 1."""
    return 0 if generator == HUMAN_TOKEN else 1


def stream_records(cfg: RaidLoaderConfig) -> Tuple[List[dict], Dict[str, int], Dict[int, int]]:
    """Varre RAID em streaming e devolve (records, contagem_por_gerador, contagem_por_label).

    Amostragem balanceada: para cada gerador, coleta um *reservatório* de até
    `cap_per_generator` registros (reservoir sampling determinístico via seed) nos
    domínios e com o filtro de ataque definidos na config.
    """
    from datasets import load_dataset

    cfg.validate()
    _assert_pinned_datasets()

    rng = random.Random(cfg.seed)
    selected = set(cfg.selected_generators)
    domains = set(cfg.domains)

    ds = load_dataset(
        cfg.hf_dataset,
        cfg.hf_config,
        split=cfg.hf_split,
        streaming=True,
        revision=cfg.hf_revision,
    )

    # Reservoir sampling por gerador (balanceia e limita memória).
    reservoirs: Dict[str, List[dict]] = {g: [] for g in selected}
    seen_per_gen: Dict[str, int] = {g: 0 for g in selected}

    for i, row in enumerate(ds):
        if i >= cfg.max_stream_rows:
            break
        if row.get(cfg.attack_field) != cfg.attack_keep:
            continue
        if row.get(cfg.domain_field) not in domains:
            continue
        gen = row.get(cfg.model_field)
        if gen not in selected:
            continue

        text = row.get(cfg.text_field)
        if not text or not str(text).strip():
            continue

        rec = {
            "text": str(text),
            "label": _label_for(gen),
            "generator": gen,
            "segment": row.get(cfg.domain_field),
        }

        seen_per_gen[gen] += 1
        res = reservoirs[gen]
        if len(res) < cfg.cap_per_generator:
            res.append(rec)
        else:
            # substitui com probabilidade cap/seen (reservoir clássico)
            j = rng.randint(0, seen_per_gen[gen] - 1)
            if j < cfg.cap_per_generator:
                res[j] = rec

        # Early-stop: se todos os reservatórios estão cheios, podemos parar.
        if all(len(reservoirs[g]) >= cfg.cap_per_generator for g in selected):
            break

    records: List[dict] = [r for res in reservoirs.values() for r in res]
    rng.shuffle(records)

    by_gen = Counter(r["generator"] for r in records)
    by_label = Counter(r["label"] for r in records)
    return records, dict(by_gen), dict(by_label)


def write_jsonl(records: List[dict], path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def build(cfg: Optional[RaidLoaderConfig] = None) -> Dict:
    """Pipeline completo: stream → schema → JSONL. Devolve um manifest com evidências."""
    cfg = cfg or DEFAULT_LOADER
    records, by_gen, by_label = stream_records(cfg)
    write_jsonl(records, cfg.output_path)
    manifest = {
        "output_path": cfg.output_path,
        "hf_dataset": cfg.hf_dataset,
        "hf_revision": cfg.hf_revision,
        "datasets_version": PINNED_DATASETS_VERSION,
        "seed": cfg.seed,
        "train_llm_generators": list(cfg.train_llm_generators),
        "held_out_generator": cfg.held_out_generator,
        "domains": list(cfg.domains),
        "attack_keep": cfg.attack_keep,
        "cap_per_generator": cfg.cap_per_generator,
        "total_records": len(records),
        "counts_per_generator": by_gen,
        "counts_per_label": {str(k): v for k, v in by_label.items()},
    }
    return manifest


if __name__ == "__main__":
    m = build()
    print(json.dumps(m, ensure_ascii=False, indent=2))
