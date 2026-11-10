# ------------------------------------------ #
# AI Knowledge Copilot - Health Router         #
# ------------------------------------------ #

"""
Health check and readiness probes router.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.config.settings import settings, get_version_info
from src.core.helpers import get_current_timestamp

from src.services.db_service import check_database_connection
from src.services.redis_service import ping_redis
from src.services.vector_service import check_vector_store_connection
from src.services.storage_service import check_storage_connection

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    checks: Dict[str, Any]
    build_info: Optional[Dict[str, str]] = None
    timestamp: str


@router.get("")
async def read_health():
    """
    Health check endpoint.
    
    Returns service health status including:
    - Service status
    - Configuration status
    - Dependency connectivity
    """
    status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "checks": {},
        "build_info": get_version_info(),
        "timestamp": get_current_timestamp().isoformat()
    }
    
    # Check Azure OpenAI
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
        status["checks"]["azure_openai"] = "configured"
        status["checks"]["openai_config"] = {
            "endpoint_configured": True,
            "deployment": settings.AZURE_OPENAI_DEPLOYMENT,
            "api_version": settings.AZURE_OPENAI_API_VERSION
        }
    else:
        status["checks"]["azure_openai"] = "not_configured"
    
    # Check database
    try:
        db_status = await check_database_connection()
        status["checks"]["database"] = db_status
    except Exception as e:
        status["checks"]["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        redis_status = await ping_redis()
        status["checks"]["redis"] = redis_status
    except Exception as e:
        status["checks"]["redis"] = f"warn: {str(e)}"
    
    # Check vector store
    try:
        vector_status = await check_vector_store_connection()
        status["checks"]["vector_store"] = vector_status
    except Exception as e:
        status["checks"]["vector_store"] = f"warn: {str(e)}"
    
    # Check storage
    try:
        storage_status = await check_storage_connection()
        status["checks"]["storage"] = storage_status
    except Exception as e:
        status["checks"]["storage"] = f"warn: {str(e)}"
    
    # Determine overall status
    check_values = [
        value for key, value in status["checks"].items()
        if key != "openai_config"
    ]

    if any(isinstance(value, str) and value.startswith("error") for value in check_values):
        status["status"] = "degraded"
    elif all(value in {"healthy", "configured"} for value in check_values):
        status["status"] = "healthy"
    else:
        status["status"] = "partial"
    
    return HealthStatus(**status)


@router.get("/ready")
async def read_ready():
    """
    Readiness probe endpoint.
    
    Used by Kubernetes for deployment readiness.
    Returns 200 when the service is ready to accept traffic.
    """
    health = await read_health()
    checks = health.checks
    if checks.get("database") != "healthy":
        raise HTTPException(status_code=503, detail={"status": "not_ready", "checks": checks})

    return {"status": "ready", "checks": checks}
