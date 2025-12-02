"""
HTTP Client - Unified HTTP request handling

Purpose: Eliminate duplicate HTTP request code
- Replaces duplicate Ollama/OpenAI request implementations
- Provides retry logic and timeout handling
- Consistent error handling
"""

import os
import re
import json
import asyncio
from typing import Any, Dict, Optional
import requests


class HTTPClient:
    """
    Unified HTTP client with retry logic

    Eliminates duplicate HTTP code in:
    - ai_error_solver.py (_ask_ollama)
    - self_healing_practice.py (_ask_ollama)
    - telegram_bot_v2.py (ask_ollama, ask_openai)
    - interactive_evolution_bot.py (ask_ollama, ask_openai)
    """

    @staticmethod
    async def post_json(
        url: str,
        data: Dict[str, Any],
        timeout: int = 30,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        POST JSON data with retry logic

        Args:
            url: Target URL
            data: JSON data to post
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts

        Returns:
            Response JSON dict

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    url,
                    json=data,
                    timeout=timeout
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    error = f"HTTP {response.status_code}: {response.text[:200]}"
                    if attempt < max_retries:
                        await asyncio.sleep(1 * attempt)  # Exponential backoff
                        continue
                    raise Exception(error)

            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    await asyncio.sleep(1 * attempt)
                    continue
                raise Exception(f"Request timeout after {max_retries} attempts")

            except Exception as e:
                if attempt < max_retries:
                    await asyncio.sleep(1 * attempt)
                    continue
                raise

        raise Exception(f"Failed after {max_retries} attempts")

    @staticmethod
    async def ask_ollama(
        prompt: str,
        model: str = "llama3.2",
        system_prompt: Optional[str] = None,
        timeout: int = 120,
        extract_json: bool = False
    ) -> Dict[str, Any]:
        """
        Query Ollama with standardized interface

        Args:
            prompt: User prompt
            model: Ollama model name
            system_prompt: Optional system prompt
            timeout: Request timeout
            extract_json: Whether to extract JSON from response

        Returns:
            {
                "success": bool,
                "content": str,  # Full response
                "structured": dict,  # Extracted JSON (if extract_json=True)
                "error": str  # Error message (if failed)
            }
        """
        try:
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            response_json = await HTTPClient.post_json(
                f"{ollama_url}/api/chat",
                data={
                    "model": model,
                    "messages": messages,
                    "stream": False
                },
                timeout=timeout
            )

            content = response_json.get('message', {}).get('content', '')

            result = {
                "success": True,
                "content": content
            }

            # Extract JSON if requested
            if extract_json:
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        result["structured"] = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        result["structured"] = {}
                else:
                    result["structured"] = {}

            return result

        except Exception as e:
            return {
                "success": False,
                "content": "",
                "error": str(e)
            }

    @staticmethod
    async def ask_openai(
        prompt: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Query OpenAI with standardized interface

        Args:
            prompt: User prompt
            model: OpenAI model name
            system_prompt: Optional system prompt
            timeout: Request timeout

        Returns:
            {
                "success": bool,
                "content": str,
                "error": str  # If failed
            }
        """
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "content": "",
                    "error": "OPENAI_API_KEY not configured"
                }

            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages
                },
                timeout=timeout
            )

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return {
                    "success": True,
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "content": "",
                    "error": f"OpenAI API error: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "content": "",
                "error": str(e)
            }

    @staticmethod
    def estimate_confidence(response: str) -> float:
        """
        Estimate confidence from AI response

        Args:
            response: AI response text

        Returns:
            Confidence score (0.0-1.0)
        """
        response_lower = response.lower()

        # High confidence indicators
        if any(word in response_lower for word in ['definitely', 'certain', 'sure', '確定', '肯定']):
            return 0.9

        # Medium confidence
        if any(word in response_lower for word in ['probably', 'likely', '可能', '應該']):
            return 0.7

        # Low confidence
        if any(word in response_lower for word in ['maybe', 'perhaps', 'might', '也許', '或許']):
            return 0.5

        # Uncertain
        if any(word in response_lower for word in ['don\'t know', 'unsure', 'unclear', '不確定', '不清楚']):
            return 0.3

        # Default medium-high confidence
        return 0.75
