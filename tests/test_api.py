"""Testes de contrato da Detection API (T-US009-01).

Cobre /api/v1/verify (caminhos PASS, REVIEW e FLAG), o formato do envelope, a
presença do token, a explicabilidade (fatores), a NÃO-devolução da entrada crua
(I1/rule 04) e o /api/v1/health.

Rodar com a raiz `src` no path (como os demais testes do repo):
    PYTHONPATH=src python3 -m pytest tests/test_api.py -q
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from shield_id.api.app import create_app
from shield_id.api.config import DEFAULT_API_CONFIG

# Entradas com score determinístico (SHA-256 do MockDetector) escolhidas para cair
# em cada faixa de decisão definida pelo ApiConfig (review=0.25, flag=0.50).
PASS_TEXT = "Legitimate bank statement text sample."  # artifact ~0.094 -> PASS
REVIEW_TEXT = "synthetic forged document body"  # artifact ~0.305 -> REVIEW
FLAG_TEXT = "attack payload generated text"  # artifact ~0.555 -> FLAG


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def _post(client: TestClient, text: str, subject: str = "subject-xyz"):
    return client.post(
        "/api/v1/verify", json={"subject_ref": subject, "document_text": text}
    )


def test_health_envelope(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["trace_id"]
    assert body["data"]["status"] == "ok"
    assert body["data"]["detector_ready"] is True
    assert body["data"]["api_version"] == DEFAULT_API_CONFIG.api_version


def test_verify_envelope_shape(client: TestClient) -> None:
    resp = _post(client, PASS_TEXT)
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) >= {"data", "success", "trace_id"}
    assert body["success"] is True
    assert body["trace_id"]
    data = body["data"]
    assert 0.0 <= data["score"] <= 1.0
    assert data["factors"], "score deve ser explicável (rule 01)"
    assert data["token"]["value"], "token presente (não-reversível)"
    assert data["token"]["algorithm"] == "HMAC-SHA256"


def test_verify_pass_path(client: TestClient) -> None:
    data = _post(client, PASS_TEXT).json()["data"]
    assert data["decision"] == "PASS"
    assert data["requires_human_review"] is False


def test_verify_review_path_routes_to_human(client: TestClient) -> None:
    data = _post(client, REVIEW_TEXT).json()["data"]
    assert data["decision"] == "REVIEW"
    assert data["requires_human_review"] is True  # rule 06


def test_verify_flag_path_routes_to_human(client: TestClient) -> None:
    data = _post(client, FLAG_TEXT).json()["data"]
    assert data["decision"] == "FLAG"
    assert data["requires_human_review"] is True  # rule 06


def test_verify_is_deterministic(client: TestClient) -> None:
    first = _post(client, FLAG_TEXT).json()["data"]["score"]
    second = _post(client, FLAG_TEXT).json()["data"]["score"]
    assert first == second


def test_verify_never_echoes_raw_input(client: TestClient) -> None:
    """I1/rule 04 + rule 16: a resposta NUNCA contém o texto cru da entrada."""
    secret_doc = "ULTRA-SECRET-DOCUMENT-BODY-DO-NOT-LEAK-12345"
    raw = _post(client, secret_doc).text
    assert secret_doc not in raw
    assert "ULTRA-SECRET" not in raw


def test_verify_rejects_unknown_fields(client: TestClient) -> None:
    """rule 01: schema estrito (extra=forbid) -> 422 em campo desconhecido."""
    resp = client.post(
        "/api/v1/verify",
        json={"subject_ref": "s", "document_text": "x", "raw_face": "blob"},
    )
    assert resp.status_code == 422


def test_verify_rejects_empty_document(client: TestClient) -> None:
    resp = client.post("/api/v1/verify", json={"subject_ref": "s", "document_text": ""})
    assert resp.status_code == 422


def test_token_is_not_reversible_payload(client: TestClient) -> None:
    """O token é um HMAC hex de 64 chars — referência, não armazém da entrada."""
    token = _post(client, PASS_TEXT).json()["data"]["token"]["value"]
    assert len(token) == 64
    assert all(c in "0123456789abcdef" for c in token)
    assert PASS_TEXT not in token
