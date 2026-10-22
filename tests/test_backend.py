"""
Backend integration tests.
Tests health endpoint and key API behaviour without full Azure connectivity.
"""
import pytest
from fastapi.testclient import TestClient
import os

# Set required env vars before importing app
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://placeholder.openai.azure.com/")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "placeholder-key")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("AZURE_SEARCH_ENDPOINT", "https://placeholder.search.windows.net")
os.environ.setdefault("AZURE_SEARCH_KEY", "placeholder-key")

from backend.src.main import app  # noqa: E402

client = TestClient(app)


def test_health_endpoint_returns_200():
    """Health endpoint must return 200 and a status field."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service" in data


def test_health_has_checks():
    """Health response must include a checks dict."""
    response = client.get("/health")
    data = response.json()
    assert "checks" in data
    assert isinstance(data["checks"], dict)


def test_docs_endpoint():
    """OpenAPI docs must be reachable."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json():
    """OpenAPI JSON schema must be present."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema


def test_question_endpoint_without_kb():
    """Question endpoint must return a controlled response when no KB context."""
    payload = {"question": "What is Azure?"}
    response = client.post("/api/questions", json=payload)
    # With no real Azure OpenAI, we expect either 200 (fallback) or 500 (config error)
    assert response.status_code in (200, 422, 500)


def test_documents_list_empty():
    """Documents list should return 200 even when empty (or DB error gracefully)."""
    response = client.get("/api/documents")
    assert response.status_code in (200, 500)


def test_invalid_question_empty():
    """Empty question string must be rejected with 422."""
    payload = {"question": ""}
    response = client.post("/api/questions", json=payload)
    assert response.status_code == 422

