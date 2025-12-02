"""
LLM Orchestrator - Multi-Model Pipeline

Tries models in order: Ollama -> GPT -> Claude
Each result must pass validators before being accepted
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from src.core.utils.http_client import HTTPClient
from .validators import FormatValidator, StaticValidator, SandboxValidator
from .llm_task import LLMTask, LLMResult

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"


class LLMOrchestrator:
    """
    Orchestrate LLM requests with automatic fallback

    Flow:
    1. Try Ollama (local, fast, cheap)
    2. If fails or invalid -> Try GPT-4
    3. If fails or invalid -> Try Claude
    4. If all fail -> Raise error

    Each response validated by:
    - FormatValidator: JSON structure
    - StaticValidator: Code syntax
    - SandboxValidator: Safe execution (optional)
    """

    def __init__(self, use_sandbox: bool = False):
        self.http_client = HTTPClient()
        self.validators = [
            FormatValidator(),
            StaticValidator(),
        ]

        # SandboxValidator can be expensive, use selectively
        if use_sandbox:
            self.validators.append(SandboxValidator())

    async def solve(self, task: LLMTask) -> LLMResult:
        """
        Solve a task using multi-model pipeline

        Args:
            task: LLM task definition

        Returns:
            LLMResult with validated response

        Raises:
            UnresolvedTaskError: If all models fail
        """
        logger.info(f"Solving task: {task.task_id} (type: {task.task_type})")

        # Try each provider in order
        providers = [LLMProvider.OLLAMA, LLMProvider.OPENAI, LLMProvider.CLAUDE]
        last_error = None

        for provider in providers:
            try:
                logger.info(f"Trying provider: {provider.value}")
                result = await self._try_provider(provider, task)

                # Validate result
                if self._validate_result(result, task):
                    logger.info(f"Task solved by {provider.value}")
                    return result
                else:
                    logger.warning(f"{provider.value} result failed validation")
                    last_error = f"Validation failed: {result.validation_errors}"

            except Exception as e:
                logger.warning(f"{provider.value} failed: {e}")
                last_error = str(e)
                continue

        # All providers failed
        error_msg = f"All LLM providers failed for task {task.task_id}"
        if last_error:
            error_msg += f". Last error: {last_error}"

        raise UnresolvedTaskError(error_msg)

    async def _try_provider(
        self,
        provider: LLMProvider,
        task: LLMTask
    ) -> LLMResult:
        """Try a specific provider"""
        if provider == LLMProvider.OLLAMA:
            return await self._try_ollama(task)
        elif provider == LLMProvider.OPENAI:
            return await self._try_openai(task)
        elif provider == LLMProvider.CLAUDE:
            return await self._try_claude(task)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _try_ollama(self, task: LLMTask) -> LLMResult:
        """Try Ollama"""
        # Check if Ollama is available first
        if not self.http_client.check_ollama_available():
            raise Exception("Ollama not available")

        response = await self.http_client.ask_ollama(
            prompt=task.prompt,
            system_prompt=task.system_prompt,
            model="llama3.2",
            timeout=120,
            extract_json=(task.expected_format == "json")
        )

        if not response["success"]:
            raise Exception(response.get("error", "Ollama failed"))

        return LLMResult(
            task_id=task.task_id,
            provider=LLMProvider.OLLAMA.value,
            raw_response=response["content"],
            success=True,
            parsed_data=response.get("structured", {})
        )

    async def _try_openai(self, task: LLMTask) -> LLMResult:
        """Try OpenAI GPT-4"""
        response = await self.http_client.ask_openai(
            prompt=task.prompt,
            system_prompt=task.system_prompt,
            model="gpt-4o",
            timeout=60
        )

        if not response["success"]:
            raise Exception(response.get("error", "OpenAI failed"))

        return LLMResult(
            task_id=task.task_id,
            provider=LLMProvider.OPENAI.value,
            raw_response=response["content"],
            success=True
        )

    async def _try_claude(self, task: LLMTask) -> LLMResult:
        """Try Claude API"""
        try:
            import anthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise Exception("ANTHROPIC_API_KEY not configured")

            client = anthropic.Anthropic(api_key=api_key)

            # Build message
            message_content = task.prompt
            if task.system_prompt:
                system = task.system_prompt
            else:
                system = "You are a helpful AI assistant."

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=system,
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )

            content = message.content[0].text

            return LLMResult(
                task_id=task.task_id,
                provider=LLMProvider.CLAUDE.value,
                raw_response=content,
                success=True
            )

        except ImportError:
            raise Exception("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            raise Exception(f"Claude API failed: {e}")

    def _validate_result(self, result: LLMResult, task: LLMTask) -> bool:
        """
        Validate result with all validators

        Returns:
            True if all validators pass
        """
        for validator in self.validators:
            try:
                if not validator.validate(result, task):
                    logger.warning(f"Validator {validator.__class__.__name__} failed")
                    return False
            except Exception as e:
                logger.error(f"Validator error: {e}")
                result.validation_errors.append(f"Validator exception: {e}")
                return False

        return True


class UnresolvedTaskError(Exception):
    """Raised when no LLM provider can solve the task"""
    pass


# Singleton
_orchestrator = None


def get_llm_orchestrator(use_sandbox: bool = False) -> LLMOrchestrator:
    """Get singleton orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator(use_sandbox=use_sandbox)
    return _orchestrator


# CLI for testing
if __name__ == "__main__":
    import asyncio
    import sys

    async def test_orchestrator():
        """Test LLM orchestrator with a simple task"""

        # Create test task
        task = LLMTask(
            task_type="analysis",
            prompt="List 3 benefits of automated testing in software development",
            system_prompt="You are a software engineering expert",
            expected_format="text"
        )

        print(f"Testing LLM Orchestrator with task: {task.task_id}")
        print(f"Prompt: {task.prompt}\n")

        try:
            orchestrator = get_llm_orchestrator()
            result = await orchestrator.solve(task)

            print(f"Success! Provider: {result.provider}")
            print(f"Response:\n{result.raw_response}")

            if result.validation_errors:
                print(f"\nValidation warnings: {result.validation_errors}")

        except UnresolvedTaskError as e:
            print(f"Failed: {e}")
            sys.exit(1)

    # Run test
    asyncio.run(test_orchestrator())
