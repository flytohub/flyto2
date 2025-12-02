"""
Vector DB Manager - Singleton access to vector database

Purpose: Eliminate duplicate vector DB connection code
- Replaces ~240 lines of duplicate code across 8+ files
- Provides singleton connection management
- One-liner search interface
- Automatic connection pooling
"""

from typing import Any, Dict, List, Optional
from pathlib import Path


class VectorDBManager:
    """
    Singleton vector DB manager

    Eliminates duplicate connection code in:
    - ai_error_solver.py (_query_similar_solutions, _store_successful_solution, _store_training_data)
    - self_healing_practice.py (_query_similar_solutions, _store_solution)
    - smart_executor.py (_query_knowledge_base)
    - daily_practice.py
    - Multiple bot scripts
    """

    _instance = None
    _connector = None
    _stores = {}  # Cache of KnowledgeStore instances by collection name

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.mode = "local"

    async def get_connector(self):
        """
        Get or create vector DB connector (singleton)

        Returns:
            Connected VectorDBConnector instance
        """
        if self._connector is None:
            from src.core.modules.atomic.vector import VectorDBConnector

            self._connector = VectorDBConnector(mode=self.mode)
            self._connector.connect()

        return self._connector

    async def get_knowledge_store(
        self,
        collection_name: str = "flyto2_project_knowledge",
        embedding_provider: str = "local"
    ):
        """
        Get or create knowledge store for collection

        Args:
            collection_name: Collection name
            embedding_provider: Embedding provider (local/openai)

        Returns:
            KnowledgeStore instance
        """
        cache_key = f"{collection_name}:{embedding_provider}"

        if cache_key not in self._stores:
            from src.core.modules.atomic.vector import KnowledgeStore

            connector = await self.get_connector()

            self._stores[cache_key] = KnowledgeStore(
                connector=connector,
                collection_name=collection_name,
                embedding_provider=embedding_provider
            )

        return self._stores[cache_key]

    async def search(
        self,
        query: str,
        collection_name: str = "flyto2_project_knowledge",
        top_k: int = 5,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        One-liner vector DB search

        Args:
            query: Search query
            collection_name: Collection to search
            top_k: Number of results
            min_score: Optional minimum similarity score

        Returns:
            List of search results with scores
        """
        from src.core.modules.atomic.vector import KnowledgeSearch

        store = await self.get_knowledge_store(collection_name)
        search = KnowledgeSearch(knowledge_store=store)

        if min_score is not None:
            return search.search_with_score_threshold(
                query=query,
                min_score=min_score,
                top_k=top_k
            )
        else:
            return search.search(query=query, top_k=top_k)

    async def store(
        self,
        content: str,
        metadata: Dict[str, Any],
        collection_name: str = "flyto2_project_knowledge"
    ):
        """
        Store content to vector DB

        Args:
            content: Content to store
            metadata: Metadata dict
            collection_name: Collection name
        """
        store = await self.get_knowledge_store(collection_name)
        store.store(content=content, metadata=metadata)

    async def close(self):
        """Close all connections"""
        if self._connector:
            self._connector.disconnect()
            self._connector = None
        self._stores.clear()


# Singleton instance
_manager = None

def get_vector_db_manager() -> VectorDBManager:
    """Get singleton vector DB manager"""
    global _manager
    if _manager is None:
        _manager = VectorDBManager()
    return _manager


# Convenience functions
async def vector_search(
    query: str,
    collection_name: str = "flyto2_project_knowledge",
    top_k: int = 5,
    min_score: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    One-liner vector DB search

    Example:
        results = await vector_search("error: module not found", min_score=0.6)
    """
    manager = get_vector_db_manager()
    return await manager.search(query, collection_name, top_k, min_score)


async def vector_store(
    content: str,
    metadata: Dict[str, Any],
    collection_name: str = "flyto2_project_knowledge"
):
    """
    One-liner vector DB storage

    Example:
        await vector_store(
            content="AI solution: install playwright",
            metadata={"category": "solution", "success": True}
        )
    """
    manager = get_vector_db_manager()
    await manager.store(content, metadata, collection_name)
