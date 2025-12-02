"""
Similarity Trainer Module - Train similarity matching from solutions

Atomic responsibility: Learn from successful solutions
Extracted from: ai_error_solver.py lines 498-644
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional, Set
from src.core.utils.vector_db_manager import vector_store
from src.core.utils.translator import translate_to_english
from src.core.utils.notifier import notify


class SimilarityTrainerModule:
    """
    Train similarity matching by comparing AI predictions with actual solutions

    Single responsibility: Extract keywords, calculate similarity, store training data
    """

    @staticmethod
    async def train(
        error: str,
        ai_solution: Dict[str, Any],
        execution_result: Dict[str, Any],
        notify_callback: Optional[callable] = None
    ):
        """
        Train similarity matching

        Args:
            error: Original error message
            ai_solution: AI's solution (full_response, structured)
            execution_result: Execution result (success, commands_executed)
            notify_callback: Optional notification callback
        """
        await notify("📊 Training similarity matching...", notify_callback)

        try:
            # Extract what AI predicted
            ai_response = ai_solution.get("full_response", "")
            ai_structured = ai_solution.get("structured", {})
            ai_commands = ai_structured.get("commands", [])

            # Extract key points from AI's response
            ai_keywords = SimilarityTrainerModule._extract_keywords(ai_response)

            # Extract key points from executed commands
            cmd_keywords = SimilarityTrainerModule._extract_keywords(" ".join(ai_commands))

            # Calculate similarity score
            similarity_score = SimilarityTrainerModule._calculate_similarity(
                ai_keywords,
                cmd_keywords
            )

            await notify(f"  Similarity score: {similarity_score:.2%}", notify_callback)

            # Store training data to vector DB
            await SimilarityTrainerModule._store_training_data(
                error=error,
                ai_prediction=ai_response[:500],
                actual_solution=ai_commands,
                similarity_score=similarity_score,
                notify_callback=notify_callback
            )

            await notify("✅ Similarity training completed", notify_callback)

        except Exception as e:
            await notify(f"⚠️ Similarity training error: {e}", notify_callback)

    @staticmethod
    def _extract_keywords(text: str) -> Set[str]:
        """Extract meaningful keywords from text"""
        # Convert to lowercase
        text = text.lower()

        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s-]', ' ', text)

        # Split into words
        words = text.split()

        # Filter out common stop words and very short words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'this', 'that',
            'it', 'from', 'be', 'are', 'was', 'were', 'have', 'has', 'had'
        }

        keywords = {
            word for word in words
            if len(word) > 2 and word not in stop_words
        }

        return keywords

    @staticmethod
    def _calculate_similarity(set1: Set[str], set2: Set[str]) -> float:
        """Calculate Jaccard similarity between two keyword sets"""
        if not set1 or not set2:
            return 0.0

        intersection = set1.intersection(set2)
        union = set1.union(set2)

        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    async def _store_training_data(
        error: str,
        ai_prediction: str,
        actual_solution: list,
        similarity_score: float,
        notify_callback: Optional[callable] = None
    ):
        """Store training data for future learning"""
        try:
            # Translate to English
            error_en = await translate_to_english(error, context="error")
            prediction_en = await translate_to_english(ai_prediction, context="solution")

            # Create training entry
            content = f"""
AI Training Data

Error: {error_en}

AI Prediction: {prediction_en}

Actual Solution: {chr(10).join(f"  - {cmd}" for cmd in actual_solution)}

Similarity Score: {similarity_score:.2%}

This training data helps improve AI solution accuracy over time.
""".strip()

            # Store to vector DB
            await vector_store(
                content=content,
                metadata={
                    "source": "ai_error_solver_training",
                    "category": "training_data",
                    "similarity_score": similarity_score,
                    "original_error": error,
                    "timestamp": datetime.now().isoformat()
                }
            )

            await notify("  💾 Training data stored to vector DB", notify_callback)

        except Exception as e:
            await notify(f"  ⚠️ Failed to store training data: {e}", notify_callback)
