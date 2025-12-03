"""
AutoRefiner V2 - Multi-pass code refinement with atomic components

Design principles:
1. Each component has ONE responsibility
2. Pure functions where possible
3. Testable in isolation
4. Clear data flow
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
from openai import OpenAI


# ============================================================================
# Data structures
# ============================================================================

@dataclass
class Issue:
    """Single quality issue detected by QualityChecker"""
    type: str  # e.g., "generic_exception", "nested_try_except"
    message: str
    location: str = ""
    deduction: float = 0.0


@dataclass
class QualityReport:
    """Quality evaluation result"""
    score: float
    issues: List[Issue]
    passed: bool


@dataclass
class RoundResult:
    """Result of a single refinement round"""
    round_index: int
    focus_types: List[str]
    before_score: float
    after_score: float
    issues_before: List[Issue]
    issues_after: List[Issue]
    code_changed: bool
    improvement: float = field(init=False)

    def __post_init__(self):
        self.improvement = self.after_score - self.before_score


@dataclass
class RefineResult:
    """Final multi-pass refinement result"""
    initial_score: float
    final_score: float
    final_code: str
    rounds: List[RoundResult]
    achieved_target: bool
    total_improvement: float = field(init=False)

    def __post_init__(self):
        self.total_improvement = self.final_score - self.initial_score


# ============================================================================
# Protocols (dependency injection)
# ============================================================================

class QualityChecker(Protocol):
    """Interface for quality evaluation"""
    def review_module(self, module_path: str) -> Dict[str, Any]:
        """Returns PR review result with score and issues"""
        ...


# ============================================================================
# Atomic components
# ============================================================================

class IssueFilter:
    """Filter issues by type"""

    @staticmethod
    def filter_by_types(issues: List[Issue], types: List[str]) -> List[Issue]:
        """Filter issues matching any of the given types"""
        return [i for i in issues if i.type in types]

    @staticmethod
    def has_any_type(issues: List[Issue], types: List[str]) -> bool:
        """Check if any issue matches the given types"""
        return any(i.type in types for i in issues)


class IssueConverter:
    """Convert between different issue formats"""

    @staticmethod
    def from_pr_result(pr_result: Dict[str, Any]) -> List[Issue]:
        """Convert PR review result to Issue list"""
        issues = []
        for item in pr_result.get("issues", []):
            issues.append(Issue(
                type=IssueConverter._infer_type(item["message"]),
                message=item["message"],
                deduction=item.get("deduction", 0.0)
            ))
        return issues

    @staticmethod
    def _infer_type(message: str) -> str:
        """Infer issue type from message"""
        msg_lower = message.lower()

        if "generic exception" in msg_lower:
            return "generic_exception"
        elif "nested" in msg_lower:
            return "nested_try_except"
        elif "parameter description" in msg_lower or "missing parameter" in msg_lower:
            return "placeholder_docstring"
        elif "error returns missing" in msg_lower:
            return "return_format_inconsistent"
        elif "duplicate import" in msg_lower:
            return "duplicate_imports"
        else:
            return "unknown"


class PromptBuilder:
    """Build prompts for code refinement"""

    SYSTEM_PROMPT = """You are an expert Python refactoring assistant specialized in SMALL, PRECISE fixes.

Context:
- You work inside the Flyto2 codebase.
- A QualityCheckerV2 reports atomic issues (nested try/except, generic exceptions, placeholders, etc.)
- AutoRefiner may call you MULTIPLE TIMES on the same file (multi-pass refinement)
- Your job: incrementally improve code quality while preserving behavior

Your goals:
1. Fix ONLY the issues listed for this round ("focus_issues_this_round")
2. Make REAL, CONCRETE code changes that resolve those issues
3. Do NOT claim fixed unless truly fixed in code
4. Preserve module's public behavior, interface, return format
5. Keep code readable and simple

Absolute rules:
- Output ONLY the FULL UPDATED PYTHON FILE. No explanations, no Markdown, no diff
- Do NOT add new dependencies
- Do NOT change module name, class name, @register_module decorator
- Do NOT change public contract (parameters, return type) unless issue requires it
- Do NOT introduce nested try/except blocks
- Avoid `except Exception:` or bare `except:`; use specific exception types
- Replace placeholder docstrings like "Parameter description" with concrete descriptions
- Keep imports minimal and non-duplicated

Multi-pass behavior:
- Each call is one "round" of refinement
- You receive: current code, remaining issues, focus issues for THIS round
- If you can't fully fix an issue, make partial progress while keeping code correct
- Never introduce new issues of the same type you're fixing

Return ONLY the complete, updated Python source code. No explanations."""

    @staticmethod
    def build_user_prompt(
        round_index: int,
        max_rounds: int,
        module_path: str,
        current_score: float,
        target_score: float,
        current_code: str,
        all_issues: List[Issue],
        focus_issues: List[Issue],
    ) -> str:
        """Build user prompt for a refinement round"""

        def format_issues(issues: List[Issue]) -> str:
            if not issues:
                return "(none)"
            lines = []
            for i, issue in enumerate(issues, start=1):
                lines.append(f"{i}. [{issue.type}] {issue.message}")
            return "\n".join(lines)

        return f"""Refinement ROUND {round_index} of {max_rounds}

Module path: {module_path}
Current score: {current_score:.1f}/10.0
Target score: {target_score:.1f}/10.0

CURRENT CODE:
```python
{current_code}
```

ALL REMAINING ISSUES:
{format_issues(all_issues)}

FOCUS ISSUES FOR THIS ROUND:
{format_issues(focus_issues)}

Fix ONLY the focus issues. Make concrete changes.
Return ONLY the full updated Python file (no explanations, no Markdown)."""


class CodeValidator:
    """Validate generated code"""

    @staticmethod
    def is_valid_python(code: str) -> bool:
        """Check if code is syntactically valid Python"""
        try:
            compile(code, "<string>", "exec")
            return True
        except SyntaxError:
            return False

    @staticmethod
    def strip_markdown(code: str) -> str:
        """Remove markdown code fences if present"""
        code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'\n```\s*$', '', code, flags=re.MULTILINE)
        return code.strip()

    @staticmethod
    def has_significant_change(old_code: str, new_code: str) -> bool:
        """Check if code actually changed (more than just whitespace)"""
        old_normalized = re.sub(r'\s+', ' ', old_code).strip()
        new_normalized = re.sub(r'\s+', ' ', new_code).strip()
        return old_normalized != new_normalized

    @staticmethod
    def check_length_reasonable(old_code: str, new_code: str, min_ratio: float = 0.7) -> bool:
        """Check if new code length is reasonable (not truncated)"""
        if not new_code or not old_code:
            return False
        ratio = len(new_code) / len(old_code)
        return ratio >= min_ratio


class RoundPlanner:
    """Plan which issues to focus on each round"""

    # Default focus plan: prioritize by impact
    DEFAULT_PLAN = [
        ["generic_exception", "nested_try_except"],  # Round 1: Critical exception issues
        ["placeholder_docstring", "missing_param_docs"],  # Round 2: Documentation
        ["return_format_inconsistent", "duplicate_imports"],  # Round 3: Format & cleanup
    ]

    @staticmethod
    def get_focus_issues_for_round(
        round_index: int,
        all_issues: List[Issue],
        plan: Optional[List[List[str]]] = None
    ) -> List[Issue]:
        """Get focus issues for a specific round"""
        if plan is None:
            plan = RoundPlanner.DEFAULT_PLAN

        if round_index < 1 or round_index > len(plan):
            return []

        focus_types = plan[round_index - 1]
        return IssueFilter.filter_by_types(all_issues, focus_types)


# ============================================================================
# Round executor (atomic single-pass refinement)
# ============================================================================

class RoundExecutor:
    """Execute a single refinement round"""

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)

    async def execute_round(
        self,
        round_index: int,
        max_rounds: int,
        module_path: str,
        current_code: str,
        current_score: float,
        target_score: float,
        all_issues: List[Issue],
        focus_issues: List[Issue],
    ) -> str:
        """Execute one refinement round, return refined code"""

        system_prompt = PromptBuilder.SYSTEM_PROMPT
        user_prompt = PromptBuilder.build_user_prompt(
            round_index=round_index,
            max_rounds=max_rounds,
            module_path=module_path,
            current_score=current_score,
            target_score=target_score,
            current_code=current_code,
            all_issues=all_issues,
            focus_issues=focus_issues,
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            timeout=60
        )

        refined_code = response.choices[0].message.content
        refined_code = CodeValidator.strip_markdown(refined_code)

        return refined_code


# ============================================================================
# Multi-pass coordinator
# ============================================================================

class MultiPassRefiner:
    """Coordinate multi-pass refinement process"""

    def __init__(
        self,
        quality_checker: QualityChecker,
        openai_api_key: str,
        max_rounds: int = 2,
        target_score: float = 9.5,
        min_improvement: float = 0.1,
    ):
        self.quality_checker = quality_checker
        self.executor = RoundExecutor(openai_api_key)
        self.max_rounds = max_rounds
        self.target_score = target_score
        self.min_improvement = min_improvement

    def refine_module(
        self,
        module_path: str,
        initial_code: str,
        initial_pr_result: Dict[str, Any],
    ) -> RefineResult:
        """
        Run multi-pass refinement on a module

        Args:
            module_path: Path to the module file
            initial_code: Initial module code
            initial_pr_result: Initial PR review result

        Returns:
            RefineResult with final code and history
        """

        initial_score = initial_pr_result["score"]
        current_code = initial_code
        current_score = initial_score
        current_issues = IssueConverter.from_pr_result(initial_pr_result)

        rounds: List[RoundResult] = []

        # Already达标
        if current_score >= self.target_score:
            return RefineResult(
                initial_score=initial_score,
                final_score=current_score,
                final_code=current_code,
                rounds=rounds,
                achieved_target=True,
            )

        # Multi-pass refinement
        for round_index in range(1, self.max_rounds + 1):
            focus_issues = RoundPlanner.get_focus_issues_for_round(
                round_index, current_issues
            )

            # No focus issues for this round
            if not focus_issues:
                # If no issues at all, we're done
                if not current_issues:
                    break
                # Otherwise continue to next round
                continue

            before_score = current_score
            issues_before = current_issues

            # Execute refinement round
            try:
                refined_code = self._execute_round_sync(
                    round_index=round_index,
                    max_rounds=self.max_rounds,
                    module_path=module_path,
                    current_code=current_code,
                    current_score=current_score,
                    target_score=self.target_score,
                    all_issues=current_issues,
                    focus_issues=focus_issues,
                )
            except Exception as e:
                print(f"   ❌ Round {round_index} refinement failed: {e}")
                break

            # Validate refined code
            if not CodeValidator.is_valid_python(refined_code):
                print(f"   ❌ Round {round_index} produced invalid Python")
                break

            if not CodeValidator.check_length_reasonable(current_code, refined_code):
                print(f"   ❌ Round {round_index} produced suspiciously short code")
                break

            code_changed = CodeValidator.has_significant_change(current_code, refined_code)

            if not code_changed:
                print(f"   ⚠️  Round {round_index} produced no meaningful changes")
                rounds.append(RoundResult(
                    round_index=round_index,
                    focus_types=[i.type for i in focus_issues],
                    before_score=before_score,
                    after_score=before_score,
                    issues_before=issues_before,
                    issues_after=issues_before,
                    code_changed=False,
                ))
                break

            # Write refined code and re-evaluate
            Path(module_path).write_text(refined_code)
            current_code = refined_code

            pr_result = self.quality_checker.review_module(module_path)
            current_score = pr_result["score"]
            current_issues = IssueConverter.from_pr_result(pr_result)

            # Record round result
            round_result = RoundResult(
                round_index=round_index,
                focus_types=[i.type for i in focus_issues],
                before_score=before_score,
                after_score=current_score,
                issues_before=issues_before,
                issues_after=current_issues,
                code_changed=True,
            )
            rounds.append(round_result)

            # Check if target reached
            if current_score >= self.target_score:
                print(f"   🎉 Target score reached: {current_score:.1f}/10.0")
                break

            # Check if improvement is significant
            if round_result.improvement < self.min_improvement:
                print(f"   ⚠️  Minimal improvement ({round_result.improvement:+.2f}), stopping")
                break

        achieved = current_score >= self.target_score

        return RefineResult(
            initial_score=initial_score,
            final_score=current_score,
            final_code=current_code,
            rounds=rounds,
            achieved_target=achieved,
        )

    def _execute_round_sync(self, **kwargs) -> str:
        """Synchronous wrapper for execute_round"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.executor.execute_round(**kwargs)
        )
