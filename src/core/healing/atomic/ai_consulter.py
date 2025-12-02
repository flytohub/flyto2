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
    Consult AI (Ollama/OpenAI/Claude) for error solutions

    Single responsibility: AI consultation with fallback logic
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
                "source": str  # ollama/openai/claude
            }
        """
        # Try Ollama first (free, local)
        await notify("🤖 Consulting Ollama...", notify_callback)
        result = await AIConsulterModule._ask_ollama(prompt, notify_callback)

        if result["success"]:
            return result

        # Fallback to OpenAI if configured
        await notify("⚠️ Ollama unavailable, trying OpenAI...", notify_callback)
        result = await AIConsulterModule._ask_openai(prompt, notify_callback)

        if result["success"]:
            return result

        # TODO: Fallback to Claude if configured

        return {"success": False, "error": "All AI services unavailable"}

    @staticmethod
    async def _ask_ollama(
        prompt: str,
        notify_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Ask Ollama for solution"""
        try:
            system_prompt = "You are an expert DevOps and Python engineer. Always respond with valid JSON."

            response = await HTTPClient.ask_ollama(
                prompt=prompt,
                model="llama3.2",
                system_prompt=system_prompt,
                timeout=120,
                extract_json=True
            )

            if response["success"] and response.get("structured"):
                structured = response["structured"]

                # Validate required fields
                if "solution_summary" in structured:
                    return {
                        "success": True,
                        "full_response": response["content"],
                        "structured": structured,
                        "summary": structured.get("solution_summary", ""),
                        "source": "ollama"
                    }

            return {"success": False, "error": "Invalid response from Ollama"}

        except Exception as e:
            await notify(f"⚠️ Ollama error: {e}", notify_callback)
            return {"success": False, "error": str(e)}

    @staticmethod
    async def _ask_openai(
        prompt: str,
        notify_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Ask OpenAI for solution"""
        try:
            system_prompt = "You are an expert DevOps and Python engineer. Always respond with valid JSON."

            response = await HTTPClient.ask_openai(
                prompt=prompt,
                model="gpt-4",
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
