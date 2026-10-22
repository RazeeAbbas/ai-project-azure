"""
Missing helpers that are imported from src.core.helpers
"""

import uuid
from datetime import datetime, timezone


def generate_request_id() -> str:
    """Generate a short unique request ID."""
    return str(uuid.uuid4())[:8]


def generate_document_id() -> str:
    """Generate a unique document ID."""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)

