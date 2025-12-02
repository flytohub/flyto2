"""
Vector Query Module - Query vector DB for similar solutions

Atomic responsibility: Vector DB search for error solutions
Extracted from: ai_error_solver.py lines 173-218
"""

from typing import Any, Dict, List
from src.core.utils.vector_db_manager import vector_search


class VectorQueryModule:
    """
    Query vector DB for similar past successful solutions

    Single responsibility: Search vector DB for similar errors and solutions
    """

    @staticmethod
    async def query_similar_solutions(
        error: str,
        error_type: str,
        min_score: float = 0.5,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query vector DB for similar past solutions

        Args:
            error: Error message
            error_type: Error type (Exception class name)
            min_score: Minimum similarity score
            top_k: Number of results to return

        Returns:
            List of similar solutions with similarity scores
        """
        try:
            # Search for similar errors and their solutions
            results = await vector_search(
                query=f"error: {error_type} {error}",
                min_score=min_score,
                top_k=top_k
            )

            # Filter for successful solutions only
            solutions = []
            for result in results:
                metadata = result.get("metadata", {})
                if metadata.get("solution_success"):
                    solutions.append({
                        "similarity": result.get("score", 0.0),
                        "content": result.get("content", ""),
                        "solution_data": metadata.get("solution_data", {}),
                        "timestamp": metadata.get("timestamp")
                    })

            return solutions

        except Exception as e:
            print(f"⚠️ Vector DB query error: {e}")
            return []
