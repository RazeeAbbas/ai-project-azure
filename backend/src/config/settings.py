# ------------------------------------------ #
# AI Knowledge Copilot - Settings              #
# ------------------------------------------ #

"""
Application settings using Pydantic Settings.

All configuration is loaded from environment variables.
No secrets should be hardcoded.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ------------------------------------------ #
    # Application General
    # ------------------------------------------ #
    APP_NAME: str = "AI Knowledge Copilot"
    APP_ENVIRONMENT: str = Field(default="development", env="APP_ENVIRONMENT")
    APP_DEBUG: bool = Field(default=False, env="APP_DEBUG")
    APP_LOG_LEVEL: str = Field(default="INFO", env="APP_LOG_LEVEL")
    
    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000", env="CORS_ORIGINS")
    
    # ------------------------------------------ #
    # Azure OpenAI
    # ------------------------------------------ #
    AZURE_OPENAI_ENDPOINT: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str = Field(..., env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT: str = Field(default="gpt-4o-mini", env="AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-10-01", env="AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = Field(default="text-embedding-ada-002", env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    
    # RAG Parameters
    RAG_TOP_K: int = Field(default=5, env="RAG_TOP_K")
    RAG_SCORE_THRESHOLD: float = Field(default=0.7, env="RAG_SCORE_THRESHOLD")
    RAG_MAX_CONTEXT_TOKENS: int = Field(default=2000, env="RAG_MAX_CONTEXT_TOKENS")
    RAG_TEMPERATURE: float = Field(default=0.3, env="RAG_TEMPERATURE")
    ENABLE_FALLBACK_RESPONSE: bool = Field(default=True, env="ENABLE_FALLBACK_RESPONSE")
    
    # ------------------------------------------ #
    # Database (PostgreSQL)
    # ------------------------------------------ #
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_HOST: str = Field(default="localhost", env="DATABASE_HOST")
    DATABASE_PORT: int = Field(default=5432, env="DATABASE_PORT")
    DATABASE_NAME: str = Field(default="kicopilot", env="DATABASE_NAME")
    DATABASE_USERNAME: str = Field(default="postgres", env="DATABASE_USERNAME")
    DATABASE_PASSWORD: str = Field(default="postgres", env="DATABASE_PASSWORD")
    
    # ------------------------------------------ #
    # Vector Store (Azure AI Search)
    # ------------------------------------------ #
    AZURE_SEARCH_ENDPOINT: str = Field(default="", env="AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY: str = Field(default="", env="AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX: str = Field(default="kicopilot-index", env="AZURE_SEARCH_INDEX")
    AZURE_SEARCH_FIELD_ID: str = Field(default="id", env="AZURE_SEARCH_FIELD_ID")
    AZURE_SEARCH_FIELD_CONTENT: str = Field(default="content", env="AZURE_SEARCH_FIELD_CONTENT")
    AZURE_SEARCH_FIELD_CONTENTVECTOR: str = Field(default="contentVector", env="AZURE_SEARCH_FIELD_CONTENTVECTOR")
    AZURE_SEARCH_FIELD_METADATA: str = Field(default="metadata", env="AZURE_SEARCH_FIELD_METADATA")
    
    # Embedding configuration for vector store
    EMBEDDING_DIMENSION: int = Field(default=1536, env="EMBEDDING_DIMENSION")
    
    # ------------------------------------------ #
    # Blob Storage (Azure)
    # ------------------------------------------ #
    AZURE_STORAGE_ACCOUNT_NAME: str = Field(default="", env="AZURE_STORAGE_ACCOUNT_NAME")
    AZURE_STORAGE_CONNECTION_STRING: str = Field(default="", env="AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER: str = Field(default="documents", env="AZURE_STORAGE_CONTAINER")
    
    # ------------------------------------------ #
    # Redis (Caching & Queue)
    # ------------------------------------------ #
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field(default="", env="REDIS_PASSWORD")
    
    # ------------------------------------------ #
    # Authentication (JWT)
    # ------------------------------------------ #
    JWT_SECRET_KEY: str = Field(default="", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_MINUTES: int = Field(default=60, env="JWT_EXPIRATION_MINUTES")
    
    # ------------------------------------------ #
    # Feature Flags
    # ------------------------------------------ #
    ENABLE_RAG: bool = Field(default=True, env="ENABLE_RAG")
    ENABLE_DOCUMENT_UPLOAD: bool = Field(default=True, env="ENABLE_DOCUMENT_UPLOAD")
    ENABLE_CHAT: bool = Field(default=True, env="ENABLE_CHAT")
    
    # ------------------------------------------ #
    # Monitoring
    # ------------------------------------------ #
    AZURE_MONITORING_INSTRUMENTATION_KEY: str = Field(default="", env="AZURE_MONITORING_INSTRUMENTATION_KEY")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    
    # ------------------------------------------ #
    # Build/Pipeline metadata
    # ------------------------------------------ #
    BUILD_VERSION: str = Field(default="dev", env="BUILD_VERSION")
    BUILD_COMMIT: str = Field(default="unknown", env="BUILD_COMMIT")
    BUILD_TIMESTAMP: str = Field(default="", env="BUILD_TIMESTAMP")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()


def get_version_info() -> dict:
    """Get build version information."""
    return {
        "version": settings.BUILD_VERSION,
        "commit": settings.BUILD_COMMIT,
        "timestamp": settings.BUILD_TIMESTAMP,
        "environment": settings.APP_ENVIRONMENT
    }
