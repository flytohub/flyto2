"""
AI Consulter Module - Consult LLM for error solutions

Atomic responsibility: Query AI for error analysis and solutions
Extracted from: ai_error_solver.py lines 220-367
"""

import re
import json
from typing import Any, Dict, List, Optional
from src.core.utils.http_client import HTTPClient
from src.core.utils.notifier import notify


class AIConsulterModule:
    """
    Consult AI (OpenAI GPT-4o) for error solutions

    Single responsibility: AI consultation using OpenAI
    """

    @staticmethod
    async def consult(
        prompt: str,
        notify_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Consult AI for error solution

        Args:
            prompt: Complete prompt with error context
            notify_callback: Optional notification callback

        Returns:
            {
                "success": bool,
                "full_response": str,
                "structured": dict,  # Extracted JSON
                "summary": str,
                "source": str  # openai
            }
        """
        # Use OpenAI GPT-4o only
        await notify("🤖 Consulting OpenAI GPT-4o...", notify_callback)
        result = await AIConsulterModule._ask_openai(prompt, notify_callback)

        if result["success"]:
            return result

        return {"success": False, "error": "OpenAI service unavailable"}

    @staticmethod
    async def _ask_openai(
        prompt: str,
        notify_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Ask OpenAI GPT-4o for solution"""
        try:
            system_prompt = "You are an expert DevOps and Python engineer. Always respond with valid JSON."

            response = await HTTPClient.ask_openai(
                prompt=prompt,
                model="gpt-4o",  # Use GPT-4o for highest quality
                system_prompt=system_prompt,
                timeout=60
            )

            if response["success"]:
                content = response["content"]

                # Extract JSON
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        structured = json.loads(json_match.group())

                        if "solution_summary" in structured:
                            return {
                                "success": True,
                                "full_response": content,
                                "structured": structured,
                                "summary": structured.get("solution_summary", ""),
                                "source": "openai"
                            }
                    except json.JSONDecodeError:
                        pass

            return {"success": False, "error": "Invalid response from OpenAI"}

        except Exception as e:
            await notify(f"⚠️ OpenAI error: {e}", notify_callback)
            return {"success": False, "error": str(e)}
