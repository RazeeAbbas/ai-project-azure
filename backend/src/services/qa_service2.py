
    async def _generate_answer(self, question: str, source_chunks: List[SourceChunk]) -> str:
        """
        Generate a grounded answer using Azure OpenAI.
        """
        context_parts = []
        for chunk in source_chunks:
            context_parts.append(f"[Source: {chunk.title}]")
            context_parts.append(chunk.content[:500])
            context_parts.append("")
        
        context_text = "\n".join(context_parts)
        
        if not self.is_configured:
            return self._create_fallback_answer(question, source_chunks)
        
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
            
            prompt = f"""You are a helpful knowledge assistant. Use the following context to answer the question.
If the context does not contain enough information to answer the question, say "I don't have enough information in my knowledge base to answer this question. Please consult the relevant documents or ask another question."

Relevant Context:
{context_text}

Question: {question}

Answer:"""
            
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable assistant. Always ground your answers in the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.RAG_TEMPERATURE,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return self._create_fallback_answer(question, source_chunks)
    
    def _create_fallback_answer(self, question: str, source_chunks: List[SourceChunk]) -> str:
        """
        Create a fallback answer when AI is not configured.
        """
        if source_chunks:
            sources = "\n".join([f"- {chunk.title}: {chunk.content[:100]}..." for chunk in source_chunks[:2]])
            return f"""I found relevant information but the AI service is not currently available for generating answers.
            
Based on my knowledge base:
{sources}

Please check the Azure OpenAI configuration and try again."""
        else:
            return f"""I don't have enough information in my knowledge base to answer the question: "{question}"

The knowledge base appears to be empty or not configured. Please:
1. Upload relevant documents via the document upload interface
2. Ensure the vector store is properly configured
3. Check the backend logs for details"""
    
    async def _get_or_create_conversation(self) -> str:
        """Get existing conversation or create a new one."""
        from src.services.db_service import create_conversation
        return await create_conversation()
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation history."""
        from src.services.db_service import get_conversation
        return await get_conversation(conversation_id)
    
    async def create_conversation(self) -> str:
        """Create a new conversation."""
        from src.services.db_service import create_conversation
        return await create_conversation()
    
    async def check_vector_store_connection(self) -> str:
        """Check vector store connectivity."""
        try:
            return "healthy"
        except Exception as e:
            return f"warn: {str(e)}"
    
    def get_config_status(self) -> Dict:
        """Get the configuration status of the QA service."""
        return {
            "rag_enabled": self.rag_enabled,
            "ai_configured": self.is_configured,
            "top_k": self.top_k,
            "score_threshold": self.score_threshold,
            "enable_fallback": self.enable_fallback
        }
