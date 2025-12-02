"""
LLM Result Validators

Three-layer validation:
1. FormatValidator: JSON structure
2. StaticValidator: Code syntax
3. SandboxValidator: Safe execution
"""

import ast
import json
import logging
from typing import Dict, Any
from .llm_task import LLMTask, LLMResult

logger = logging.getLogger(__name__)


class BaseValidator:
    """Base validator interface"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """
        Validate result

        Args:
            result: LLM result to validate
            task: Original task

        Returns:
            True if valid, False otherwise
        """
        raise NotImplementedError


class FormatValidator(BaseValidator):
    """Validate JSON structure and schema"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """Check if result matches expected format"""
        try:
            # If not expecting JSON, pass through
            if task.expected_format != "json":
                if task.expected_format == "diff":
                    return self._validate_diff_format(result.raw_response)
                return True

            # Parse JSON
            data = json.loads(result.raw_response)

            # Check required fields based on task type
            if task.expected_schema:
                return self._validate_json_structure(data, task.expected_schema)

            return True

        except json.JSONDecodeError as e:
            logger.warning(f"Format validation failed: Invalid JSON - {e}")
            result.validation_errors.append(f"Invalid JSON: {e}")
            return False
        except Exception as e:
            logger.error(f"Format validation error: {e}")
            result.validation_errors.append(f"Format error: {e}")
            return False

    def _validate_json_structure(self, data: Dict, schema: Dict) -> bool:
        """Validate JSON against schema"""
        if not schema:
            return True

        # Simple schema validation (can be enhanced with jsonschema library)
        for key, value_type in schema.items():
            if key not in data:
                logger.warning(f"Missing required field: {key}")
                return False

        return True

    def _validate_diff_format(self, text: str) -> bool:
        """Validate unified diff format"""
        lines = text.split('\n')
        has_diff_header = any(line.startswith('diff --git') for line in lines)
        has_hunks = any(line.startswith('@@') for line in lines)

        return has_diff_header and has_hunks


class StaticValidator(BaseValidator):
    """Validate Python code syntax"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """Check if generated code is syntactically valid"""
        if task.task_type != "code_generation":
            return True

        try:
            # Extract Python code from result
            code = self._extract_code(result.raw_response)

            if not code:
                return True  # No code to validate

            # Parse with AST
            ast.parse(code)

            # Check for dangerous imports
            if not self._check_safe_imports(code):
                logger.warning("Static validation failed: Dangerous imports detected")
                result.validation_errors.append("Dangerous imports detected")
                return False

            return True

        except SyntaxError as e:
            logger.warning(f"Static validation failed: Syntax error - {e}")
            result.validation_errors.append(f"Syntax error: {e}")
            return False
        except Exception as e:
            logger.error(f"Static validation error: {e}")
            result.validation_errors.append(f"Static validation error: {e}")
            return False

    def _extract_code(self, text: str) -> str:
        """Extract Python code from markdown or raw text"""
        # Look for ```python ... ```
        if '```python' in text:
            start = text.find('```python') + 9
            end = text.find('```', start)
            if end > start:
                return text[start:end].strip()

        # Look for ```\n...\n```
        if '```' in text:
            start = text.find('```') + 3
            end = text.find('```', start)
            if end > start:
                return text[start:end].strip()

        # Assume entire text is code
        return text

    def _check_safe_imports(self, code: str) -> bool:
        """Check for dangerous imports"""
        dangerous_modules = ['os.system', 'subprocess', 'eval', 'exec', '__import__']

        for danger in dangerous_modules:
            if danger in code:
                return False

        return True


class SandboxValidator(BaseValidator):
    """Validate code execution in sandbox (expensive, use sparingly)"""

    def validate(self, result: LLMResult, task: LLMTask) -> bool:
        """Run code in isolated sandbox"""
        # This is expensive and requires proper sandboxing
        # For V4, we'll skip this or use it selectively

        logger.info("SandboxValidator: Skipped (not implemented)")
        return True
