# ------------------------------------------ #
# AI Knowledge Copilot - Database Service      #
# ------------------------------------------ #

"""
PostgreSQL database service for document metadata.
Uses asyncpg for async database operations.
"""

import json
import uuid
import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from src.config.settings import settings

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
    async with db_connection() as conn:
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
        async with db_connection() as conn:
            await conn.fetch("SELECT 1")
        return "healthy"
    except Exception as e:
        return f"error: {str(e)}"


async def create_document(
    title: str,
    file_name: str,
    content_type: str,
    file_size: int,
    blob_url: str,
    content: bytes = None,
) -> Dict[str, Any]:
    """Create a document record and return the stored row."""
    document_id = f"doc_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)
    async with db_connection() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO documents (
                id, title, file_name, content_type, file_size, blob_url, content,
                status, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending', $8, $8)
            RETURNING id, title, file_name, content_type, file_size, blob_url,
                      content, status, chunk_count, created_at, updated_at
            """,
            document_id,
            title,
            file_name,
            content_type,
            file_size,
            blob_url,
            content,
            now,
        )
    return dict(row)


async def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    """Get a document record, including content needed for ingestion."""
    async with db_connection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM documents WHERE id = $1",
            document_id,
        )
    return dict(row) if row else None


async def list_documents(
    status: Optional[str] = None,
    content_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List documents with optional status and content-type filters."""
    conditions = []
    params = []
    if status:
        params.append(status)
        conditions.append(f"status = ${len(params)}")
    if content_type:
        params.append(content_type)
        conditions.append(f"content_type = ${len(params)}")

    query = "SELECT * FROM documents"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY updated_at DESC"

    async with db_connection() as conn:
        rows = await conn.fetch(query, *params)
    return [dict(row) for row in rows]


async def update_document_status(document_id: str, status: str) -> bool:
    """Update document status and its modified timestamp."""
    async with db_connection() as conn:
        result = await conn.execute(
            "UPDATE documents SET status = $2, updated_at = NOW() WHERE id = $1",
            document_id,
            status,
        )
    return result.endswith(" 1")


async def create_chunks(document_id: str, chunks: List[Dict[str, Any]]) -> int:
    """Persist document chunks and update the document's chunk count."""
    async with db_connection() as conn:
        for chunk in chunks:
            await conn.execute(
                """
                INSERT INTO chunks (
                    id, document_id, content, chunk_index, chunk_size, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT (document_id, chunk_index) DO NOTHING
                """,
                chunk["id"],
                document_id,
                chunk["content"],
                chunk["chunk_index"],
                chunk["chunk_size"],
                json.dumps(chunk.get("metadata", {})),
            )
        await conn.execute(
            "UPDATE documents SET chunk_count = $2, updated_at = NOW() WHERE id = $1",
            document_id,
            len(chunks),
        )
    return len(chunks)


async def get_chunks_by_document(document_id: str) -> List[Dict[str, Any]]:
    """Get chunks for a document in chunk order."""
    async with db_connection() as conn:
        rows = await conn.fetch(
            "SELECT * FROM chunks WHERE document_id = $1 ORDER BY chunk_index",
            document_id,
        )
    return [dict(row) for row in rows]


async def delete_document_and_chunks(document_id: str) -> bool:
    """Delete a document; its chunks are removed by the foreign-key cascade."""
    async with db_connection() as conn:
        result = await conn.execute("DELETE FROM documents WHERE id = $1", document_id)
    return result.endswith(" 1")

