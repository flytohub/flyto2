"""
AutoRefiner V3 (Synchronous Edition)
Zero-async, zero-event-loop-conflicts, atomic multi-pass refinement system.

Design Principles:
1. 100% synchronous — fully compatible with FastAPI, pytest, bots, and any running event loop.
2. Atomic components — each class has exactly one responsibility.
3. Deterministic multi-pass refinement with score tracking.
4. No behavior change to existing code except removing async issues.
"""

from __future__ import annotations
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, TYPE_CHECKING
from openai import OpenAI

if TYPE_CHECKING:
    from src.core.metrics.collector import MetricsCollector


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Issue:
    type: str
    message: str
    location: str = ""
    deduction: float = 0.0


@dataclass
class QualityReport:
    score: float
    issues: List[Issue]
    passed: bool


@dataclass
class RoundResult:
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
    initial_score: float
    final_score: float
    final_code: str
    rounds: List[RoundResult]
    achieved_target: bool
    total_improvement: float = field(init=False)

    def __post_init__(self):
        self.total_improvement = self.final_score - self.initial_score


# ============================================================================
# Protocol for Dependency Injection
# ============================================================================

class QualityChecker(Protocol):
    def review_module(self, module_path: str) -> Dict[str, Any]:
        ...


# ============================================================================
# Atomic Components
# ============================================================================

class IssueFilter:
    @staticmethod
    def filter_by_types(issues: List[Issue], types: List[str]) -> List[Issue]:
        return [i for i in issues if i.type in types]

    @staticmethod
    def has_any_type(issues: List[Issue], types: List[str]) -> bool:
        return any(i.type in types for i in issues)


class IssueConverter:
    @staticmethod
    def from_pr_result(pr_result: Dict[str, Any]) -> List[Issue]:
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
        msg = message.lower()
        if "generic exception" in msg:
            return "generic_exception"
        if "nested" in msg:
            return "nested_try_except"
        if "parameter description" in msg or "parameter documentation" in msg:
            return "placeholder_docstring"
        if "duplicate import" in msg:
            return "duplicate_imports"
        if "file size" in msg and "limit" in msg:
            return "missing_file_size_check"
        if "error" in msg and "missing" in msg and "field" in msg:
            return "missing_error_field"
        if "return" in msg and "missing" in msg:
            return "return_format_inconsistent"
        return "unknown"


class PromptBuilder:
    SYSTEM_PROMPT = """You are an expert Python refactoring assistant specialized in SMALL, PRECISE fixes.
Your job: fix ONLY the focus issues listed for this round.
Rules:
- Output ONLY the FULL UPDATED PYTHON FILE (no Markdown).
- No new dependencies.
- No changing module signature.
- Fix real issues, do NOT claim fixed unless code changes.
- Absolutely NO nested function definitions.
"""

    @staticmethod
    def build_user_prompt(
        current_code: str,
        round_index: int,
        max_rounds: int,
        all_issues: List[Issue],
        focus_issues: List[Issue],
        before_score: float,
        target_score: float,
        module_path: str
    ) -> str:

        def fmt(items: List[Issue]):
            if not items:
                return "(none)"
            return "\n".join(f"- [{i.type}] {i.message}" for i in items)

        return f"""
Refinement ROUND {round_index}/{max_rounds}
Module: {module_path}
Current score: {before_score:.1f}
Target score: {target_score:.1f}

ALL ISSUES:
{fmt(all_issues)}

FOCUS ISSUES THIS ROUND:
{fmt(focus_issues)}

CURRENT CODE:
{current_code}

Fix ONLY the focus issues. Return ONLY the full updated Python file.
"""


class CodeValidator:
    @staticmethod
    def is_valid_python(code: str) -> bool:
        try:
            compile(code, "<refined>", "exec")
            return True
        except SyntaxError:
            return False

    @staticmethod
    def strip_markdown(text: str) -> str:
        text = re.sub(r"^```python\s*", "", text.strip())
        text = re.sub(r"```$", "", text)
        return text.strip()

    @staticmethod
    def has_meaningful_change(old: str, new: str) -> bool:
        return re.sub(r"\s+", " ", old).strip() != re.sub(r"\s+", " ", new).strip()

    @staticmethod
    def length_ok(old: str, new: str, min_ratio=0.70) -> bool:
        return len(new) >= len(old) * min_ratio


class RoundPlanner:
    DEFAULT_PLAN = [
        ["generic_exception", "nested_try_except"],   # Round 1
        ["placeholder_docstring", "missing_error_field"],  # Round 2
        ["missing_file_size_check"],                  # Round 3
        ["return_format_inconsistent", "duplicate_imports"],  # Round 4
    ]

    @staticmethod
    def focus_for_round(index: int, issues: List[Issue]):
        if index > len(RoundPlanner.DEFAULT_PLAN):
            return []
        wanted = RoundPlanner.DEFAULT_PLAN[index - 1]
        return IssueFilter.filter_by_types(issues, wanted)


# ============================================================================
# RoundExecutor (synchronous)
# ============================================================================

class RoundExecutor:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def refine_once(
        self,
        current_code: str,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        """One synchronous refinement call"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            timeout=60
        )

        refined = response.choices[0].message.content
        return CodeValidator.strip_markdown(refined)


# ============================================================================
# Multi-pass Refiner (synchronous)
# ============================================================================

class MultiPassRefiner:

    def __init__(
        self,
        quality_checker: QualityChecker,
        openai_api_key: str,
        max_rounds: int = 3,
        target_score: float = 9.5,
        min_improvement: float = 0.1,
        metrics_collector: Optional['MetricsCollector'] = None,
        model_name: str = "gpt-4o"
    ):
        self.qc = quality_checker
        self.executor = RoundExecutor(openai_api_key)
        self.max_rounds = max_rounds
        self.target = target_score
        self.min_improvement = min_improvement
        self.metrics_collector = metrics_collector
        self.model_name = model_name

    def refine_module(
        self,
        module_path: str,
        initial_code: str,
        initial_result: Dict[str, Any]
    ) -> RefineResult:

        current_code = initial_code
        current_score = initial_result["score"]
        issues = IssueConverter.from_pr_result(initial_result)

        rounds: List[RoundResult] = []

        if current_score >= self.target:
            result = RefineResult(
                initial_score=current_score,
                final_score=current_score,
                final_code=current_code,
                rounds=[],
                achieved_target=True,
            )
            # Collect metrics even if no refinement needed
            if self.metrics_collector:
                self._record_metrics(module_path, result, initial_code)
            return result

        for r in range(1, self.max_rounds + 1):
            focus = RoundPlanner.focus_for_round(r, issues)
            if not focus:
                continue

            before_score = current_score
            issues_before = issues

            user_prompt = PromptBuilder.build_user_prompt(
                current_code=current_code,
                round_index=r,
                max_rounds=self.max_rounds,
                all_issues=issues,
                focus_issues=focus,
                before_score=current_score,
                target_score=self.target,
                module_path=module_path
            )

            refined_code = self.executor.refine_once(
                current_code=current_code,
                system_prompt=PromptBuilder.SYSTEM_PROMPT,
                user_prompt=user_prompt
            )

            if not CodeValidator.is_valid_python(refined_code):
                break

            if not CodeValidator.length_ok(current_code, refined_code):
                break

            changed = CodeValidator.has_meaningful_change(current_code, refined_code)
            if not changed:
                rounds.append(RoundResult(
                    round_index=r,
                    focus_types=[i.type for i in focus],
                    before_score=before_score,
                    after_score=before_score,
                    issues_before=issues_before,
                    issues_after=issues_before,
                    code_changed=False,
                ))
                break

            Path(module_path).write_text(refined_code)
            current_code = refined_code

            # Re-evaluate quality
            eval_result = self.qc.review_module(module_path)
            current_score = eval_result["score"]
            issues = IssueConverter.from_pr_result(eval_result)

            rounds.append(RoundResult(
                round_index=r,
                focus_types=[i.type for i in focus],
                before_score=before_score,
                after_score=current_score,
                issues_before=issues_before,
                issues_after=issues,
                code_changed=True,
            ))

            if current_score >= self.target:
                break

            if current_score - before_score < self.min_improvement:
                break

        result = RefineResult(
            initial_score=initial_result["score"],
            final_score=current_score,
            final_code=current_code,
            rounds=rounds,
            achieved_target=current_score >= self.target,
        )

        # Collect metrics if enabled
        if self.metrics_collector:
            self._record_metrics(module_path, result, initial_code)

        return result

    def _record_metrics(
        self,
        module_path: str,
        result: RefineResult,
        initial_code: str
    ) -> None:
        """Record metrics for this refine session"""
        try:
            # Extract module name from path
            module_name = Path(module_path).stem

            # Record module metric first to get ID
            module_metrics_id = self.metrics_collector.record_module_metric(
                module_name=module_name,
                task_description=f"Auto-refine module: {module_name}",
                initial_score=result.initial_score,
                final_score=result.final_score,
                attempts=len(result.rounds),
                success=result.achieved_target,
                model_used=self.model_name,
                total_time_seconds=None,
                metadata={
                    "total_improvement": result.total_improvement,
                    "target_score": self.target,
                }
            )

            # Record each iteration
            for round_result in result.rounds:
                # Convert issues to dict format
                issues_before = [
                    {"type": issue.type, "message": issue.message, "deduction": issue.deduction}
                    for issue in round_result.issues_before
                ]
                issues_after = [
                    {"type": issue.type, "message": issue.message, "deduction": issue.deduction}
                    for issue in round_result.issues_after
                ]

                # Determine strategy used
                strategy = "_".join(round_result.focus_types) if round_result.focus_types else "general"

                self.metrics_collector.record_refine_iteration(
                    module_metrics_id=module_metrics_id,
                    iteration_number=round_result.round_index,
                    score_before=round_result.before_score,
                    score_after=round_result.after_score,
                    issues_before=issues_before,
                    issues_after=issues_after,
                    strategy_used=strategy,
                    code_similarity=None  # Could calculate if needed
                )

        except Exception as e:
            # Don't let metrics collection failure break the refine process
            print(f"Warning: Failed to record metrics: {e}")
