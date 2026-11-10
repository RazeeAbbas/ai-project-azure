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

        # Normalize content type for matching
        content_type_lower = (content_type or "").lower().replace(" ", "")

        if "pdf" in content_type_lower or content_type_lower == "application/pdf":
            return f"[PDF Document] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "docx" in content_type_lower or "doc" in content_type_lower:
            return f"[Word Document] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "pptx" in content_type_lower or "ppt" in content_type_lower:
            return f"[PowerPoint] {content_str[:2000]}\n\n[Extracted content simulation]"
        elif "json" in content_type_lower:
            return f"[JSON File] {content_str[:2000]}"
        else:
            return content_str[:2000]
    
    def _split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
        """
        Split text into chunks with overlap.
        """
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_size must be positive and greater than chunk_overlap")

        chunks = []
        step = chunk_size - chunk_overlap
        for chunk_index, start in enumerate(range(0, len(text), step)):
            content = text[start:start + chunk_size].strip()
            if content:
                chunks.append({
                    "id": f"chunk_{chunk_index}",
                    "content": content,
                    "chunk_index": chunk_index,
                    "chunk_size": len(content),
                    "metadata": {},
                })
        return chunks

