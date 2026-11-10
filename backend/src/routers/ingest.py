# ------------------------------------------ #
# AI Knowledge Copilot - Ingest Router         #
# ------------------------------------------ #

"""
Document ingestion router.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from src.schemas import IngestionRequest, ChunkInfo, ChunkListResponse
from src.services.document_service import DocumentService
from src.core.helpers import generate_request_id

router = APIRouter(prefix="/ingest", tags=["ingestion"])
logger = logging.getLogger(__name__)


def get_document_service() -> DocumentService:
    return DocumentService()


@router.post("/trigger")
async def trigger_ingestion(
    ingestion_request: IngestionRequest
):
    """
    Trigger ingestion of a document.
    
    This initiates the document processing pipeline:
    1. Extract text from document
    2. Split into chunks
    3. Generate embeddings
    4. Store in vector database
    """
    request_id = f"ingest-{ingestion_request.document_id}"
    logger.info(f"[{request_id}] Trigger Ingestion", extra={"request_id": request_id})
    
    try:
        document_service = get_document_service()
        result = await document_service.ingest_document(
            document_id=ingestion_request.document_id,
            chunk_size=ingestion_request.chunk_size,
            chunk_overlap=ingestion_request.chunk_overlap,
            include_metadata=ingestion_request.include_metadata
        )
        
        logger.info(f"[{request_id}] Ingestion triggered successfully", extra={"request_id": request_id})
        
        return {
            "message": "Ingestion triggered successfully",
            "document_id": ingestion_request.document_id,
            "result": result
        }
    
    except Exception as e:
        logger.error(f"[{request_id}] Ingestion failed: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/chunks", response_model=ChunkListResponse)
async def list_chunks(
    document_id: Optional[str] = Query(None, description="Filter by document ID")
):
    """
    List all chunks in the vector store.
    
    Returns chunk information with indexes and metadata.
    """
    request_id = generate_request_id()
    logger.info(f"[{request_id}] List Chunks Request: document_id={document_id}", extra={"request_id": request_id})
    
    try:
        document_service = get_document_service()
        chunks = await document_service.list_chunks(document_id=document_id)
        return {
            "chunks": chunks,
            "total": len(chunks)
        }
    except Exception as e:
        logger.error(f"[{request_id}] Error listing chunks: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Failed to list chunks: {str(e)}")


@router.get("/chunks/{chunk_id}")
async def get_chunk(chunk_id: str):
    """
    Get a specific chunk by ID.
    """
    request_id = f"chunk-{chunk_id}"
    logger.info(f"[{request_id}] Get Chunk Request", extra={"request_id": request_id})
    
    try:
        document_service = get_document_service()
        chunk = await document_service.get_chunk(chunk_id)
        
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        return chunk
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error getting chunk: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Failed to get chunk: {str(e)}")
