"""Router /api/v1/health (rule 16: health endpoint)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from ..config import ApiConfig
from ..dependencies import get_api_config, get_detector
from ..detector import Detector
from ..schemas import Envelope, HealthStatus

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=Envelope[HealthStatus])
def health(
    detector: Detector = Depends(get_detector),
    cfg: ApiConfig = Depends(get_api_config),
) -> Envelope[HealthStatus]:
    """Reporta prontidão da API e se um detector está injetado (rule 16)."""
    status = HealthStatus(
        status="ok",
        detector_ready=detector is not None,
        api_version=cfg.api_version,
    )
    return Envelope[HealthStatus](data=status, success=True, trace_id=str(uuid.uuid4()))
