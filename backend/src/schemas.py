# ------------------------------------------ #
# AI Knowledge Copilot - Schemas               #
# ------------------------------------------ #

"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "markdown"
    HTML = "html"
    POWERPOINT = "pptx"
    JSON = "json"


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    content_type: DocumentType = Field(..., description="Document content type")
    content: bytes = Field(..., description="Document content binary")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean title."""
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Title cannot be empty")
        if len(v) > 500:
            raise ValueError("Title cannot exceed 500 characters")
        return v


class DocumentResponse(BaseModel):
    """Response model for document info."""
    id: str
    title: str
    content_type: str
    file_name: Optional[str] = None
    size_bytes: int
    status: str  # pending, processing, completed, error, failed
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class IngestionRequest(BaseModel):
    """Request model for ingestion trigger."""
    document_id: str = Field(..., description="Document ID to ingest")
    chunk_size: Optional[int] = Field(default=1000, description="Target chunk size in characters")
    chunk_overlap: Optional[int] = Field(default=200, description="Chunk overlap in characters")
    include_metadata: Optional[bool] = Field(default=True, description="Include metadata in chunks")


class ChunkInfo(BaseModel):
    """Response model for a single chunk."""
    id: str
    document_id: str
    content: str
    chunk_index: int
    chunk_size: int
    parent_document_id: Optional[str] = None
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class ChunkListResponse(BaseModel):
    """Response model for list of chunks."""
    chunks: List[ChunkInfo]
    total: int


class QuestionRequest(BaseModel):
    """Request model for question."""
    question: str = Field(..., min_length=1, max_length=5000, description="Question to ask")
    conversation_id: Optional[str] = Field(default=None, description="Conversation thread ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    
    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate and clean question."""
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Question cannot be empty")
        if len(v) > 5000:
            raise ValueError("Question cannot exceed 5000 characters")
        return v


class SourceChunk(BaseModel):
    """Model for a retrieved source chunk."""
    id: str
    document_id: str
    content: str
    score: float
    title: Optional[str] = None
    source_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class RAGResponse(BaseModel):
    """Response model for RAG question/answer."""
    answer: str
    sources: List[SourceChunk]
    question: str
    conversation_id: Optional[str]
    retrieved_at: datetime
    grounding_score: float
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response model for conversation."""
    id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class TokenCount(BaseModel):
    """Model for token counts."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""
    texts: List[str] = Field(..., min_length=1, description="Texts to embed")
    model: Optional[str] = Field(default=None, description="Embedding model to use")


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""
    embeddings: List[List[float]]
    model: str
    usage: TokenCount


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    
    class Config:
        from_attributes = True
