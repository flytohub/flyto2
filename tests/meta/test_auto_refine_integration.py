"""
Integration tests for Auto-Refine Engine components

Tests that all atomic components work together correctly:
- IssueAnalyzer
- EnhancedPromptBuilder
- CodeDiffer
- ConvergenceDetector
"""

import pytest
from src.core.meta.issue_analyzer import IssueAnalyzer
from src.core.meta.enhanced_prompt_builder import EnhancedPromptBuilder, RefineStrategy
from src.core.meta.code_differ import CodeDiffer
from src.core.meta.convergence_detector import ConvergenceDetector, ConvergenceReason


class TestAutoRefineIntegration:
    """Integration test suite for Auto-Refine Engine"""

    @pytest.fixture
    def quality_report_with_issues(self):
        """Sample quality report with issues"""
        return {
            "score": 8.5,
            "issues": [
                {
                    "message": "Found 1 nested function(s)",
                    "deduction": 0.5,
                    "location": "line 10"
                },
                {
                    "message": "Generic Exception catch without specific exceptions first",
                    "deduction": 0.5,
                    "location": "line 20"
                },
                {
                    "message": "Missing parameter documentation",
                    "deduction": 0.2,
                    "location": "line 5"
                }
            ]
        }

    @pytest.fixture
    def sample_code_v1(self):
        """Sample code version 1"""
        return """async def execute(self):
    def nested_helper():
        return 1

    try:
        result = nested_helper()
        return result
    except Exception:
        return None"""

    @pytest.fixture
    def sample_code_v2(self):
        """Sample code version 2 (improved)"""
        return """async def execute(self):
    try:
        result = calculate()
        return result
    except ValueError:
        return None
    except Exception:
        return None"""

    def test_full_workflow_single_iteration(
        self,
        quality_report_with_issues,
        sample_code_v1,
        sample_code_v2
    ):
        """Test complete workflow: analyze -> build prompt -> compare -> detect convergence"""

        # Step 1: Analyze quality issues
        issue_analyzer = IssueAnalyzer()
        analyzed_issues = issue_analyzer.analyze(quality_report_with_issues)

        assert len(analyzed_issues) == 3
        assert all(hasattr(issue, 'priority') for issue in analyzed_issues)

        # Convert to dict format for prompt builder
        issue_dicts = [issue.to_dict() for issue in analyzed_issues]

        # Step 2: Build targeted fix prompt
        prompt_builder = EnhancedPromptBuilder()
        prompt = prompt_builder.build_prompt(
            code=sample_code_v1,
            analyzed_issues=issue_dicts,
            strategy=RefineStrategy.TARGETED_FIX
        )

        assert isinstance(prompt, str)
        assert "nested function" in prompt.lower()
        assert sample_code_v1 in prompt

        # Step 3: Compare code versions
        code_differ = CodeDiffer()
        diff = code_differ.compare(sample_code_v1, sample_code_v2)

        assert diff.total_changes > 0
        assert code_differ.has_significant_changes(diff, min_changes=1)

        # Step 4: Detect convergence
        attempt_history = [
            {"attempt": 1, "score": 8.5, "code": sample_code_v1},
            {"attempt": 2, "score": 9.2, "code": sample_code_v2, "similarity_to_previous": diff.similarity_ratio}
        ]

        convergence_detector = ConvergenceDetector()
        convergence = convergence_detector.detect(attempt_history, target_score=9.5)

        # Should not converge yet (score improving but not at target)
        assert convergence.has_converged is False

    def test_workflow_target_reached(self):
        """Test workflow when target score is reached"""

        issue_analyzer = IssueAnalyzer()
        convergence_detector = ConvergenceDetector()

        # Perfect code with no issues
        perfect_report = {"score": 9.6, "issues": []}
        analyzed_issues = issue_analyzer.analyze(perfect_report)

        assert len(analyzed_issues) == 0

        # Check convergence
        history = [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 9.6, "code": "code2"}
        ]

        convergence = convergence_detector.detect(history, target_score=9.5)

        assert convergence.has_converged is True
        assert convergence.reason == ConvergenceReason.TARGET_REACHED

    def test_workflow_with_strategy_selection(self):
        """Test prompt builder strategy selection based on progress"""

        prompt_builder = EnhancedPromptBuilder()

        # First attempt: should use targeted fix
        strategy1 = prompt_builder.select_strategy(
            attempt_number=1,
            current_score=8.0
        )
        assert strategy1 == RefineStrategy.TARGETED_FIX

        # Second attempt with critical issues: should use full rewrite
        strategy2 = prompt_builder.select_strategy(
            attempt_number=2,
            current_score=7.5,
            has_critical_issues=True
        )
        assert strategy2 == RefineStrategy.FULL_REWRITE

        # Making progress: should use incremental
        strategy3 = prompt_builder.select_strategy(
            attempt_number=3,
            current_score=9.0,
            previous_score=8.5
        )
        assert strategy3 == RefineStrategy.INCREMENTAL_IMPROVEMENT

    def test_workflow_detects_plateau(self):
        """Test that convergence detector catches score plateau"""

        convergence_detector = ConvergenceDetector(
            score_plateau_threshold=0.1,
            lookback_window=3
        )

        # Scores barely changing
        history = [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 8.02, "code": "code2"},
            {"attempt": 3, "score": 8.05, "code": "code3"}
        ]

        convergence = convergence_detector.detect(history, target_score=9.5)

        assert convergence.has_converged is True
        assert convergence.reason == ConvergenceReason.SCORE_PLATEAU

    def test_workflow_diff_detects_minimal_changes(self):
        """Test that differ detects minimal changes"""

        code_differ = CodeDiffer()

        code1 = "def test():\n    pass"
        code2 = "def test():\n    pass\n"  # Just whitespace difference

        diff = code_differ.compare(code1, code2)

        assert diff.similarity_ratio > 0.95
        assert code_differ.is_code_identical(code1, code2)

    def test_workflow_issue_prioritization(self):
        """Test that issues are properly prioritized"""

        issue_analyzer = IssueAnalyzer()

        report = {
            "score": 7.5,
            "issues": [
                {"message": "Missing parameter documentation", "deduction": 0.2},
                {"message": "Found 1 nested function(s)", "deduction": 0.5},
                {"message": "Duplicate import statements", "deduction": 0.1}
            ]
        }

        analyzed = issue_analyzer.analyze(report)

        # Should be sorted by priority (nested function = priority 1, others lower)
        assert analyzed[0].type == "nested_function"
        assert analyzed[0].priority == 1

    def test_workflow_convergence_decision(self):
        """Test should_stop_refining decision logic"""

        convergence_detector = ConvergenceDetector()
        code_differ = CodeDiffer()

        # Scenario: reached target
        history_target = [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 9.6, "code": "code2"}
        ]

        conv = convergence_detector.detect(history_target, target_score=9.5)
        should_stop = convergence_detector.should_stop_refining(conv, attempt_number=2, max_attempts=5)

        assert should_stop is True

        # Scenario: max attempts reached
        history_max = [
            {"attempt": i, "score": 8.0 + i * 0.1, "code": f"code{i}"}
            for i in range(1, 6)
        ]

        conv2 = convergence_detector.detect(history_max, target_score=9.5)
        should_stop2 = convergence_detector.should_stop_refining(conv2, attempt_number=5, max_attempts=5)

        assert should_stop2 is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
