# ------------------------------------------ #
# AI Knowledge Copilot - Database Service      #
# ------------------------------------------ #

"""
PostgreSQL database service for document metadata.
Uses asyncpg for async database operations.
"""

import os
import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from src.config.settings import settings
from src.core.helpers import get_current_timestamp

# Connection pool
pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60,
            timeout=30
        )
    return pool


async def close_pool():
    """Close the database connection pool."""
    global pool
    if pool is not None:
        await pool.close()
        pool = None


@asynccontextmanager
async def db_connection():
    """Context manager for database connections."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn


async def init_database():
    """Initialize the database schema."""
    async with await get_pool() as conn:
        # Create documents table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR(64) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                file_name VARCHAR(500) NOT NULL,
                content_type VARCHAR(100) NOT NULL,
                file_size BIGINT NOT NULL,
                blob_url TEXT NOT NULL,
                content BYTEA,
                status VARCHAR(50) DEFAULT 'pending',
                chunk_count INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create chunks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id VARCHAR(64) PRIMARY KEY,
                document_id VARCHAR(64) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_size INTEGER NOT NULL,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE (document_id, chunk_index)
            )
        """)
        
        # Create conversations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR(64) PRIMARY KEY,
                messages JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_status 
            ON documents(status)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_content_type 
            ON documents(content_type)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document_id 
            ON chunks(document_id)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_content 
            ON chunks USING GIN (to_tsvector('english', content))
        """)
    
    return True


async def check_database_connection() -> str:
    """Check database connectivity."""
    try:
        async with await get_pool() as conn:
            await conn.fetch("SELECT 1")
        return "healthy"
    except Exception as e:
        return f"error: {str(e)}"

