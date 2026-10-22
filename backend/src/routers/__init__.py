"""
__init__.py  - re-export routers so main.py can do:
  from src.routers import health, documents, questions, ingest
"""
from src.routers import health, documents_part1 as documents, questions, ingest

__all__ = ["health", "documents", "questions", "ingest"]

