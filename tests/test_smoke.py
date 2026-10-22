"""
Smoke test - runs after deployment to verify the deployed endpoint is healthy.
Usage: BACKEND_URL=https://... pytest tests/test_smoke.py
"""
import os
import requests
import pytest

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


def test_health_smoke():
    """Deployed health endpoint returns 200 with healthy-ish status."""
    resp = requests.get(f"{BACKEND_URL}/health", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") in ("healthy", "degraded", "partial")


def test_openapi_reachable():
    """OpenAPI schema is reachable on deployed service."""
    resp = requests.get(f"{BACKEND_URL}/openapi.json", timeout=10)
    assert resp.status_code == 200


def test_docs_reachable():
    """Swagger UI is reachable."""
    resp = requests.get(f"{BACKEND_URL}/docs", timeout=10)
    assert resp.status_code == 200

