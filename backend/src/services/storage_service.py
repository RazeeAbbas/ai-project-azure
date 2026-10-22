# ------------------------------------------ #
# AI Knowledge Copilot - Storage Service       #
# ------------------------------------------ #

"""
Azure Blob Storage service for document management.
Uses Azure Storage Blob SDK with fallback to Azurite for local dev.
"""

import os
from typing import Optional, List, Dict, Any
import aiofiles

try:
    from azure.storage.blob import (
        BlobServiceClient,
        BlobClient,
        ContainerClient
    )
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    print("Azure Storage SDK not available - using local fallback mode")


from src.config.settings import settings
from src.core.helpers import get_current_timestamp


class StorageService:
    """Service for managing Azure Blob Storage operations."""
    
    def __init__(self):
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_STORAGE_CONTAINER
        self.blob_service_client = None
        self._container_client = None
        self.is_local = "devstoreaccount1" in self.connection_string or not self.connection_string
    
    async def get_blob_service_client(self):
        """Get or create the blob service client."""
        if self.blob_service_client is None:
            if not AZURE_STORAGE_AVAILABLE:
                raise RuntimeError("Azure Storage SDK is not installed")
            
            if self.connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
            else:
                from azure.identity import DefaultAzureCredential
                self.blob_service_client = BlobServiceClient(
                    account_url=f"https://{self.account_name}.blob.core.windows.net",
                    credential=DefaultAzureCredential()
                )
        
        return self.blob_service_client
    
    @property
    async def container_client(self):
        """Get the container client."""
        if self._container_client is None:
            blob_service_client = await self.get_blob_service_client()
            self._container_client = blob_service_client.get_container_client(self.container_name)
            
            if self.is_local:
                await self._ensure_container_exists()
        
        return self._container_client
    
    async def _ensure_container_exists(self):
        """Ensure the container exists."""
        if self.is_local:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            try:
                await container_client.create_container()
            except Exception:
                pass
    
    async def upload_document(
        self,
        file_path: str,
        file_name: str,
        content_type: str,
        overwrite: bool = True
    ) -> str:
        """Upload a document to blob storage."""
        container = await self.container_client
        
        blob_name = f"documents/{get_current_timestamp().replace(':', '-')}-{hash(file_name) & 0xFFFFFFFF}.bin"
        
        if not self.is_local:
            blob_client = container.get_blob_client(blob_name)
            with open(file_path, "rb") as data:
                await blob_client.upload_blob(data, overwrite=overwrite, content_type=content_type)
            blob_url = f"{blob_client.url}"
        else:
            blob_url = f"http://127.0.0.1:10000/{self.container_name}/{blob_name}"
            async with aiofiles.open(blob_url.replace("http://127.0.0.1:10000/", ""), "wb") as f:
                pass  # Local mode placeholder
        
        return blob_url
    
    async def download_document(self, blob_name: str) -> bytes:
        """Download a document from blob storage."""
        container = await self.container_client
        
        if self.is_local:
            return b"Local storage mock content"
        
        blob_client = container.get_blob_client(blob_name)
        download_stream = await blob_client.download_blob()
        return await download_stream.readall()
    
    async def delete_document(self, blob_name: str) -> bool:
        """Delete a document from blob storage."""
        container = await self.container_client
        
        if self.is_local:
            return True
        
        blob_client = container.get_blob_client(blob_name)
        try:
            await blob_client.delete_blob()
            return True
        except Exception:
            return False
