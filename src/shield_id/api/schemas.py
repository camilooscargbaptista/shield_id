"""Pydantic v2 I/O schemas para a Detection API (rule 01).

Contrato explicável (rule 01): o trust score NUNCA é um escalar opaco — sempre vem
acompanhado dos fatores que o compõem e de um token não-reversível (rule 04/I1: o
token referencia o veredito, jamais armazena a entrada crua).
"""
from __future__ import annotations

from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Decision(str, Enum):
    """Veredito da verificação. REVIEW/FLAG exigem revisão humana (rule 06)."""

    PASS = "PASS"
    REVIEW = "REVIEW"
    FLAG = "FLAG"


class VerifyRequest(BaseModel):
    """Entrada KYC para verificação.

    rule 04 / I1: NADA aqui é persistido. O texto do documento é consumido em
    memória pelo detector e descartado; só o score derivado + fatores mascarados saem.
    `subject_ref` é um pseudônimo opaco fornecido pelo chamador, NÃO PII.
    """

    model_config = ConfigDict(extra="forbid")

    subject_ref: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Pseudônimo opaco do sujeito (NÃO PII). Não é persistido.",
    )
    document_text: str = Field(
        ...,
        min_length=1,
        max_length=20_000,
        description="Texto do documento KYC a inspecionar. Consumido em memória; nunca persistido (I1).",
    )


class ContributingFactor(BaseModel):
    """Uma contribuição explicável para o trust score (rule 01 — score não-opaco)."""

    name: str = Field(..., description="Nome do fator (ex.: 'document_artifact_score').")
    contribution: float = Field(
        ..., description="Contribuição assinada para o score (negativa reduz confiança)."
    )
    detail: str = Field(
        default="",
        description="Detalhe legível e MASCARADO (rule 16) — nunca contém a entrada crua.",
    )


class VerificationToken(BaseModel):
    """Token explicável e NÃO-reversível (I1/rule 04).

    É uma referência assinada/hasheada do veredito — não armazena a entrada crua.
    Permite auditoria/contestação (rule 06) sem reter biometria/texto cru.
    """

    value: str = Field(..., description="Hash HMAC do veredito (não-reversível).")
    algorithm: str = Field(default="HMAC-SHA256", description="Algoritmo de derivação.")
    issued_at: str = Field(..., description="Timestamp ISO-8601 UTC da emissão.")


class TrustScore(BaseModel):
    """Resultado explicável da verificação (rule 01)."""

    score: float = Field(
        ..., ge=0.0, le=1.0, description="Trust score em [0,1] (1 = mais confiável)."
    )
    decision: Decision = Field(..., description="PASS / REVIEW / FLAG.")
    requires_human_review: bool = Field(
        ..., description="True para REVIEW/FLAG — roteia para revisão humana (rule 06)."
    )
    factors: List[ContributingFactor] = Field(
        ..., description="Fatores que compõem o score (explicabilidade — rule 01)."
    )
    token: VerificationToken = Field(..., description="Referência não-reversível do veredito.")


class ApiError(BaseModel):
    """Corpo de erro do envelope (rule 01)."""

    code: str
    message: str


class Envelope(BaseModel, Generic[T]):
    """Envelope de resposta padrão (rule 01): {data, success, trace_id}."""

    data: Optional[T] = None
    success: bool
    trace_id: str
    error: Optional[ApiError] = None


class HealthStatus(BaseModel):
    """Payload do /health (rule 16)."""

    status: str = Field(..., description="'ok' quando a API e o detector estão prontos.")
    detector_ready: bool = Field(..., description="True se um Detector está injetado.")
    api_version: str
