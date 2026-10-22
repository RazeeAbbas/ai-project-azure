# ------------------------------------------ #
# AI Knowledge Copilot - Redis Service         #
# ------------------------------------------ #

"""
Redis caching service. Falls back gracefully when Redis is unavailable.
"""

import logging
from typing import Optional
from src.config.settings import settings

logger = logging.getLogger(__name__)

_redis_client = None


async def _get_client():
    """Get or create Redis client lazily."""
    global _redis_client
    if _redis_client is None:
        try:
            import aioredis
            _redis_client = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_connect_timeout=3,
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {e} — caching disabled")
            _redis_client = None
    return _redis_client


async def ping_redis() -> str:
    """Ping Redis; return 'healthy' or a warning string."""
    client = await _get_client()
    if client is None:
        return "warn: redis not configured"
    try:
        await client.ping()
        return "healthy"
    except Exception as e:
        return f"warn: {e}"


async def cache_get(key: str) -> Optional[str]:
    """Get a cached value."""
    client = await _get_client()
    if client is None:
        return None
    try:
        return await client.get(key)
    except Exception:
        return None


async def cache_set(key: str, value: str, ttl_seconds: int = 300) -> bool:
    """Set a cached value with TTL."""
    client = await _get_client()
    if client is None:
        return False
    try:
        await client.set(key, value, ex=ttl_seconds)
        return True
    except Exception:
        return False

