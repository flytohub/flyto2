"""
Prompt Builder Module - Build AI prompts with full context

Atomic responsibility: Construct comprehensive AI prompts
Extracted from: ai_error_solver.py lines 243-321
"""

import json
from typing import Any, Dict, List


class PromptBuilderModule:
    """
    Build AI prompts with full project context

    Single responsibility: Create context-rich prompts for AI error resolution
    """

    @staticmethod
    def build_error_resolution_prompt(
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
        project_context = PromptBuilderModule._get_project_context()

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
    def _get_project_context() -> str:
        """Get Flyto2 project context description"""
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
