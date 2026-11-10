# ------------------------------------------ #
# AI Knowledge Copilot - Embedding Service     #
# ------------------------------------------ #

"""
Embedding service for generating text embeddings.
Uses Azure OpenAI embedding model.
"""

import logging
from typing import List, Optional

from src.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using Azure OpenAI.
    
    This service generates vector embeddings for:
    - Documents for indexing
    - Questions for retrieval
    - Any other text content
    """
    
    def __init__(self):
        self.embedding_deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        self.model = self.embedding_deployment
        self.is_configured = (
            settings.AZURE_OPENAI_ENDPOINT and 
            settings.AZURE_OPENAI_API_KEY
        )
        
        # Azure OpenAI client (lazy initialization)
        self._client = None
    
    def _get_client(self):
        """Get or create the Azure OpenAI client."""
        if self._client is None and self.is_configured:
            from openai import AzureOpenAI
            self._client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
        return self._client
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding
        """
        if not self.is_configured:
            # Return a placeholder embedding
            # In production, this should come from the embedding model
            logger.warning("Azure OpenAI not configured - using placeholder embedding")
            return [0.0] * settings.EMBEDDING_DIMENSION
        
        try:
            client = self._get_client()
            if client is None:
                return [0.0] * settings.EMBEDDING_DIMENSION
            
            response = client.embeddings.create(
                input=[text],
                model=self.embedding_deployment
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return zero vector on error
            return [0.0] * settings.EMBEDDING_DIMENSION
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (list of lists of floats)
        """
        if not self.is_configured:
            # Return placeholder embeddings
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
        
        try:
            client = self._get_client()
            if client is None:
                return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
            
            response = client.embeddings.create(
                input=texts,
                model=self.embedding_deployment
            )
            
            return [data.embedding for data in response.data]
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return zero vectors on error
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
    
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return await self.generate_embeddings(documents)
    
    async def embed_query(self, query: str) -> List[float]:
        """Embed a query (question)."""
        return await self.generate_embedding(query)
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return settings.EMBEDDING_DIMENSION
    
    def get_embedding_model(self) -> str:
        """Get the embedding model name."""
        return self.embedding_deployment
    
    def check_connection(self) -> str:
        """Check embedding service connectivity."""
        if not self.is_configured:
            return "not_configured"
        try:
            self._get_client()
            return "healthy"
        except Exception as e:
            return f"error: {str(e)}"
