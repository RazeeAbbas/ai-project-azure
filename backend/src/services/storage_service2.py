
    async def list_documents(self, prefix: str = "documents/") -> List[Dict[str, Any]]:
        """List documents in the container."""
        container = await self.container_client
        
        if self.is_local:
            return [
                {
                    "name": "document1.pdf",
                    "blob_url": "http://127.0.0.1:10000/documents/doc1.pdf",
                    "size": 1024
                }
            ]
        
        blobs = []
        async for blob in container.list_blobs(name_starts_with=prefix):
            blobs.append({
                "name": blob.name,
                "blob_url": blob.url,
                "size": blob.size
            })
        
        return blobs
    
    async def check_connection(self) -> str:
        """Check storage connectivity."""
        try:
            container = await self.container_client
            if self.is_local:
                return "healthy (local)"
            
            containers = container.list_blobs()
            return "healthy"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def get_document_info(self, blob_name: str) -> Dict[str, Any]:
        """Get information about a document."""
        container = await self.container_client
        
        if self.is_local:
            return {
                "name": blob_name,
                "size": 1024,
                "content_type": "application/octet-stream"
            }
        
        blob_client = container.get_blob_client(blob_name)
        try:
            props = await blob_client.get_blob_properties()
            return {
                "name": props.name,
                "size": props.size,
                "content_type": props.content_type,
                "last_modified": props.last_modified
            }
        except Exception:
            return {
                "name": blob_name,
                "size": 0,
                "content_type": "unknown"
            }
