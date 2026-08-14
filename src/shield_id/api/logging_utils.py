"""Log estruturado SEM PII (rule 16/04).

Emite uma linha JSON com `trace_id, layer, action, decision, latency_ms`. NUNCA
inclui a entrada KYC crua nem o texto do documento — só metadados de veredito.
"""
from __future__ import annotations

import json
import logging
import sys

_logger = logging.getLogger("shield_id.api")
if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


def log_verification(trace_id: str, decision: str, latency_ms: float) -> None:
    """Loga o evento de verificação como JSON, sem PII (rule 16).

    Note que NÃO recebe o texto do documento — por construção é impossível vazar a
    entrada crua aqui.
    """
    _logger.info(
        json.dumps(
            {
                "trace_id": trace_id,
                "layer": 1,
                "action": "verify",
                "decision": decision,
                "latency_ms": round(latency_ms, 3),
            }
        )
    )
