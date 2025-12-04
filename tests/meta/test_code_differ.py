"""
Unit tests for CodeDiffer component

Tests the code comparison and diff analysis functionality.
"""

import pytest
from src.core.meta.code_differ import (
    CodeDiffer,
    CodeChange,
    DiffSummary
)


class TestCodeDiffer:
    """Test suite for CodeDiffer"""

    @pytest.fixture
    def differ(self):
        """Create differ instance"""
        return CodeDiffer()

    @pytest.fixture
    def sample_old_code(self):
        """Sample old code"""
        return """def execute():
    result = do_something()
    return result"""

    @pytest.fixture
    def sample_new_code(self):
        """Sample new code with modifications"""
        return """def execute():
    result = await do_something_async()
    if not result:
        return None
    return result"""

    def test_compare_returns_diff_summary(self, differ, sample_old_code, sample_new_code):
        """Test that compare returns DiffSummary"""
        result = differ.compare(sample_old_code, sample_new_code)

        assert isinstance(result, DiffSummary)

    def test_compare_counts_changes(self, differ, sample_old_code, sample_new_code):
        """Test that compare counts changes correctly"""
        result = differ.compare(sample_old_code, sample_new_code)

        assert result.total_changes > 0
        assert result.lines_added > 0 or result.lines_modified > 0

    def test_compare_calculates_similarity(self, differ, sample_old_code, sample_new_code):
        """Test that compare calculates similarity ratio"""
        result = differ.compare(sample_old_code, sample_new_code)

        assert 0.0 <= result.similarity_ratio <= 1.0

    def test_compare_identical_code(self, differ):
        """Test comparing identical code"""
        code = "def test():\n    pass"
        result = differ.compare(code, code)

        assert result.total_changes == 0
        assert result.similarity_ratio == 1.0

    def test_compare_generates_diff_text(self, differ, sample_old_code, sample_new_code):
        """Test that compare generates unified diff text"""
        result = differ.compare(sample_old_code, sample_new_code)

        assert isinstance(result.diff_text, str)
        assert len(result.diff_text) > 0

    def test_has_significant_changes_true(self, differ, sample_old_code, sample_new_code):
        """Test has_significant_changes returns True for changes"""
        result = differ.compare(sample_old_code, sample_new_code)
        has_changes = differ.has_significant_changes(result, min_changes=1)

        assert has_changes is True

    def test_has_significant_changes_false(self, differ):
        """Test has_significant_changes returns False for no changes"""
        code = "def test():\n    pass"
        result = differ.compare(code, code)
        has_changes = differ.has_significant_changes(result, min_changes=1)

        assert has_changes is False

    def test_extract_added_content(self, differ):
        """Test extracting added content"""
        old_code = "def test():\n    pass"
        new_code = "def test():\n    result = calculate()\n    return result"

        result = differ.compare(old_code, new_code)
        added = differ.extract_added_content(result)

        assert isinstance(added, list)
        assert len(added) > 0

    def test_extract_removed_content(self, differ):
        """Test extracting removed content"""
        old_code = "def test():\n    old_var = 1\n    return old_var"
        new_code = "def test():\n    return 1"

        result = differ.compare(old_code, new_code)
        removed = differ.extract_removed_content(result)

        assert isinstance(removed, list)
        assert len(removed) > 0

    def test_detect_pattern_changes_added(self, differ):
        """Test detecting added patterns"""
        old_code = "def test():\n    pass"
        new_code = "async def test():\n    await something()"

        result = differ.compare(old_code, new_code)
        patterns = differ.detect_pattern_changes(result, ["async", "await"])

        assert "async" in patterns
        assert "await" in patterns

    def test_detect_pattern_changes_removed(self, differ):
        """Test detecting removed patterns"""
        old_code = "def test():\n    nested_function()\n    pass"
        new_code = "def test():\n    pass"

        result = differ.compare(old_code, new_code)
        patterns = differ.detect_pattern_changes(result, ["nested_function"])

        assert "nested_function" in patterns
        assert patterns["nested_function"] is False

    def test_is_code_identical_true(self, differ):
        """Test is_code_identical returns True for same code"""
        code1 = "def test():\n    pass"
        code2 = "def test():\n    pass"

        assert differ.is_code_identical(code1, code2) is True

    def test_is_code_identical_false(self, differ):
        """Test is_code_identical returns False for different code"""
        code1 = "def test():\n    pass"
        code2 = "def test():\n    return 1"

        assert differ.is_code_identical(code1, code2) is False

    def test_is_code_identical_whitespace(self, differ):
        """Test is_code_identical handles whitespace"""
        code1 = "def test():\n    pass\n\n"
        code2 = "def test():\n    pass"

        assert differ.is_code_identical(code1, code2) is True

    def test_code_change_to_dict(self):
        """Test CodeChange.to_dict()"""
        change = CodeChange(
            change_type="added",
            line_number=5,
            new_content="new line",
            context=["context line"]
        )

        result = change.to_dict()

        assert isinstance(result, dict)
        assert result["change_type"] == "added"
        assert result["line_number"] == 5

    def test_diff_summary_to_dict(self, differ, sample_old_code, sample_new_code):
        """Test DiffSummary.to_dict()"""
        summary = differ.compare(sample_old_code, sample_new_code)
        result = summary.to_dict()

        assert isinstance(result, dict)
        assert "lines_added" in result
        assert "lines_removed" in result
        assert "similarity_ratio" in result
        assert "changes" in result

    def test_compare_with_context_lines(self, differ, sample_old_code, sample_new_code):
        """Test compare with different context line counts"""
        result1 = differ.compare(sample_old_code, sample_new_code, context_lines=1)
        result2 = differ.compare(sample_old_code, sample_new_code, context_lines=5)

        assert result1.total_changes == result2.total_changes

    def test_analyze_changes_detects_additions(self, differ):
        """Test that analyze_changes detects additions"""
        old_code = "line1"
        new_code = "line1\nline2"

        result = differ.compare(old_code, new_code)

        assert result.lines_added > 0

    def test_analyze_changes_detects_deletions(self, differ):
        """Test that analyze_changes detects deletions"""
        old_code = "line1\nline2"
        new_code = "line1"

        result = differ.compare(old_code, new_code)

        assert result.lines_removed > 0

    def test_analyze_changes_detects_modifications(self, differ):
        """Test that analyze_changes detects modifications"""
        old_code = "def old_function():\n    pass"
        new_code = "def new_function():\n    pass"

        result = differ.compare(old_code, new_code)

        assert result.total_changes > 0

    def test_has_significant_changes_with_min_similarity(self, differ):
        """Test has_significant_changes with similarity threshold"""
        old_code = "def test():\n    pass"
        new_code = "def test():\n    return 1"

        result = differ.compare(old_code, new_code)
        has_changes = differ.has_significant_changes(
            result,
            min_changes=1,
            min_similarity=0.5
        )

        assert isinstance(has_changes, bool)

    def test_extract_content_handles_empty_diff(self, differ):
        """Test extract functions handle empty diffs"""
        code = "def test():\n    pass"
        result = differ.compare(code, code)

        added = differ.extract_added_content(result)
        removed = differ.extract_removed_content(result)

        assert added == []
        assert removed == []

    def test_detect_pattern_changes_no_match(self, differ, sample_old_code, sample_new_code):
        """Test detect_pattern_changes with non-matching patterns"""
        result = differ.compare(sample_old_code, sample_new_code)
        patterns = differ.detect_pattern_changes(result, ["nonexistent_pattern"])

        assert "nonexistent_pattern" in patterns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
