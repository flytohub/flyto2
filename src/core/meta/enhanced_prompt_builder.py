"""
Enhanced Prompt Builder Component

Builds targeted fix prompts based on analyzed issues and refinement strategies.
Zero coupling - pure function design with dependency injection.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from enum import Enum


class RefineStrategy(Enum):
    """Refinement strategy types"""
    TARGETED_FIX = "targeted_fix"
    FULL_REWRITE = "full_rewrite"
    INCREMENTAL_IMPROVEMENT = "incremental_improvement"


class EnhancedPromptBuilder:
    """
    Builds targeted fix prompts for code refinement

    Pure, stateless component with zero coupling.
    All dependencies injected through constructor or method parameters.
    """

    # Base prompt templates by strategy
    STRATEGY_TEMPLATES = {
        RefineStrategy.TARGETED_FIX: """You are an expert Python developer. Fix the following specific issues in the code:

{issue_list}

Current Code:
```python
{code}
```

Requirements:
- Fix ONLY the listed issues
- Maintain all existing functionality
- Follow atomic module constraints (no nested functions, proper error handling)
- Return complete, working code

Output the fixed code only, no explanations.""",

        RefineStrategy.FULL_REWRITE: """You are an expert Python developer. Rewrite this code to meet quality standards:

Quality Issues Found:
{issue_list}

Current Code:
```python
{code}
```

Requirements:
- Address all quality issues
- Maintain the same functionality and interface
- Follow atomic module constraints (no nested functions, proper error handling)
- Use best practices for Python async code
- Return complete, working code

Output the rewritten code only, no explanations.""",

        RefineStrategy.INCREMENTAL_IMPROVEMENT: """You are an expert Python developer. Improve this code incrementally:

Previous Attempt Score: {previous_score}/10.0
Current Issues:
{issue_list}

Current Code:
```python
{code}
```

Context from Previous Attempt:
{previous_context}

Requirements:
- Address the current issues while maintaining previous improvements
- Avoid introducing new issues
- Follow atomic module constraints (no nested functions, proper error handling)
- Return complete, working code

Output the improved code only, no explanations."""
    }

    # Issue formatting template
    ISSUE_FORMAT = """
Priority {priority} - {severity}:
- Type: {type}
- Location: {location}
- Issue: {message}
- Suggested Fix: {fix_suggestion}
- Score Impact: -{deduction} points
"""

    def build_prompt(
        self,
        code: str,
        analyzed_issues: List[Dict[str, Any]],
        strategy: RefineStrategy = RefineStrategy.TARGETED_FIX,
        previous_score: Optional[float] = None,
        previous_context: Optional[str] = None
    ) -> str:
        """
        Build refinement prompt based on issues and strategy

        Args:
            code: Current code to refine
            analyzed_issues: List of analyzed issues (from IssueAnalyzer.analyze())
            strategy: Refinement strategy to use
            previous_score: Score from previous attempt (for incremental strategy)
            previous_context: Context from previous attempt

        Returns:
            Complete prompt string ready for LLM
        """
        # Format issue list
        issue_list = self._format_issues(analyzed_issues)

        # Get template for strategy
        template = self.STRATEGY_TEMPLATES.get(
            strategy,
            self.STRATEGY_TEMPLATES[RefineStrategy.TARGETED_FIX]
        )

        # Build prompt based on strategy
        if strategy == RefineStrategy.INCREMENTAL_IMPROVEMENT:
            prompt = template.format(
                code=code,
                issue_list=issue_list,
                previous_score=previous_score or 0.0,
                previous_context=previous_context or "No previous context available"
            )
        else:
            prompt = template.format(
                code=code,
                issue_list=issue_list
            )

        return prompt

    def _format_issues(self, analyzed_issues: List[Dict[str, Any]]) -> str:
        """
        Format issues for prompt inclusion

        Args:
            analyzed_issues: List of analyzed issues

        Returns:
            Formatted string of issues
        """
        if not analyzed_issues:
            return "No specific issues found."

        formatted = []
        for issue in analyzed_issues:
            formatted.append(
                self.ISSUE_FORMAT.format(
                    priority=issue.get("priority", 5),
                    severity=issue.get("severity", "UNKNOWN"),
                    type=issue.get("type", "unknown"),
                    location=issue.get("location", "N/A"),
                    message=issue.get("message", "No description"),
                    fix_suggestion=issue.get("fix_suggestion", "Review and fix"),
                    deduction=issue.get("deduction", 0.0)
                )
            )

        return "\n".join(formatted)

    def build_context_from_attempt(
        self,
        attempt_number: int,
        code: str,
        score: float,
        issues: List[Dict[str, Any]]
    ) -> str:
        """
        Build context string from a previous attempt

        Args:
            attempt_number: The attempt number
            code: Code from that attempt
            score: Score achieved
            issues: Issues found

        Returns:
            Context string describing the attempt
        """
        issue_types = [issue.get("type", "unknown") for issue in issues]
        unique_types = list(set(issue_types))

        context = f"""Attempt #{attempt_number}:
- Score: {score}/10.0
- Issues Found: {len(issues)}
- Issue Types: {', '.join(unique_types) if unique_types else 'None'}
- Total Score Deduction: {sum(issue.get('deduction', 0.0) for issue in issues):.1f} points
"""
        return context

    def select_strategy(
        self,
        attempt_number: int,
        current_score: float,
        previous_score: Optional[float] = None,
        has_critical_issues: bool = False
    ) -> RefineStrategy:
        """
        Select appropriate refinement strategy

        Args:
            attempt_number: Current attempt number
            current_score: Current quality score
            previous_score: Previous attempt score (if any)
            has_critical_issues: Whether critical issues exist

        Returns:
            Recommended RefineStrategy
        """
        # First attempt: always targeted fix
        if attempt_number == 1:
            return RefineStrategy.TARGETED_FIX

        # Critical issues or very low score: full rewrite
        if has_critical_issues or current_score < 7.0:
            return RefineStrategy.FULL_REWRITE

        # No improvement or score regressed: try different approach
        if previous_score is not None and current_score <= previous_score:
            # Alternate between targeted and rewrite
            if attempt_number % 2 == 0:
                return RefineStrategy.FULL_REWRITE
            else:
                return RefineStrategy.TARGETED_FIX

        # Making progress: incremental improvement
        return RefineStrategy.INCREMENTAL_IMPROVEMENT
