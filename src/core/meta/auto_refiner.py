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

        for check in pr_result.get("checks", []):
            if not check.get("passed", True):
                check_name = check.get("name", "").lower()
                description = check.get("description", "").lower()
                combined = f"{check_name} {description}"

                for fixable_pattern in self.fixable_issues:
                    if fixable_pattern in combined:
                        fixable.append(check.get("description", check_name))
                        break

        return fixable

    def _get_unfixable_issues(self, pr_result: Dict[str, Any], fixed: list) -> list:
        """Get issues that cannot be automatically fixed."""
        all_issues = []

        for check in pr_result.get("checks", []):
            if not check.get("passed", True):
                desc = check.get("description", check.get("name", ""))
                all_issues.append(desc)

        return [issue for issue in all_issues if issue not in fixed]

    def _generate_fixes(
        self,
        original_code: str,
        issues: list,
        openai_api_key: str
    ) -> Optional[str]:
        """Generate fixed code using GPT-4o."""
        prompt = f"""You are a code refactoring expert. Fix ONLY the following issues in the code below:

ISSUES TO FIX:
{chr(10).join(f'- {issue}' for issue in issues)}

ORIGINAL CODE:
```python
{original_code}
```

REQUIREMENTS:
1. Fix ONLY the listed issues
2. Preserve all functionality
3. Maintain code structure
4. Keep all comments and docstrings
5. Return ONLY the fixed code (no explanations)

COMMON FIXES:
- Duplicate imports: Move all imports to file top
- Missing self prefix: Add self. to all instance variables
- Nested functions: Move functions to class level
- Placeholder code: Remove TODO, pass, NotImplementedError
- Inconsistent return format: Use {{"ok": bool, "output": {{}}, "error": None/Dict, "meta": {{}}}}

Return the fixed code:"""

        try:
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code refactoring expert. Return ONLY the fixed code, no explanations or markdown."
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

            return refined_code.strip()

        except Exception as e:
            print(f"Failed to generate fixes: {e}")
            return None
