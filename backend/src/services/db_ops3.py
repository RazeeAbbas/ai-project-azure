
# Chunk operations
async def create_chunks(
    document_id: str,
    chunks: List[Dict[str, Any]]
) -> int:
    """Create multiple chunks for a document."""
    async with await get_pool() as conn:
        inserted = 0
        for chunk_data in chunks:
            chunk_id = chunk_data.pop("id", f"chunk_{os.urandom(8).hex()}")
            chunk_data["document_id"] = document_id
            chunk_data["created_at"] = get_current_timestamp()
            
            await conn.execute("""
                INSERT INTO chunks (
                    id, document_id, content, chunk_index, chunk_size, metadata, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (document_id, chunk_index) DO NOTHING
            """, chunk_id, document_id, chunk_data["content"], 
               chunk_data["chunk_index"], chunk_data["chunk_size"],
               chunk_data["metadata"], chunk_data["created_at"])
            inserted += 1
    
    return inserted


async def get_chunks_by_document(document_id: str) -> List[Dict[str, Any]]:
    """Get all chunks for a document."""
    async with await get_pool() as conn:
        rows = await conn.fetch("""
            SELECT id, document_id, content, chunk_index, chunk_size, metadata, created_at
            FROM chunks
            WHERE document_id = $1
            ORDER BY chunk_index
        """, document_id)
        return [dict(row) for row in rows]


async def get_chunk(chunk_id: str) -> Optional[Dict[str, Any]]:
    """Get a chunk by ID."""
    async with await get_pool() as conn:
        row = await conn.fetchrow("""
            SELECT id, document_id, content, chunk_index, chunk_size, metadata, created_at
            FROM chunks
            WHERE id = $1
        """, chunk_id)
        
        if row:
            return dict(row)
        return None
