"""
RAG Retriever with Structured Query Format

Implements three-step retrieval format:
[RETRIEVE KNOWLEDGE]
query: natural language
filters: ...
top_k: 5
[/RETRIEVE]

Ensures:
- AI can query knowledge consistently
- Multilingual support via Language Bridge
- Structured filtering
- Reproducible across different LLMs
"""

from typing import Dict, Any, List, Optional
from src.core.utils.language_bridge import get_language_bridge
from src.core.utils.vector_db_manager import get_vector_db_manager


class RAGRetriever:
    """
    RAG Retriever with Language Bridge support

    Features:
    - Structured query format
    - Automatic language detection
    - zh → en translation for search
    - Metadata filtering
    - Importance scoring
    """

    def __init__(self):
        self.language_bridge = get_language_bridge()
        self.vector_manager = get_vector_db_manager()

    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        min_score: Optional[float] = None,
        collection_name: str = "flyto2_project_knowledge"
    ) -> Dict[str, Any]:
        """
        Retrieve knowledge with language bridge

        Args:
            query: Natural language query (any language)
            filters: Metadata filters
                {
                    "language": "zh" | "en",
                    "category": "practice" | "error" | "success" | ...,
                    "module_id": "browser.click",
                    "importance": {"$gte": 0.7}
                }
            top_k: Number of results
            min_score: Minimum similarity score
            collection_name: Qdrant collection

        Returns:
            {
                "success": bool,
                "query": {
                    "original": str,
                    "search_query": str,
                    "language": "zh" | "en",
                    "translated": bool
                },
                "results": [
                    {
                        "content": str,
                        "score": float,
                        "metadata": {...}
                    }
                ],
                "total": int
            }
        """
        # Step 1: Prepare query with language bridge
        prepared = await self.language_bridge.prepare_query_for_search(query)

        search_query = prepared["search_query"]

        # Step 2: Build Qdrant filter
        qdrant_filter = None
        if filters:
            # Convert filters to Qdrant format
            qdrant_filter = self._build_qdrant_filter(filters)

        # Step 3: Search vector DB
        try:
            # Get knowledge store directly (bypasses manager)
            from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore

            connector = VectorDBConnector(mode="local")
            connector.connect()

            store = KnowledgeStore(
                connector=connector,
                collection_name=collection_name,
                embedding_provider="local"
            )

            # Search with language-bridged query
            results = store.search(
                query=search_query,
                top_k=top_k,
                score_threshold=min_score,
                filters=filters  # Pass filters directly to Qdrant
            )

            # Sort by importance score if available
            results = self._sort_by_importance(results)

            return {
                "success": True,
                "query": prepared,
                "results": results[:top_k],
                "total": len(results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": prepared,
                "results": [],
                "total": 0
            }

    def _build_qdrant_filter(self, filters: Dict[str, Any]) -> Dict:
        """Build Qdrant filter from simple dict"""
        # TODO: Convert to Qdrant filter format
        # For now, we'll filter in Python
        return {}

    def _filter_results(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter results by metadata"""
        filtered = []

        for result in results:
            metadata = result.get("metadata", {})
            match = True

            for key, value in filters.items():
                if key == "importance":
                    # Handle range queries
                    if isinstance(value, dict):
                        result_value = metadata.get("importance", 0.0)
                        if "$gte" in value and result_value < value["$gte"]:
                            match = False
                            break
                        if "$lte" in value and result_value > value["$lte"]:
                            match = False
                            break
                else:
                    # Exact match
                    if metadata.get(key) != value:
                        match = False
                        break

            if match:
                filtered.append(result)

        return filtered

    def _sort_by_importance(self, results: List[Dict]) -> List[Dict]:
        """Sort by importance score (descending)"""
        return sorted(
            results,
            key=lambda x: x.get("metadata", {}).get("importance", 0.0),
            reverse=True
        )

    def format_retrieval_request(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> str:
        """
        Format retrieval request for AI

        Returns structured format:
        [RETRIEVE KNOWLEDGE]
        query: {query}
        filters:
          language: en
          category: error
        top_k: 5
        [/RETRIEVE]
        """
        request = "[RETRIEVE KNOWLEDGE]\n"
        request += f"query: {query}\n"

        if filters:
            request += "filters:\n"
            for key, value in filters.items():
                request += f"  {key}: {value}\n"

        request += f"top_k: {top_k}\n"
        request += "[/RETRIEVE]\n"

        return request

    async def parse_and_execute_retrieval(self, request_text: str) -> Dict[str, Any]:
        """
        Parse structured retrieval request and execute

        Input format:
        [RETRIEVE KNOWLEDGE]
        query: How to fix timeout error?
        filters:
          category: error
          module_id: browser.click
        top_k: 5
        [/RETRIEVE]

        Returns: retrieval results
        """
        import re

        # Extract query
        query_match = re.search(r'query:\s*(.+)', request_text)
        query = query_match.group(1).strip() if query_match else ""

        # Extract top_k
        top_k_match = re.search(r'top_k:\s*(\d+)', request_text)
        top_k = int(top_k_match.group(1)) if top_k_match else 5

        # Extract filters
        filters = {}
        filter_section = re.search(r'filters:\s*\n((?:  .+\n)+)', request_text)
        if filter_section:
            filter_lines = filter_section.group(1).strip().split('\n')
            for line in filter_lines:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    filters[key.strip()] = value.strip()

        # Execute retrieval
        return await self.retrieve(
            query=query,
            filters=filters if filters else None,
            top_k=top_k
        )


# Singleton
_retriever = None

def get_rag_retriever() -> RAGRetriever:
    """Get singleton RAG retriever"""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever


# Convenience functions
async def retrieve_knowledge(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Quick knowledge retrieval with language bridge

    Example:
        # Chinese query
        results = await retrieve_knowledge("如何修復 timeout 錯誤？")
        # → Automatically translates to EN → searches → returns results

        # English query
        results = await retrieve_knowledge("How to fix timeout error?")
        # → Direct search

        # With filters
        results = await retrieve_knowledge(
            "browser error",
            filters={"category": "error", "module_id": "browser.click"}
        )
    """
    retriever = get_rag_retriever()
    return await retriever.retrieve(query, filters, top_k)


async def execute_structured_query(request_text: str) -> Dict[str, Any]:
    """
    Execute structured [RETRIEVE KNOWLEDGE] request

    Example:
        request = '''
        [RETRIEVE KNOWLEDGE]
        query: timeout error in browser module
        filters:
          category: error
          language: en
        top_k: 5
        [/RETRIEVE]
        '''

        results = await execute_structured_query(request)
    """
    retriever = get_rag_retriever()
    return await retriever.parse_and_execute_retrieval(request_text)
