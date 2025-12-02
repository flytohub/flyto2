"""
Prompt Builder Module - Build AI prompts with full context

Atomic responsibility: Construct comprehensive AI prompts
Extracted from: ai_error_solver.py lines 243-321

Enhanced with RAG retriever integration for dynamic project knowledge.
"""

import json
import asyncio
from typing import Any, Dict, List


class PromptBuilderModule:
    """
    Build AI prompts with full project context

    Single responsibility: Create context-rich prompts for AI error resolution
    """

    @staticmethod
    async def build_error_resolution_prompt(
        error: str,
        error_type: str,
        context: Dict[str, Any],
        similar_solutions: List[Dict[str, Any]]
    ) -> str:
        """
        Build comprehensive prompt for AI error resolution

        Args:
            error: Error message
            error_type: Error type
            context: Error context (operation, params, etc.)
            similar_solutions: Similar past solutions from vector DB

        Returns:
            Complete prompt string for AI
        """
        project_context = await PromptBuilderModule._get_project_context_with_rag(error, error_type)

        prompt = f"""{project_context}

**Current Error**:
Type: {error_type}
Message: {error}

**Context**:
{json.dumps(context, indent=2)[:1000]}

**Similar Past Solutions**:
"""

        if similar_solutions:
            for i, sol in enumerate(similar_solutions[:3], 1):
                content = sol.get("content", "")[:300]
                similarity = sol.get("similarity", 0.0)
                prompt += f"\n{i}. (Similarity: {similarity:.0%})\n{content}\n"
        else:
            prompt += "\nNo similar solutions found in knowledge base.\n"

        prompt += """

**Your Task**:
Analyze this error and provide a practical solution.

Return your response as JSON:
{
  "error_analysis": "What caused this error",
  "solution_type": "command/code_change/configuration/install",
  "solution_summary": "Brief description",
  "commands": ["list", "of", "commands", "to", "run"],
  "code_changes": {
    "file": "path/to/file.py",
    "description": "what to change"
  },
  "explanation": "Why this solution works"
}

Be specific and actionable. Provide exact commands to run.
"""

        return prompt

    @staticmethod
    async def _get_project_context_with_rag(error: str, error_type: str) -> str:
        """
        Get dynamic project context from RAG knowledge base

        Queries the knowledge base for relevant information based on the error,
        including pain points, architecture, modules, and best practices.

        Falls back to static context if RAG is unavailable.
        """
        try:
            from src.core.utils.rag_retriever import retrieve_knowledge

            # Build search query from error
            search_query = f"{error_type} {error}"

            # Query knowledge base for relevant information
            results = await retrieve_knowledge(
                query=search_query,
                top_k=5
            )

            if results["success"] and results["results"]:
                # Build context from retrieved knowledge
                context_parts = ["Flyto2 Project Context (from knowledge base):\n"]

                for i, result in enumerate(results["results"], 1):
                    content = result.get("content", "")
                    metadata = result.get("metadata", {})
                    category = metadata.get("category", "unknown")
                    score = result.get("score", 0.0)

                    if score > 0.3:  # Only include relevant results
                        context_parts.append(
                            f"\n[{category.upper()}] (relevance: {score:.0%}):\n{content}\n"
                        )

                # Add fallback static info if no relevant results
                if len(context_parts) == 1:
                    context_parts.append(PromptBuilderModule._get_static_context())

                return "".join(context_parts)

        except Exception:
            pass  # Fall back to static context

        # Fallback: Use static context
        return PromptBuilderModule._get_static_context()

    @staticmethod
    def _get_static_context() -> str:
        """Get static Flyto2 project context (fallback)"""
        return """Flyto2 Project Context:

**Architecture**: Atomic module system
- Location: src/core/modules/atomic/
- Categories: browser, string, array, math, object, file, datetime, data, utility
- Modules are small, reusable Python classes
- Workflows are YAML-based

**Technology Stack**:
- Python 3.x with asyncio
- Playwright for browser automation
- YAML workflows
- Vector database (Qdrant/ChromaDB)
- Ollama for AI

**Philosophy**:
- Never give up on errors
- Self-healing and auto-recovery
- Learn from every solution
- Generate missing modules when needed

**Common Commands**:
- playwright install [browser]
- pip install [package]
- python -m [module]
"""
