
async def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    """Get a document by ID."""
    async with await get_pool() as conn:
        row = await conn.fetchrow("""
            SELECT id, title, file_name, content_type, file_size, blob_url, status, chunk_count, created_at, updated_at
            FROM documents
            WHERE id = $1
        """, document_id)
        
        if row:
            return dict(row)
        return None


async def list_documents(status: Optional[str] = None, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """List documents with optional filtering."""
    async with await get_pool() as conn:
        query = "SELECT id, title, file_name, content_type, file_size, status, chunk_count, created_at, updated_at FROM documents WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = $1"
            params.append(status)
        
        if content_type:
            query += " AND content_type = $2"
            params.append(content_type)
        
        query += " ORDER BY updated_at DESC"
        
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


async def update_document_status(document_id: str, status: str) -> bool:
    """Update document status."""
    async with await get_pool() as conn:
        result = await conn.execute("""
            UPDATE documents SET status = $2, updated_at = NOW() WHERE id = $1
        """, document_id, status)
        return result == "UPDATE"


async def get_document_by_blob_url(blob_url: str) -> Optional[Dict[str, Any]]:
    """Get document by blob URL."""
    async with await get_pool() as conn:
        row = await conn.fetchrow("""
            SELECT id, title, file_name, content_type, file_size, blob_url, status, chunk_count, created_at, updated_at
            FROM documents
            WHERE blob_url = $1
        """, blob_url)
        
        if row:
            return dict(row)
        return None
