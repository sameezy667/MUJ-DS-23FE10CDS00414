"""
@file test_server.py
@description Unit and integration tests for FastAPI backend server and REST endpoints
@module tests
"""

import pytest
from starlette.testclient import TestClient
from backend.server import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Provides a TestClient instance for testing REST endpoints."""
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    """Tests that /api/v1/health returns HTTP 200 OK and valid status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "orto-gec-engine"


def test_analyze_endpoint_sva(client: TestClient) -> None:
    """Tests /api/v1/analyze with an SVA error input."""
    payload = {
        "text": "The box of old vintage vinyl records were dropped by the movers.",
        "options": {
            "enable_critic": True,
            "max_refinements": 1,
            "model": "gpt-4o-mini",
        },
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["original_text"] == payload["text"]
    assert "was dropped" in data["corrected_text"]
    assert len(data["edits"]) >= 1
    assert data["edits"][0]["errant_type"] == "R:VERB:SVA"
    assert data["telemetry"]["latency_ms"] > 0
    assert "X-RateLimit-Limit" in response.headers


def test_analyze_endpoint_clean_text(client: TestClient) -> None:
    """Tests /api/v1/analyze with clean input."""
    payload = {
        "text": "The students are studying in the library.",
        "options": {"enable_critic": True},
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["original_text"] == data["corrected_text"]


def test_humanize_endpoint(client: TestClient) -> None:
    """Tests /api/v1/style/humanize de-clichés synthetic text and computes burstiness."""
    payload = {
        "text": "Delving deep into the tapestry of knowledge is a testament to growth."
    }
    response = client.post("/api/v1/style/humanize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "humanized_text" in data
    assert "stylometry" in data
    assert "burstiness_score" in data["stylometry"]["report"]

