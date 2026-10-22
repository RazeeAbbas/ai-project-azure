
# Document operations
async def create_document(
    title: str,
    file_name: str,
    content_type: str,
    file_size: int,
    blob_url: str,
    content: bytes = None
) -> Dict[str, Any]:
    """Create a new document record."""
    async with await get_pool() as conn:
        document_id = f"doc_{os.urandom(12).hex()}"
        now = get_current_timestamp()
        
        await conn.execute("""
            INSERT INTO documents (id, title, file_name, content_type, file_size, blob_url, content, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, document_id, title, file_name, content_type, file_size, blob_url, content, "pending", now, now)
        
        return {
            "id": document_id,
            "title": title,
            "file_name": file_name,
            "content_type": content_type,
            "file_size": file_size,
            "blob_url": blob_url,
            "status": "pending",
            "created_at": now,
            "updated_at": now
        }
