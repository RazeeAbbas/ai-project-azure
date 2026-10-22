# ------------------------------------------ #
# AI Knowledge Copilot - Backend              #
# ------------------------------------------ #
# FastAPI backend with RAG capabilities      #
# Built for Azure AI Knowledge Copilot project #
# ------------------------------------------ #

"""
AI Knowledge Copilot - Backend API

This backend provides:
- Document ingestion endpoint (upload, chunk, embed, store)
- Question/answer endpoint (RAG with grounding)
- Health check endpoint
- Structured logging
- Configuration via environment variables
"""

# Root directory for the project
import os
import sys
from pathlib import Path

# Add src to path for local development
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

from src.config.settings import settings
from src.routers import health, documents, questions, ingest
from src.core.logging import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Gauge(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)
ACTIVE_CONNECTIONS = Gauge(
    "app_active_connections",
    "Active connections"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting AI Knowledge Copilot backend")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Azure OpenAI Endpoint: {settings.AZURE_OPENAI_ENDPOINT[:15]}...{settings.AZURE_OPENAI_ENDPOINT[-10:]}")
    logger.info(f"Database: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}")
    
    # Check required configuration
    missing_vars = []
    if not settings.AZURE_OPENAI_ENDPOINT or settings.AZURE_OPENAI_ENDPOINT == "https://your-resource.openai.azure.com/":
        missing_vars.append("AZURE_OPENAI_ENDPOINT")
    if not settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_API_KEY == "your-api-key":
        missing_vars.append("AZURE_OPENAI_API_KEY")
    
    if missing_vars:
        logger.warning(f"Missing configuration: {', '.join(missing_vars)}")
        logger.warning("AI/RAG features will be disabled in production")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Knowledge Copilot backend")

app = FastAPI(
    title="AI Knowledge Copilot API",
    description="Backend API with RAG capabilities for knowledge management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

# Health endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with dependency status."""
    status = {
        "status": "healthy",
        "service": "ai-knowledge-copilot",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check Azure OpenAI connectivity
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
        status["checks"]["azure_openai"] = "configured"
    else:
        status["checks"]["azure_openai"] = "not_configured"
    
    # Check database connectivity
    try:
        from src.services.db_service import check_database_connection
        db_status = await check_database_connection()
        status["checks"]["database"] = db_status
    except Exception as e:
        status["checks"]["database"] = f"error: {str(e)}"
    
    # Check Redis connectivity
    try:
        from src.services.redis_service import ping_redis
        redis_status = await ping_redis()
        status["checks"]["redis"] = redis_status
    except Exception as e:
        status["checks"]["redis"] = f"warn: {str(e)}"
    
    # Check vector store connectivity
    try:
        from src.services.vector_service import check_vector_store_connection
        vector_status = await check_vector_store_connection()
        status["checks"]["vector_store"] = vector_status
    except Exception as e:
        status["checks"]["vector_store"] = f"warn: {str(e)}"
    
    # Check document storage connectivity
    try:
        from src.services.storage_service import check_storage_connection
        storage_status = await check_storage_connection()
        status["checks"]["storage"] = storage_status
    except Exception as e:
        status["checks"]["storage"] = f"warn: {str(e)}"
    
    # Determine overall status
    all_checks = status["checks"]
    if all(v == "healthy" or v == "configured" for v in all_checks.values()):
        status["status"] = "healthy"
    elif any(v == "error" or v.startswith("error") for v in all_checks.values()):
        status["status"] = "degraded"
    else:
        status["status"] = "partial"
    
    request_id = {"request_id": "n/a"}
    status.update(request_id)
    
    return status

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingestion"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown complete")
