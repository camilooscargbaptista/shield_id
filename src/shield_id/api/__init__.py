"""SHIELD-ID Detection API (US-009).

A casca FastAPI `/api/v1/verify` que recebe entradas KYC e devolve um
**trust score explicável + token não-reversível**. Plugável no detector real
(`TextForgeryDetector`) via a interface `Detector`, mas testável agora com um
`MockDetector` determinístico (decisão D11 — sem GPU, sem modelo real).

Invariantes honrados:
- I1 / rule 04: NUNCA persiste entrada KYC ou texto cru — opera em memória e
  retorna apenas score derivado + fatores mascarados.
- rule 16: logs sem PII (mascarados).
- rule 32: limiares vêm do config (`ApiConfig`), nunca hardcoded na lógica.
- rule 06: decisões REVIEW/FLAG roteiam para revisão humana.
"""
from .app import create_app

__all__ = ["create_app"]
