"""
Unit tests for EnhancedPromptBuilder component

Tests the prompt building functionality for code refinement.
"""

import pytest
from src.core.meta.enhanced_prompt_builder import (
    EnhancedPromptBuilder,
    RefineStrategy
)


class TestEnhancedPromptBuilder:
    """Test suite for EnhancedPromptBuilder"""

    @pytest.fixture
    def builder(self):
        """Create builder instance"""
        return EnhancedPromptBuilder()

    @pytest.fixture
    def sample_code(self):
        """Sample code for testing"""
        return """async def execute(self):
    result = await do_something()
    return result"""

    @pytest.fixture
    def sample_issues(self):
        """Sample analyzed issues"""
        return [
            {
                "type": "nested_function",
                "severity": "HIGH",
                "deduction": 0.5,
                "message": "Found 1 nested function(s)",
                "location": "line 45",
                "fix_suggestion": "Remove nested function definition",
                "priority": 1
            },
            {
                "type": "generic_exception",
                "severity": "HIGH",
                "deduction": 0.5,
                "message": "Generic Exception catch without specific exceptions first",
                "location": "line 67",
                "fix_suggestion": "Add specific exception types",
                "priority": 1
            },
            {
                "type": "placeholder_docstring",
                "severity": "MEDIUM",
                "deduction": 0.2,
                "message": "Missing parameter documentation",
                "location": "line 22",
                "fix_suggestion": "Replace placeholder text",
                "priority": 3
            }
        ]

    def test_build_prompt_targeted_fix(self, builder, sample_code, sample_issues):
        """Test building targeted fix prompt"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=sample_issues,
            strategy=RefineStrategy.TARGETED_FIX
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert sample_code in prompt
        assert "nested function" in prompt.lower()
        assert "generic exception" in prompt.lower()

    def test_build_prompt_full_rewrite(self, builder, sample_code, sample_issues):
        """Test building full rewrite prompt"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=sample_issues,
            strategy=RefineStrategy.FULL_REWRITE
        )

        assert isinstance(prompt, str)
        assert "rewrite" in prompt.lower()
        assert sample_code in prompt

    def test_build_prompt_incremental(self, builder, sample_code, sample_issues):
        """Test building incremental improvement prompt"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=sample_issues,
            strategy=RefineStrategy.INCREMENTAL_IMPROVEMENT,
            previous_score=8.5,
            previous_context="Previous attempt had nested function issue"
        )

        assert isinstance(prompt, str)
        assert "8.5" in prompt
        assert "Previous attempt had nested function issue" in prompt

    def test_build_prompt_empty_issues(self, builder, sample_code):
        """Test building prompt with no issues"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=[],
            strategy=RefineStrategy.TARGETED_FIX
        )

        assert isinstance(prompt, str)
        assert sample_code in prompt
        assert "No specific issues found" in prompt

    def test_format_issues(self, builder, sample_issues):
        """Test issue formatting"""
        formatted = builder._format_issues(sample_issues)

        assert isinstance(formatted, str)
        assert "Priority 1" in formatted
        assert "nested_function" in formatted
        assert "generic_exception" in formatted
        assert "line 45" in formatted

    def test_format_issues_empty(self, builder):
        """Test formatting empty issues list"""
        formatted = builder._format_issues([])

        assert formatted == "No specific issues found."

    def test_build_context_from_attempt(self, builder, sample_code, sample_issues):
        """Test building context string"""
        context = builder.build_context_from_attempt(
            attempt_number=2,
            code=sample_code,
            score=8.5,
            issues=sample_issues
        )

        assert isinstance(context, str)
        assert "Attempt #2" in context
        assert "8.5/10.0" in context
        assert "3" in context  # number of issues

    def test_select_strategy_first_attempt(self, builder):
        """Test strategy selection for first attempt"""
        strategy = builder.select_strategy(
            attempt_number=1,
            current_score=8.0
        )

        assert strategy == RefineStrategy.TARGETED_FIX

    def test_select_strategy_critical_issues(self, builder):
        """Test strategy selection with critical issues"""
        strategy = builder.select_strategy(
            attempt_number=2,
            current_score=9.0,
            has_critical_issues=True
        )

        assert strategy == RefineStrategy.FULL_REWRITE

    def test_select_strategy_low_score(self, builder):
        """Test strategy selection with low score"""
        strategy = builder.select_strategy(
            attempt_number=2,
            current_score=6.5
        )

        assert strategy == RefineStrategy.FULL_REWRITE

    def test_select_strategy_no_improvement(self, builder):
        """Test strategy selection when score doesn't improve"""
        strategy = builder.select_strategy(
            attempt_number=2,
            current_score=8.0,
            previous_score=8.5
        )

        # Should try different approach (full rewrite for even attempts)
        assert strategy == RefineStrategy.FULL_REWRITE

    def test_select_strategy_making_progress(self, builder):
        """Test strategy selection when making progress"""
        strategy = builder.select_strategy(
            attempt_number=3,
            current_score=9.0,
            previous_score=8.5
        )

        assert strategy == RefineStrategy.INCREMENTAL_IMPROVEMENT

    def test_strategy_templates_exist(self, builder):
        """Test that all strategies have templates"""
        for strategy in RefineStrategy:
            assert strategy in builder.STRATEGY_TEMPLATES

    def test_prompt_includes_all_issues(self, builder, sample_code, sample_issues):
        """Test that prompt includes all provided issues"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=sample_issues,
            strategy=RefineStrategy.TARGETED_FIX
        )

        for issue in sample_issues:
            assert issue["type"] in prompt
            assert issue["location"] in prompt

    def test_prompt_includes_priorities(self, builder, sample_code, sample_issues):
        """Test that prompt includes issue priorities"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=sample_issues,
            strategy=RefineStrategy.TARGETED_FIX
        )

        assert "Priority 1" in prompt
        assert "Priority 3" in prompt

    def test_context_includes_score_deduction(self, builder, sample_code, sample_issues):
        """Test that context includes total score deduction"""
        context = builder.build_context_from_attempt(
            attempt_number=1,
            code=sample_code,
            score=8.8,
            issues=sample_issues
        )

        # Total deduction: 0.5 + 0.5 + 0.2 = 1.2
        assert "1.2" in context

    def test_incremental_prompt_with_no_context(self, builder, sample_code, sample_issues):
        """Test incremental prompt when no previous context provided"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=sample_issues,
            strategy=RefineStrategy.INCREMENTAL_IMPROVEMENT
        )

        assert "No previous context available" in prompt

    def test_build_prompt_preserves_code(self, builder, sample_code, sample_issues):
        """Test that original code is preserved in prompt"""
        prompt = builder.build_prompt(
            code=sample_code,
            analyzed_issues=sample_issues,
            strategy=RefineStrategy.TARGETED_FIX
        )

        # Code should appear exactly as provided
        assert sample_code in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
