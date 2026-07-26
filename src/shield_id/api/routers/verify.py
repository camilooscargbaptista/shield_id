"""Router /api/v1/verify — recebe entrada KYC, devolve trust score explicável + token.

rule 01: tipado, status codes corretos, detector injetado. I1/rule 04: nada persistido.
rule 16: log mascarado sem PII. rule 06: REVIEW/FLAG sinalizam revisão humana.
"""
from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, Depends

from ..config import ApiConfig
from ..dependencies import get_api_config, get_detector
from ..detector import Detector
from ..logging_utils import log_verification
from ..schemas import Envelope, TrustScore, VerifyRequest
from ..service import verify as run_verify

router = APIRouter(prefix="/api/v1", tags=["verify"])


@router.post("/verify", response_model=Envelope[TrustScore], status_code=200)
def verify(
    payload: VerifyRequest,
    detector: Detector = Depends(get_detector),
    cfg: ApiConfig = Depends(get_api_config),
) -> Envelope[TrustScore]:
    """Verifica uma entrada KYC e retorna trust score + fatores + token (rule 01).

    O texto do documento é consumido em memória pelo serviço e NUNCA persistido nem
    devolvido (I1/rule 04). REVIEW/FLAG marcam `requires_human_review=True` (rule 06).
    """
    trace_id = str(uuid.uuid4())
    started = time.perf_counter()

    result = run_verify(
        subject_ref=payload.subject_ref,
        document_text=payload.document_text,
        detector=detector,
        cfg=cfg,
    )

    latency_ms = (time.perf_counter() - started) * 1000.0
    # rule 16: log estruturado sem PII — só o veredito, nunca a entrada crua.
    log_verification(trace_id=trace_id, decision=result.decision.value, latency_ms=latency_ms)

    return Envelope[TrustScore](data=result, success=True, trace_id=trace_id)
