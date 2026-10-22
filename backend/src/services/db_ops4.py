
async def delete_document_and_chunks(document_id: str) -> bool:
    """Delete a document and all its chunks."""
    async with await get_pool() as conn:
        result1 = await conn.execute("DELETE FROM chunks WHERE document_id = $1", document_id)
        result2 = await conn.execute("DELETE FROM documents WHERE id = $1", document_id)
        
        deleted_chunks = int(result1.split()[1]) if result1 else 0
        return deleted_chunks > 0 or result2 == "DELETE 1"


# Conversation operations
async def create_conversation(messages: List[Dict[str, Any]] = None) -> str:
    """Create a new conversation."""
    async with await get_pool() as conn:
        conversation_id = f"conv_{os.urandom(12).hex()}"
        now = get_current_timestamp()
        
        if messages is None:
            messages = []
        
        await conn.execute("""
            INSERT INTO conversations (id, messages, created_at, updated_at)
            VALUES ($1, $2, $3, $4)
        """, conversation_id, messages, now, now)
        
        return conversation_id


async def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get conversation by ID."""
    async with await get_pool() as conn:
        row = await conn.fetchrow("""
            SELECT id, messages, created_at, updated_at
            FROM conversations
            WHERE id = $1
        """, conversation_id)
        
        if row:
            return dict(row)
        return None


async def update_conversation(conversation_id: str, messages: List[Dict[str, Any]]) -> bool:
    """Update conversation messages."""
    async with await get_pool() as conn:
        result = await conn.execute("""
            UPDATE conversations SET messages = $2, updated_at = NOW() WHERE id = $1
        """, conversation_id, messages)
        return result == "UPDATE"
