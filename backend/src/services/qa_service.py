# ------------------------------------------ #
# AI Knowledge Copilot - QA Service            #
# ------------------------------------------ #

"""
Question/Answer service with RAG capabilities.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.config.settings import settings

logger = logging.getLogger(__name__)


class SourceChunk:
    """A source chunk retrieved for answering a question."""
    def __init__(self, id: str, document_id: str, content: str, score: float, title: str = None):
        self.id = id
        self.document_id = document_id
        self.content = content
        self.score = score
        self.title = title


class RAGResult:
    """Result from a RAG question."""
    def __init__(self, answer: str, sources: List[SourceChunk], question: str, conversation_id: str, retrieved_at: str, grounding_score: float):
        self.answer = answer
        self.sources = sources
        self.question = question
        self.conversation_id = conversation_id
        self.retrieved_at = retrieved_at
        self.grounding_score = grounding_score


class QAConnector:
    """
    Question/Answer connector with RAG functionality.
    
    This class handles:
    - Document retrieval (vector search)
    - Prompt construction with context
    - Grounded answer generation
    - Fallback handling
    """
    
    def __init__(self):
        self.rag_enabled = settings.ENABLE_RAG
        self.top_k = settings.RAG_TOP_K
        self.score_threshold = settings.RAG_SCORE_THRESHOLD
        self.max_context_tokens = settings.RAG_MAX_CONTEXT_TOKENS
        self.temperature = settings.RAG_TEMPERATURE
        self.enable_fallback = settings.ENABLE_FALLBACK_RESPONSE
        
        self.conversations = {}
        
        self.is_configured = (
            settings.AZURE_OPENAI_ENDPOINT and 
            settings.AZURE_OPENAI_API_KEY
        )
    
    async def ask_question(
        self,
        question: str,
        conversation_id: Optional[str] = None
    ) -> RAGResult:
        """
        Ask a question using RAG.
        """
        if not self.rag_enabled:
            return self._create_fallback_result(question, conversation_id)
        
        retrieved_chunks = await self._retrieve_context(question, top_k=self.top_k)
        
        avg_score = sum(c.score for c in retrieved_chunks) / len(retrieved_chunks) if retrieved_chunks else 0
        
        if self.is_configured:
            answer = await self._generate_answer(question, retrieved_chunks)
        else:
            answer = self._create_fallback_answer(question, retrieved_chunks)
        
        if conversation_id is None:
            conversation_id = await self._get_or_create_conversation()
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
        
        return RAGResult(
            answer=answer,
            sources=retrieved_chunks,
            question=question,
            conversation_id=conversation_id,
            retrieved_at=datetime.now().isoformat(),
            grounding_score=avg_score
        )
    
    async def _retrieve_context(self, question: str, top_k: int = 5) -> List[SourceChunk]:
        """
        Retrieve relevant context chunks for a question.
        """
        mock_documents = [
            {
                "id": "doc_001",
                "document_id": "document_001",
                "title": "AI Architecture Guide",
                "content": "The AI architecture uses FastAPI with Azure OpenAI for natural language processing. The RAG pipeline involves document chunking, embedding generation using text-embedding-ada-002, and vector storage in Azure AI Search for semantic retrieval.",
                "score": 0.92
            },
            {
                "id": "doc_002",
                "document_id": "document_002",
                "title": "Terraform Infrastructure Guide",
                "content": "Infrastructure is provisioned using Terraform with reusable modules. The architecture includes resource groups, virtual networks, AKS for container orchestration, and Azure Container Registry for image storage. CI/CD pipelines automate the deployment process.",
                "score": 0.88
            },
            {
                "id": "doc_003",
                "document_id": "document_003",
                "title": "Monitoring with Application Insights",
                "content": "Application Insights provides comprehensive monitoring including performance metrics, dependency tracking, and custom events. Alerts can be configured for availability and resource utilization. Dashboards visualize application and infrastructure health.",
                "score": 0.75
            }
        ]
        
        question_lower = question.lower()
        scored_chunks = []
        
        for doc in mock_documents:
            score = 0.3
            keywords = question_lower.split()
            for kw in keywords:
                if kw in doc["content"].lower() or kw in doc["title"].lower():
                    score += 0.1
            score = min(score, 1.0)
            
            if score >= self.score_threshold:
                scored_chunks.append(SourceChunk(
                    id=doc["id"],
                    document_id=doc["document_id"],
                    content=doc["content"],
                    score=score,
                    title=doc["title"]
                ))
        
        scored_chunks.sort(key=lambda x: x.score, reverse=True)
        return scored_chunks[:top_k]
