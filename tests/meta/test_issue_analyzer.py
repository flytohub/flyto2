"""
Unit tests for IssueAnalyzer component

Tests the atomic issue analysis functionality.
"""

import pytest
from src.core.meta.issue_analyzer import (
    IssueAnalyzer,
    AnalyzedIssue,
    IssueSeverity,
    IssueType
)


class TestIssueAnalyzer:
    """Test suite for IssueAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return IssueAnalyzer()

    @pytest.fixture
    def sample_quality_report(self):
        """Sample quality report"""
        return {
            "score": 8.5,
            "issues": [
                {
                    "message": "Found 1 nested function(s)",
                    "deduction": 0.5,
                    "location": "line 45"
                },
                {
                    "message": "Missing parameter documentation",
                    "deduction": 0.2,
                    "location": "line 22"
                },
                {
                    "message": "Generic Exception catch without specific exceptions first",
                    "deduction": 0.5,
                    "location": "line 67"
                },
                {
                    "message": "Missing file size limit check",
                    "deduction": 0.3,
                    "location": "line 55"
                }
            ]
        }

    def test_analyze_returns_list(self, analyzer, sample_quality_report):
        """Test that analyze returns a list"""
        result = analyzer.analyze(sample_quality_report)
        assert isinstance(result, list)

    def test_analyze_correct_count(self, analyzer, sample_quality_report):
        """Test that analyze returns correct number of issues"""
        result = analyzer.analyze(sample_quality_report)
        assert len(result) == 4

    def test_analyze_returns_analyzed_issues(self, analyzer, sample_quality_report):
        """Test that analyze returns AnalyzedIssue objects"""
        result = analyzer.analyze(sample_quality_report)
        assert all(isinstance(issue, AnalyzedIssue) for issue in result)

    def test_analyze_sorts_by_priority(self, analyzer, sample_quality_report):
        """Test that issues are sorted by priority"""
        result = analyzer.analyze(sample_quality_report)

        # Should be sorted by priority (1 = highest)
        priorities = [issue.priority for issue in result]
        assert priorities == sorted(priorities)

    def test_classify_nested_function(self, analyzer):
        """Test classification of nested function issue"""
        issue_type = analyzer._classify_issue_type("Found 1 nested function(s)")
        assert issue_type == IssueType.NESTED_FUNCTION.value

    def test_classify_placeholder_docstring(self, analyzer):
        """Test classification of placeholder docstring"""
        issue_type = analyzer._classify_issue_type("Missing parameter documentation")
        assert issue_type == IssueType.PLACEHOLDER_DOCSTRING.value

    def test_classify_generic_exception(self, analyzer):
        """Test classification of generic exception"""
        issue_type = analyzer._classify_issue_type("Generic Exception catch without specific exceptions first")
        assert issue_type == IssueType.GENERIC_EXCEPTION.value

    def test_classify_file_size_check(self, analyzer):
        """Test classification of file size check"""
        issue_type = analyzer._classify_issue_type("Missing file size limit check")
        assert issue_type == IssueType.MISSING_FILE_SIZE_CHECK.value

    def test_classify_unknown_type(self, analyzer):
        """Test classification of unknown issue type"""
        issue_type = analyzer._classify_issue_type("Some unknown issue")
        assert issue_type == IssueType.UNKNOWN.value

    def test_determine_severity_critical(self, analyzer):
        """Test severity determination for critical issues"""
        severity = analyzer._determine_severity(1.0)
        assert severity == IssueSeverity.CRITICAL

    def test_determine_severity_high(self, analyzer):
        """Test severity determination for high issues"""
        severity = analyzer._determine_severity(0.5)
        assert severity == IssueSeverity.HIGH

    def test_determine_severity_medium(self, analyzer):
        """Test severity determination for medium issues"""
        severity = analyzer._determine_severity(0.3)
        assert severity == IssueSeverity.MEDIUM

    def test_determine_severity_low(self, analyzer):
        """Test severity determination for low issues"""
        severity = analyzer._determine_severity(0.1)
        assert severity == IssueSeverity.LOW

    def test_filter_by_types(self, analyzer, sample_quality_report):
        """Test filtering issues by type"""
        issues = analyzer.analyze(sample_quality_report)
        filtered = analyzer.filter_by_types(
            issues,
            [IssueType.NESTED_FUNCTION.value, IssueType.GENERIC_EXCEPTION.value]
        )

        assert len(filtered) == 2
        assert all(
            issue.type in [IssueType.NESTED_FUNCTION.value, IssueType.GENERIC_EXCEPTION.value]
            for issue in filtered
        )

    def test_has_any_type_true(self, analyzer, sample_quality_report):
        """Test has_any_type returns True when type exists"""
        issues = analyzer.analyze(sample_quality_report)
        result = analyzer.has_any_type(
            issues,
            [IssueType.NESTED_FUNCTION.value]
        )
        assert result is True

    def test_has_any_type_false(self, analyzer, sample_quality_report):
        """Test has_any_type returns False when type doesn't exist"""
        issues = analyzer.analyze(sample_quality_report)
        result = analyzer.has_any_type(
            issues,
            [IssueType.DUPLICATE_IMPORTS.value]
        )
        assert result is False

    def test_get_highest_priority_issues(self, analyzer, sample_quality_report):
        """Test getting top N highest priority issues"""
        issues = analyzer.analyze(sample_quality_report)
        top_issues = analyzer.get_highest_priority_issues(issues, limit=2)

        assert len(top_issues) == 2
        # First should have highest priority
        assert top_issues[0].priority <= top_issues[1].priority

    def test_analyzed_issue_to_dict(self, analyzer, sample_quality_report):
        """Test AnalyzedIssue.to_dict() method"""
        issues = analyzer.analyze(sample_quality_report)
        issue_dict = issues[0].to_dict()

        assert isinstance(issue_dict, dict)
        assert "type" in issue_dict
        assert "severity" in issue_dict
        assert "deduction" in issue_dict
        assert "message" in issue_dict
        assert "location" in issue_dict
        assert "fix_suggestion" in issue_dict
        assert "priority" in issue_dict

    def test_empty_issues_list(self, analyzer):
        """Test handling of empty issues list"""
        report = {"score": 10.0, "issues": []}
        result = analyzer.analyze(report)
        assert len(result) == 0

    def test_missing_issues_key(self, analyzer):
        """Test handling of missing issues key"""
        report = {"score": 10.0}
        result = analyzer.analyze(report)
        assert len(result) == 0

    def test_priority_map_completeness(self, analyzer):
        """Test that all issue types have priority mappings"""
        for issue_type in IssueType:
            assert issue_type.value in analyzer.PRIORITY_MAP

    def test_fix_suggestions_completeness(self, analyzer):
        """Test that all issue types have fix suggestions"""
        for issue_type in IssueType:
            assert issue_type.value in analyzer.FIX_SUGGESTIONS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
