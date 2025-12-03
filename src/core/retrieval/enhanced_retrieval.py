#!/usr/bin/env python3
"""
Enhanced Retrieval Module
Implements Query Rewrite, MMR, Hybrid Search, Reranking
"""
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np


class QueryRewriter:
    """Query Rewriter"""

    def __init__(self, strategies: List[str]):
        self.strategies = strategies

    def rewrite(self, query: str, context: Optional[str] = None) -> List[str]:
        """
        Rewrite query to generate multiple variants

        Args:
            query: Original query
            context: Conversation context (optional)

        Returns:
            List of query variants
        """
        queries = [query]  # Original query

        if 'expand_keywords' in self.strategies:
            queries.extend(self._expand_keywords(query))

        if 'add_context' in self.strategies and context:
            queries.extend(self._add_context(query, context))

        if 'specify_type' in self.strategies:
            queries.extend(self._specify_type(query))

        # Deduplicate
        return list(set(queries))

    def _expand_keywords(self, query: str) -> List[str]:
        """Expand keywords"""
        # Simple synonym expansion
        expansions = []

        # Name related
        if any(word in query.lower() for word in ['name', 'called', 'who']):
            expansions.append('my name')
            expansions.append('name')

        # Interest related
        if any(word in query.lower() for word in ['like', 'interest', 'hobby']):
            expansions.append('like')
            expansions.append('interest')

        # Recommendation related
        if any(word in query.lower() for word in ['recommend', 'suggest', 'learn']):
            expansions.append('recommend interest')

        return expansions

    def _add_context(self, query: str, context: str) -> List[str]:
        """Add context information"""
        # Extract key information from context
        queries = []

        # If asking about "my", add possible topics
        if 'my' in query.lower() or 'i ' in query.lower():
            if 'Python' in context:
                queries.append(f"{query} Python")
            if 'machine learning' in context.lower():
                queries.append(f"{query} machine learning")

        return queries

    def _specify_type(self, query: str) -> List[str]:
        """Explicitly specify content type"""
        # Add type labels based on query type
        queries = []

        if any(word in query.lower() for word in ['name', 'like', 'my']):
            queries.append(f"conversation: {query}")

        return queries


class MMRSelector:
    """MMR (Maximal Marginal Relevance) Selector"""

    def __init__(self, diversity: float = 0.3):
        """
        Args:
            diversity: Diversity parameter (0.0-1.0)
                      0.0 = Only look at similarity
                      1.0 = Only look at diversity
        """
        self.diversity = diversity

    def select(
        self,
        candidates: List[Dict[str, Any]],
        query_embedding: Optional[List[float]],
        final_k: int
    ) -> List[Dict[str, Any]]:
        """
        Use MMR to select final results

        Args:
            candidates: List of candidate results
            query_embedding: Query vector (optional)
            final_k: Final count to retain

        Returns:
            MMR selected results
        """
        if len(candidates) <= final_k:
            return candidates

        if not query_embedding:
            # If no query vector, just take top-k
            return candidates[:final_k]

        selected = []
        remaining = candidates.copy()

        # First selection: highest similarity
        selected.append(remaining.pop(0))

        # Iteratively select remaining
        while len(selected) < final_k and remaining:
            best_score = -float('inf')
            best_idx = 0

            for i, candidate in enumerate(remaining):
                # MMR score = lambda * sim(query, doc) - (1-lambda) * max(sim(doc, selected))
                query_sim = candidate.get('score', 0.0)

                # Calculate max similarity with already selected documents
                max_selected_sim = 0.0
                if 'embedding' in candidate:
                    for selected_doc in selected:
                        if 'embedding' in selected_doc:
                            sim = self._cosine_similarity(
                                candidate['embedding'],
                                selected_doc['embedding']
                            )
                            max_selected_sim = max(max_selected_sim, sim)

                # MMR score
                mmr_score = (
                    (1 - self.diversity) * query_sim -
                    self.diversity * max_selected_sim
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i

            selected.append(remaining.pop(best_idx))

        return selected

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return dot_product / (norm_v1 * norm_v2)


class EnhancedRetrieval:
    """Enhanced Retriever"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Args:
            config_path: Config file path (defaults to config/vector_config.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "vector_config.yaml"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        retrieval_config = self.config['retrieval']

        # Query Rewriter
        if retrieval_config['query_rewrite']['enabled']:
            self.query_rewriter = QueryRewriter(
                strategies=retrieval_config['query_rewrite']['strategies']
            )
        else:
            self.query_rewriter = None

        # MMR Selector
        if retrieval_config['mmr']['enabled']:
            self.mmr_selector = MMRSelector(
                diversity=retrieval_config['mmr']['diversity']
            )
        else:
            self.mmr_selector = None

        # Retrieval parameters
        self.top_k = retrieval_config['top_k']
        self.score_threshold = retrieval_config['score_threshold']
        self.final_k = retrieval_config['mmr']['final_k']
        self.method = retrieval_config['method']

    def retrieve(
        self,
        query: str,
        qdrant_client,
        collection_name: str,
        embedding_function,
        context: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute enhanced retrieval

        Args:
            query: Query string
            qdrant_client: Qdrant client
            collection_name: Collection name
            embedding_function: Embedding function
            context: Conversation context (for query rewrite)
            metadata_filter: Metadata filter conditions

        Returns:
            List of retrieval results
        """
        # 1. Query Rewrite
        queries = [query]
        if self.query_rewriter:
            queries = self.query_rewriter.rewrite(query, context)

        # 2. Execute retrieval for each query
        all_results = []
        query_embedding = None

        for q in queries:
            # Generate embedding
            embedding = embedding_function(q)
            if query_embedding is None:
                query_embedding = embedding

            # Execute vector retrieval
            results = self._vector_search(
                qdrant_client,
                collection_name,
                embedding,
                metadata_filter
            )
            all_results.extend(results)

        # 3. Deduplicate (by ID)
        seen_ids = set()
        unique_results = []
        for result in all_results:
            result_id = result.get('id')
            if result_id and result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)

        # 4. Score filtering
        filtered_results = [
            r for r in unique_results
            if r.get('score', 0.0) >= self.score_threshold
        ]

        # 5. Sort (by score descending)
        filtered_results.sort(key=lambda x: x.get('score', 0.0), reverse=True)

        # 6. MMR deduplication
        if self.mmr_selector and len(filtered_results) > self.final_k:
            final_results = self.mmr_selector.select(
                filtered_results,
                query_embedding,
                self.final_k
            )
        else:
            final_results = filtered_results[:self.final_k]

        return final_results

    def _vector_search(
        self,
        qdrant_client,
        collection_name: str,
        embedding: List[float],
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute vector retrieval"""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Build filter conditions
            filter_conditions = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    # Metadata is nested, need to use metadata.key
                    field_key = f"metadata.{key}"
                    conditions.append(
                        FieldCondition(key=field_key, match=MatchValue(value=value))
                    )
                if conditions:
                    filter_conditions = Filter(must=conditions)

            # Execute search (Qdrant v1.16+ uses query_points instead of search)
            search_result = qdrant_client.query_points(
                collection_name=collection_name,
                query=embedding,
                limit=self.top_k,
                query_filter=filter_conditions,
                with_payload=True,
                with_vectors=True  # For MMR
            ).points

            # Convert result format
            results = []
            for hit in search_result:
                results.append({
                    'id': hit.id,
                    'score': hit.score,
                    'content': hit.payload.get('content', ''),
                    'metadata': hit.payload.get('metadata', {}),
                    'embedding': hit.vector if hasattr(hit, 'vector') else None
                })

            return results

        except Exception as e:
            print(f"Warning: Vector retrieval failed: {e}")
            return []

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieval results as context

        Args:
            results: Retrieval results

        Returns:
            Formatted context string
        """
        if not results:
            return ""

        context_parts = []

        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            score = result.get('score', 0.0)

            # Citation format
            citation = self._format_citation(i, metadata)

            context_parts.append(f"{citation}\n{content}")

        return "\n\n".join(context_parts)

    def _format_citation(self, index: int, metadata: Dict[str, Any]) -> str:
        """Format citation"""
        citation_config = self.config['prompt']['citation']

        if not citation_config['enabled']:
            return f"[{index}]"

        format_template = citation_config['format']

        # Replace template variables
        citation = format_template.format(
            index=index,
            type=metadata.get('type', 'unknown'),
            project=metadata.get('project', 'unknown'),
            timestamp=metadata.get('timestamp', '')
        )

        return citation
