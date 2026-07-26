"""Serviço de verificação: orquestra detector -> decisão -> score explicável + token.

Mantém TODA a lógica fora dos routers (rule 01). I1/rule 04: opera em memória, nunca
persiste a entrada crua. rule 32: faixas de decisão vêm do `ApiConfig`. rule 16:
fatores/logs são mascarados (nunca contêm o texto cru).
"""
from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone

from .config import ApiConfig
from .detector import Detector
from .schemas import (
    ContributingFactor,
    Decision,
    TrustScore,
    VerificationToken,
)


def _mask(text: str) -> str:
    """Resumo NÃO-reversível para auditoria (rule 16/04): só comprimento + prefixo de hash.

    Nunca devolve o conteúdo cru — apenas metadados seguros para log/fator.
    """
    fingerprint = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    return f"len={len(text)} sha256:{fingerprint}…"


def _classify(artifact_score: float, cfg: ApiConfig) -> Decision:
    """Mapeia P(forjado) -> PASS/REVIEW/FLAG usando os limiares do config (rule 32)."""
    if artifact_score >= cfg.flag_threshold:
        return Decision.FLAG
    if artifact_score >= cfg.review_threshold:
        return Decision.REVIEW
    return Decision.PASS


def _issue_token(
    subject_ref: str, decision: Decision, artifact_score: float, issued_at: str, cfg: ApiConfig
) -> VerificationToken:
    """Emite um token NÃO-reversível (I1/rule 04): HMAC do veredito, não da entrada crua.

    O payload assinado é só metadado de veredito (pseudônimo + decisão + score + tempo),
    permitindo auditoria/contestação (rule 06) sem reter o texto/biometria cru.
    """
    payload = f"{subject_ref}|{decision.value}|{artifact_score:.6f}|{issued_at}"
    signature = hmac.new(
        cfg.token_signing_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return VerificationToken(value=signature, algorithm="HMAC-SHA256", issued_at=issued_at)


def verify(
    subject_ref: str, document_text: str, detector: Detector, cfg: ApiConfig
) -> TrustScore:
    """Executa a verificação e retorna um trust score explicável (rule 01).

    Fluxo: detector -> artifact_score -> trust_score (1 - artifact) -> decisão -> token.
    I1/rule 04: `document_text` é consumido aqui e descartado; só score derivado +
    fatores mascarados saem da função.
    """
    artifact_score = detector.predict_proba([document_text])[0]
    trust_score = 1.0 - artifact_score
    decision = _classify(artifact_score, cfg)
    issued_at = datetime.now(timezone.utc).isoformat()

    factors = [
        ContributingFactor(
            name="document_artifact_score",
            # contribuição assinada: quanto maior P(forjado), mais ela derruba a confiança.
            contribution=-round(artifact_score, 6),
            detail=_mask(document_text),
        )
    ]

    return TrustScore(
        score=round(trust_score, 6),
        decision=decision,
        requires_human_review=decision in (Decision.REVIEW, Decision.FLAG),
        factors=factors,
        token=_issue_token(subject_ref, decision, artifact_score, issued_at, cfg),
    )
