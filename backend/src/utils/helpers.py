# ------------------------------------------ #
# AI Knowledge Copilot - Core Utilities        #
# ------------------------------------------ #

"""
Core utility functions for the AI Knowledge Copilot backend.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum


class ContentType(Enum):
    """Supported document content types."""
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    TXT = "text/plain"
    MD = "text/markdown"
    HTML = "text/html"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    JSON = "application/json"


class ErrorCode(Enum):
    """Standard error codes for API responses."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    VECTOR_STORE_ERROR = "VECTOR_STORE_ERROR"
    DOCUMENT_PROCESSING_ERROR = "DOCUMENT_PROCESSING_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def generate_document_id() -> str:
    """Generate a unique document ID."""
    return str(uuid.uuid4())


def generate_chunk_id() -> str:
    """Generate a unique chunk ID."""
    return str(uuid.uuid4())


def generate_sha256(content: bytes) -> str:
    """Generate SHA256 hash of content."""
    return hashlib.sha256(content).hexdigest()


def generate_slug(title: str, max_length: int = 50) -> str:
    """Generate a URL-friendly slug from a title."""
    import re
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Truncate to max length
    slug = slug[:max_length]
    return slug


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get an environment variable."""
    value = os.getenv(name, default)
    if value is None or value == "":
        return default
    return value


def mask_sensitive_data(data: dict, sensitive_fields: list = None) -> dict:
    """Mask sensitive fields in a dictionary for logging."""
    if sensitive_fields is None:
        sensitive_fields = ["password", "secret", "token", "key", "api_key"]
    
    masked = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            masked[key] = "***"
        else:
            masked[key] = value
    
    return masked


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize and truncate text for logging."""
    if not text:
        return ""
    
    # Replace newlines with spaces
    text = text.replace("\n", " ").replace("\r", " ")
    # Truncate
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def calculate_sha256(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()
