"""
Auto-Refiner - Automatically fix quality issues in generated modules
Atomic, zero coupling implementation for V3.0
"""
from typing import Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
import re


class AutoRefiner:
    """
    Atomic auto-refiner with zero coupling.

    Automatically fixes quality issues in generated modules by:
    1. Analyzing PR review results
    2. Generating targeted fixes using GPT-4o
    3. Applying fixes to the module code
    4. Validating the fixes

    Requirements:
    - Only fixes issues that can be automatically corrected
    - Preserves module functionality
    - Maintains code structure and style
    """

    def __init__(self):
        self.fixable_issues = [
            "duplicate imports",
            "missing self prefix",
            "nested function",
            "placeholder code",
            "inconsistent return format"
        ]

    def refine_module(
        self,
        module_path: str,
        pr_result: Dict[str, Any],
        openai_api_key: str
    ) -> Dict[str, Any]:
        """
        Automatically refine a module based on PR review issues.

        Args:
            module_path: Path to the module file
            pr_result: PR review result from QualityCheckerV2
            openai_api_key: OpenAI API key

        Returns:
            {
                "success": bool,
                "fixed_issues": List[str],
                "unfixed_issues": List[str],
                "refined_code": str or None,
                "score_improvement": float
            }
        """
        path = Path(module_path)

        if not path.exists():
            return {
                "success": False,
                "error": f"Module file not found: {module_path}",
                "fixed_issues": [],
                "unfixed_issues": [],
                "refined_code": None,
                "score_improvement": 0.0
            }

        # Read original code
        original_code = path.read_text()

        # Extract fixable issues from PR result
        fixable_issues = self._extract_fixable_issues(pr_result)

        if not fixable_issues:
            return {
                "success": True,
                "message": "No fixable issues found",
                "fixed_issues": [],
                "unfixed_issues": pr_result.get("issues", []),
                "refined_code": None,
                "score_improvement": 0.0
            }

        # Generate fixes using GPT-4o
        refined_code = self._generate_fixes(
            original_code,
            fixable_issues,
            openai_api_key
        )

        if not refined_code:
            return {
                "success": False,
                "error": "Failed to generate fixes",
                "fixed_issues": [],
                "unfixed_issues": pr_result.get("issues", []),
                "refined_code": None,
                "score_improvement": 0.0
            }

        # Write refined code to file
        path.write_text(refined_code)

        return {
            "success": True,
            "fixed_issues": fixable_issues,
            "unfixed_issues": self._get_unfixable_issues(pr_result, fixable_issues),
            "refined_code": refined_code,
            "score_improvement": len(fixable_issues) * 0.5  # Estimated improvement
        }

    def _extract_fixable_issues(self, pr_result: Dict[str, Any]) -> list:
        """Extract issues that can be automatically fixed."""
        fixable = []

        # Check the "issues" array from QualityCheckerV2
        for issue in pr_result.get("issues", []):
            issue_message = issue.get("message", "").lower()

            # Map specific issue messages to fixable patterns
            fixable_mappings = {
                "generic exception handler": "Only generic Exception handler",
                "error returns missing": "Error returns missing 'error' field",
                "missing parameter documentation": "Missing parameter documentation",
                "duplicate imports": "Duplicate imports found",
                "missing self prefix": "Missing self. prefix on variables",
                "nested function": "Nested function definitions",
                "placeholder code": "Placeholder or TODO code found",
                "inconsistent return": "Inconsistent return format"
            }

            for pattern_key, full_message in fixable_mappings.items():
                if pattern_key in issue_message:
                    fixable.append(issue.get("message"))
                    break

        return fixable

    def _get_unfixable_issues(self, pr_result: Dict[str, Any], fixed: list) -> list:
        """Get issues that cannot be automatically fixed."""
        all_issues = []

        for issue in pr_result.get("issues", []):
            issue_message = issue.get("message", "")
            all_issues.append(issue_message)

        return [issue for issue in all_issues if issue not in fixed]

    def _generate_fixes(
        self,
        original_code: str,
        issues: list,
        openai_api_key: str
    ) -> Optional[str]:
        """Generate fixed code using GPT-4o."""
        # Build specific fix instructions for each issue
        fix_instructions = {
            "Only generic Exception handler": """
- Replace generic 'except Exception' with specific exception types (ValueError, TypeError, IOError, etc.)
- Keep ONE final 'except Exception' that raises RuntimeError with module name
- Example:
  try:
      ...
  except ValueError as e:
      return {"ok": False, "output": {}, "error": {"message": f"Invalid value: {e}"}, "meta": {}}
  except TypeError as e:
      return {"ok": False, "output": {}, "error": {"message": f"Invalid type: {e}"}, "meta": {}}
  except Exception as e:
      raise RuntimeError(f"{self.module_name} execution failed: {e}")
""",
            "Error returns missing 'error' field": """
- Ensure ALL returns with "ok": False have an "error" field with a {"message": "..."} dict
- NEVER use {"error": None} when "ok": False
- Example: {"ok": False, "output": {}, "error": {"message": "description"}, "meta": {}}
""",
            "Missing parameter documentation": """
- Add complete parameter documentation in the class docstring
- Format: param_name (type): Clear description
- Example:
  Parameters:
      text (str): The input text string to be reversed
      case_sensitive (bool, optional): Whether to preserve case. Defaults to True.
"""
        }

        fix_details = []
        for issue in issues:
            for pattern, instruction in fix_instructions.items():
                if pattern in issue:
                    fix_details.append(instruction)
                    break

        prompt = f"""You are a SENIOR Python code refactoring expert. Fix the issues in the code below with SURGICAL PRECISION.

ISSUES TO FIX:
{chr(10).join(f'- {issue}' for issue in issues)}

SPECIFIC FIX INSTRUCTIONS:
{chr(10).join(fix_details)}

ORIGINAL CODE:
```python
{original_code}
```

CRITICAL REQUIREMENTS:
1. Fix ONLY the listed issues - DO NOT add features or refactor unnecessarily
2. PRESERVE all functionality exactly
3. Maintain EXACT code structure and indentation
4. Keep ALL comments and docstrings unchanged (except when fixing documentation)
5. Do NOT remove nested try-except - instead flatten it properly
6. Return ONLY the complete fixed Python code (no markdown, no explanations)

Return the fixed code now:"""

        try:
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Python code refactoring expert. Return ONLY the complete fixed Python code with no markdown formatting or explanations. Make minimal, targeted changes to fix the specific issues."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                timeout=60
            )

            refined_code = response.choices[0].message.content

            # Remove markdown code blocks if present
            refined_code = re.sub(r'^```python\s*\n', '', refined_code)
            refined_code = re.sub(r'\n```\s*$', '', refined_code)
            refined_code = refined_code.strip()

            # Sanity check - code should have similar length
            if len(refined_code) < len(original_code) * 0.8:
                print(f"Warning: Refined code suspiciously short ({len(refined_code)} vs {len(original_code)} chars)")
                return None

            return refined_code

        except Exception as e:
            print(f"Failed to generate fixes: {e}")
            return None
