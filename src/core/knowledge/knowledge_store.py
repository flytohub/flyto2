"""
Knowledge Store Wrapper - Simplified interface for document ingestion

Wraps the atomic vector module's KnowledgeStore

Enterprise-grade configuration with cloud support
"""

import os
from typing import Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.core.modules.atomic.vector.knowledge_store import KnowledgeStore as AtomicKnowledgeStore
from src.core.modules.atomic.vector.connector import VectorDBConnector


class KnowledgeStore:
    """Simplified knowledge store interface"""

    def __init__(self):
        """Initialize knowledge store with cloud connector"""
        # Create cloud connector
        mode = os.getenv("QDRANT_MODE", "cloud")  # Default to cloud
        self.connector = VectorDBConnector(
            mode=mode,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.connector.connect()

        # Create atomic knowledge store
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local")
        self.store = AtomicKnowledgeStore(
            connector=self.connector,
            collection_name="flyto2_knowledge",
            embedding_provider=embedding_provider
        )

    async def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store knowledge entry

        Args:
            content: Text content to store
            metadata: Metadata dictionary

        Returns:
            ID of stored entry
        """
        return self.store.store(content=content, metadata=metadata)

    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> list:
        """
        Search for similar entries

        Args:
            query: Search query
            filters: Metadata filters
            top_k: Number of results to return

        Returns:
            List of matching entries
        """
        return self.store.search(query=query, filters=filters, top_k=top_k)
