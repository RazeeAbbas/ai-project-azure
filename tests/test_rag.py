"""
RAG functional test — validates RAG pipeline logic (unit-level, no live Azure).
"""
import pytest
import asyncio
import sys
import os

os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://placeholder.openai.azure.com/")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "placeholder")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("AZURE_SEARCH_ENDPOINT", "https://placeholder.search.windows.net")
os.environ.setdefault("AZURE_SEARCH_KEY", "placeholder")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.src.services.qa_service import QAConnector  # noqa: E402


@pytest.mark.asyncio
async def test_qa_connector_creates():
    """QAConnector should initialise without error."""
    connector = QAConnector()
    assert connector is not None


@pytest.mark.asyncio
async def test_fallback_when_not_configured():
    """When Azure OpenAI is not configured, connector should return fallback."""
    connector = QAConnector()
    connector.is_configured = False
    result = await connector.ask_question("What is DevOps?")
    assert result is not None
    assert result.answer  # should have some content


@pytest.mark.asyncio
async def test_text_chunking():
    """Chunking logic should split a long document into chunks."""
    from backend.src.services.document_service import DocumentService
    svc = DocumentService()
    # Simulate chunking a 5000-char text
    text = "Azure is a cloud platform. " * 200  # ~5400 chars
    chunks = svc._chunk_text(text, chunk_size=1000, chunk_overlap=200)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk["content"]) <= 1500  # reasonable size
        assert "id" in chunk
        assert "content" in chunk

