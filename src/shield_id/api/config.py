"""ApiConfig — limiares de decisão da API (rule 32: nada de número mágico na lógica).

Reusa o `decision_threshold` do detector (Layer 1) como cutoff base e adiciona o
limiar inferior de REVIEW, separando as três faixas de decisão PASS/REVIEW/FLAG.
Tudo aqui é config, não lógica — por isso vive fora dos routers/serviço.
"""
from __future__ import annotations

from dataclasses import dataclass

from shield_id.layers.layer1_detection.config import TextDetectorConfig


@dataclass(frozen=True)
class ApiConfig:
    """Limiares de decisão e metadados de versão da API.

    O `artifact_score` do detector é P(entrada é sintética/forjada). Quanto maior,
    menor a confiança. As faixas:
      - score <  review_threshold              -> PASS   (automático)
      - review_threshold <= score < flag_threshold -> REVIEW (revisão humana, rule 06)
      - score >= flag_threshold                -> FLAG   (revisão humana, rule 06)

    `flag_threshold` reusa o `decision_threshold` da Layer 1 (rule 32 — single source),
    enquanto `review_threshold` é a banda de incerteza abaixo dele.
    """

    api_version: str = "v1"
    # rule 32: cutoff de FLAG vem do config do detector (NÃO hardcoded aqui).
    flag_threshold: float = TextDetectorConfig.decision_threshold
    # banda de incerteza: metade do caminho até o cutoff de FLAG (derivado, não mágico).
    review_threshold: float = TextDetectorConfig.decision_threshold / 2.0
    # segredo de assinatura do token. Em produção vem de um secret manager (rule 13);
    # aqui é um placeholder NÃO-secreto só para tornar o token determinístico em teste.
    token_signing_key: str = "shield-id-mock-signing-key-not-a-secret"

    def __post_init__(self) -> None:
        if not (0.0 <= self.review_threshold <= self.flag_threshold <= 1.0):
            raise ValueError(
                "limiares inválidos: exige 0 <= review_threshold <= flag_threshold <= 1"
            )


DEFAULT_API_CONFIG = ApiConfig()
