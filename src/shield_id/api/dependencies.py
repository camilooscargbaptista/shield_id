"""Dependency injection da API (rule 01: detector e config injetados, não globais rígidos).

O detector e o config são guardados no `app.state` pelo factory `create_app` e expostos
aos routers via `Depends`. Isso permite trocar o `MockDetector` pelo `TextForgeryDetector`
real depois SEM tocar nos routers.
"""
from __future__ import annotations

from fastapi import Depends, Request

from .config import ApiConfig
from .detector import Detector


def get_detector(request: Request) -> Detector:
    """Resolve o `Detector` injetado no app (mock agora, real depois — D11)."""
    return request.app.state.detector


def get_api_config(request: Request) -> ApiConfig:
    """Resolve o `ApiConfig` injetado (rule 32: limiares vêm daqui)."""
    return request.app.state.api_config


DetectorDep = Depends(get_detector)
ApiConfigDep = Depends(get_api_config)
