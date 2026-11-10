# ------------------------------------------ #
# AI Knowledge Copilot - Document Router       #
# (Part 1 - Setup and Upload)                   #
# ------------------------------------------ #

"""
Document management router.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import tempfile
import aiofiles
import logging

from src.schemas import DocumentUploadRequest, DocumentResponse
from src.services.document_service import DocumentService
from src.services.storage_service import StorageService
from src.core.helpers import generate_request_id

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

# Dependency for document service
def get_document_service() -> DocumentService:
    return DocumentService()


@router.post("", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    title: Optional[str] = Query(None, description="Document title (defaults to file name)"),
    document_type: Optional[str] = Query(None, description="Document type")
):
    """
    Upload a document for ingestion.
    
    The document is stored in Azure Blob Storage.
    The ingestion process is triggered asynchronously.
    """
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Upload Document Request: {file.filename}", extra={"request_id": request_id})
    
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is required")
        
        # Read file content
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Determine content type
        content_type = document_type or file.content_type or "application/octet-stream"
        
        # Save to temporary file for subsequent processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.rsplit('.', 1)[-1]}") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Upload to storage
        storage_service = StorageService()
        blob_url = await storage_service.upload_document(
            file_path=tmp_path,
            file_name=file.filename,
            content_type=content_type
        )
        
        # Create document record
        document_service = get_document_service()
        document = await document_service.create_document(
            title=title or file.filename,
            file_name=file.filename,
            content_type=content_type,
            file_size=len(content),
            blob_url=blob_url,
            content=content
        )
        
        # Trigger ingestion
        await document_service.ingest_document(document.id)
        document = await document_service.get_document(document.id) or document
        
        logger.info(f"[{request_id}] Document uploaded successfully: {document.id}", extra={"request_id": request_id})
        
        return document
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error uploading document: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
