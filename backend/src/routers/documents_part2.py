# ------------------------------------------ #
# AI Knowledge Copilot - Document Router       #
# (Part 2 - List, Get, Delete)                  #
# ------------------------------------------ #

"""
Document management router - continued.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import Optional, List
import logging

from src.schemas import DocumentResponse
from src.services.document_service import DocumentService
from src.services.storage_service import StorageService
from src.core.helpers import generate_request_id

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

def get_document_service() -> DocumentService:
    return DocumentService()


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    status: Optional[str] = Query(None, description="Filter by status"),
    content_type: Optional[str] = Query(None, description="Filter by content type")
):
    """List all documents with optional filtering."""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] List Documents Request: status={status}, content_type={content_type}", extra={"request_id": request_id})
    
    try:
        document_service = get_document_service()
        documents = await document_service.list_documents(
            status=status,
            content_type=content_type
        )
        return documents
    except Exception as e:
        logger.error(f"[{request_id}] Error listing documents: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document by ID."""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Get Document Request: {document_id}", extra={"request_id": request_id})
    
    try:
        document_service = get_document_service()
        document = await document_service.get_document(document_id)
        if not document:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error getting document: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its associated chunks."""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Delete Document Request: {document_id}", extra={"request_id": request_id})
    
    try:
        document_service = get_document_service()
        deleted = await document_service.delete_document(document_id)
        
        if not deleted:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"[{request_id}] Document deleted successfully: {document_id}", extra={"request_id": request_id})
        return {"message": "Document deleted successfully", "id": document_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error deleting document: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
