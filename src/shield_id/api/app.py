"""Factory da aplicação FastAPI (rule 01: app versionado, envelope, detector injetado).

`create_app` injeta um `Detector` e um `ApiConfig` no `app.state`. Por padrão usa o
`MockDetector` determinístico (D11). Quando o modelo real estiver certificado, basta
passar `detector=TextForgeryDetector(...)` aqui — os routers não mudam.
"""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI

from .config import DEFAULT_API_CONFIG, ApiConfig
from .detector import Detector, MockDetector
from .routers import health, verify


def create_app(
    detector: Optional[Detector] = None, api_config: Optional[ApiConfig] = None
) -> FastAPI:
    """Constrói o app FastAPI com o detector e config injetados.

    Args:
        detector: implementação do `Detector`. Default: `MockDetector` (D11).
        api_config: limiares/versão. Default: `DEFAULT_API_CONFIG` (rule 32).
    """
    app = FastAPI(title="SHIELD-ID Detection API", version="0.1.0")
    app.state.detector = detector if detector is not None else MockDetector()
    app.state.api_config = api_config if api_config is not None else DEFAULT_API_CONFIG

    app.include_router(health.router)
    app.include_router(verify.router)
    return app


# Alvo padrão para `uvicorn shield_id.api.app:app` (usa o MockDetector — D11).
app = create_app()
