# ------------------------------------------ #
# AI Knowledge Copilot - Question Router       #
# ------------------------------------------ #

"""
Question/Answer router with RAG capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging

from src.schemas import QuestionRequest, RAGResponse
from src.services.qa_service import QAConnector

router = APIRouter(prefix="/questions", tags=["questions"])
logger = logging.getLogger(__name__)


def get_qa_connector() -> QAConnector:
    return QAConnector()


@router.post("", response_model=RAGResponse)
async def ask_question(
    question_request: QuestionRequest,
    qa_connector: QAConnector = Depends(get_qa_connector)
):
    """
    Ask a question using RAG (Retrieval Augmented Generation).
    
    The RAG flow:
    1. Retrieve relevant document chunks based on the question
    2. Construct prompts with retrieved context
    3. Generate grounded answer using Azure OpenAI
    4. Return answer with source references
    
    If the knowledge base doesn't contain enough information,
    the system returns a controlled response stating that
    the answer cannot be grounded in the available documents.
    """
    request_id = f"qa-{question_request.question[:20]}..."  # Truncated for logging
    logger.info(f"[{request_id}] Question Request: {question_request.question[:100]}...", 
                extra={"request_id": request_id})
    
    try:
        # Validate that RAG is enabled
        if not qa_connector.rag_enabled:
            raise HTTPException(
                status_code=503, 
                detail="RAG service is currently unavailable. Please try again later."
            )
        
        # Execute question with RAG
        result = await qa_connector.ask_question(
            question=question_request.question,
            conversation_id=question_request.conversation_id
        )
        
        logger.info(f"[{request_id}] Question answered successfully", 
                    extra={"request_id": request_id, "conversation_id": result.conversation_id})
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error processing question: {str(e)}", 
                     exc_info=True, extra={"request_id": request_id})
        raise HTTPException(
            status_code=500, 
            detail="Failed to process question. Please try again later."
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    qa_connector: QAConnector = Depends(get_qa_connector)
):
    """
    Get conversation history by conversation ID.
    """
    try:
        result = await qa_connector.get_conversation(conversation_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}", 
                     exc_info=True, extra={"request_id": f"conv-{conversation_id}"})
        raise HTTPException(status_code=500, detail="Failed to get conversation")


@router.post("/conversations")
async def create_conversation(
    qa_connector: QAConnector = Depends(get_qa_connector)
):
    """
    Create a new conversation thread.
    """
    try:
        conversation_id = await qa_connector.create_conversation()
        
        return {
            "conversation_id": conversation_id,
            "message": "Conversation created successfully"
        }
    
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}", 
                     exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create conversation")
