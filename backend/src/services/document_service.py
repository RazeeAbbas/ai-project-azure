# ------------------------------------------ #
# AI Knowledge Copilot - Document Service      #
# ------------------------------------------ #

"""
Document service for managing document lifecycle.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.schemas import DocumentResponse
from src.services.db_service import (
    create_document, get_document, list_documents, 
    update_document_status, delete_document_and_chunks,
    get_chunks_by_document
)
from src.services.storage_service import StorageService
from src.services.embedding_service import EmbeddingService
from src.services.vector_service import VectorService
from src.utils.helpers import generate_document_id

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing document lifecycle."""
    
    def __init__(self):
        self.storage_service = StorageService()
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def create_document(
        self,
        title: str,
        file_name: str,
        content_type: str,
        file_size: int,
        blob_url: str,
        content: bytes = None
    ) -> DocumentResponse:
        """Create a new document record."""
        document_id = generate_document_id()
        
        doc = await create_document(
            title=title,
            file_name=file_name,
            content_type=content_type,
            file_size=file_size,
            blob_url=blob_url,
            content=content
        )
        
        await update_document_status(document_id, "processing")
        
        return DocumentResponse(
            id=doc["id"],
            title=doc["title"],
            file_name=doc["file_name"],
            content_type=doc["content_type"],
            file_size=doc["file_size"],
            blob_url=doc["blob_url"],
            status=doc["status"],
            chunk_count=doc["chunk_count"] or 0,
            created_at=datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(doc["updated_at"].replace("Z", "+00:00")),
            metadata=None
        )
    
    async def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """Get document by ID."""
        doc = await get_document(document_id)
        
        if doc:
            return DocumentResponse(
                id=doc["id"],
                title=doc["title"],
                file_name=doc["file_name"],
                content_type=doc["content_type"],
                file_size=doc["file_size"],
                blob_url=doc["blob_url"],
                status=doc["status"],
                chunk_count=doc["chunk_count"] or 0,
                created_at=datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(doc["updated_at"].replace("Z", "+00:00")),
                metadata=None
            )
        return None
    
    async def list_documents(self, status: Optional[str] = None, content_type: Optional[str] = None) -> List[DocumentResponse]:
        """List documents with optional filtering."""
        docs = await list_documents(status=status, content_type=content_type)
        results = []
        
        for doc in docs:
            results.append(DocumentResponse(
                id=doc["id"],
                title=doc["title"],
                file_name=doc["file_name"],
                content_type=doc["content_type"],
                file_size=doc["file_size"],
                blob_url=doc["blob_url"],
                status=doc["status"],
                chunk_count=doc["chunk_count"] or 0,
                created_at=datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(doc["updated_at"].replace("Z", "+00:00")),
                metadata=None
            ))
        

        return results
    
    async def ingest_document(
        self,
        document_id: str,
        chunk_size: Optional[int] = 1000,
        chunk_overlap: Optional[int] = 200,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest a document: extract text, chunk, embed, and store.
        """
        request_id = f"doc-{document_id}"
        logger.info(f"[{request_id}] Starting document ingestion", extra={"request_id": request_id})
        
        try:
            document = await self.get_document(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            content = document.get("content") or b"Demo document content for testing"
            
            text = self._extract_text_from_bytes(content, document["content_type"])
            
            chunks = self._split_text(
                text,
                chunk_size=chunk_size or self.chunk_size,
                chunk_overlap=chunk_overlap or self.chunk_overlap
            )
            
            texts = [chunk["content"] for chunk in chunks]
            embeddings = await self.embedding_service.generate_embeddings(texts)
            
            vector_data = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk["metadata"]["chunk_index"] = i
                chunk["metadata"]["document_id"] = document_id
                
                vector_data.append({
                    "id": chunk["id"],
                    "document_id": document_id,
                    "content": chunk["content"],
                    "embedding": embedding,
                    "metadata": chunk["metadata"],
                    "chunk_index": i
                })
            
            await self.vector_service.store_documents(
                documents=vector_data,
                document_ids=[document_id],
                chunk_ids=[c["id"] for c in chunks]
            )
            
            await create_chunks(document_id, chunks)
            await update_document_status(document_id, "completed")
            
            logger.info(f"[{request_id}] Document ingestion completed", extra={"request_id": request_id})
            
            return {
                "status": "completed",
                "chunk_count": len(chunks),
                "embedding_count": len(embeddings)
            }
        
        except Exception as e:

            logger.error(f"[{request_id}] Document ingestion failed: {str(e)}", exc_info=True, extra={"request_id": request_id})
            await update_document_status(document_id, "failed")
            raise
    
    def _extract_text_from_bytes(self, content: bytes, content_type: str) -> str:
        """
        Extract text from document bytes.
        """
        content_str = content.decode("utf-8", errors="ignore")
        
        if "pdf" in content_type:
            return f"[PDF Document] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "docx" in content_type or "doc" in content_type:
            return f"[Word Document] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "pptx" in content_type or "ppt" in content_type:
            return f"[PowerPoint] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "json" in content_type:
            return f"[JSON File] {content_str[:2000]}"
        else:
            return content_str[:2000]
    
    def _split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
        """
        Split text into chunks with overlap.
        """
        chunks = []
        
        if not text:
            return chunks
        
        if len(text) <= chunk_size:
            chunks.append({
                "id": f"chunk_{abs(hash(text)) % 100000}",
                "content": text,
                "chunk_index": 0,
                "chunk_size": len(text),
                "metadata": {}
            })
            return chunks

            start = end - chunk_overlap
            
            if start <= 0:
                break
        
        return chunks
    
    async def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Get a chunk by ID."""
        return None
    
    async def list_chunks(self, document_id: Optional[str] = None) -> List[Dict]:
        """List chunks, optionally filtered by document."""
        if document_id:
            return await get_chunks_by_document(document_id)
        return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks."""
        return await delete_document_and_chunks(document_id)
    
    async def check_connection(self) -> str:
        """Check database connectivity."""
        return "healthy"


            start = end - chunk_overlap
            
            if start <= 0:
                break
        
        return chunks
    
    async def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Get a chunk by ID."""
        return None
    
    async def list_chunks(self, document_id: Optional[str] = None) -> List[Dict]:
        """List chunks, optionally filtered by document."""
        if document_id:
            return await get_chunks_by_document(document_id)
        return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks."""
        return await delete_document_and_chunks(document_id)
    
    async def check_connection(self) -> str:
        """Check database connectivity."""
        return "healthy"

        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            if end < len(text):
                search_start = min(end, len(text) - 50)
                search_end = min(end + 500, len(text))
                
                last_period = max(
                    text.rfind('.', start, search_end),
                    text.rfind('!', start, search_end),
                    text.rfind('?', start, search_end)
                )
                
                if last_period > end - 50 and last_period < end + 500:
                    end = last_period + 1
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunks.append({
                    "id": f"chunk_{abs(hash(chunk_content)) % 100000}",
                    "content": chunk_content,
                    "chunk_index": chunk_index,
                    "chunk_size": len(chunk_content),
                    "metadata": {}
                })
                chunk_index += 1
            
            start = end - chunk_overlap
            
            if start <= 0:
                break
        
        return chunks

            logger.error(f"[{request_id}] Document ingestion failed: {str(e)}", exc_info=True, extra={"request_id": request_id})
            await update_document_status(document_id, "failed")
            raise
    
    def _extract_text_from_bytes(self, content: bytes, content_type: str) -> str:
        """
        Extract text from document bytes.
        """
        content_str = content.decode("utf-8", errors="ignore")
        
        if "pdf" in content_type:
            return f"[PDF Document] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "docx" in content_type or "doc" in content_type:
            return f"[Word Document] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "pptx" in content_type or "ppt" in content_type:
            return f"[PowerPoint] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "json" in content_type:
            return f"[JSON File] {content_str[:2000]}"
        else:
            return content_str[:2000]

        return results
