"""
Issue Analyzer Component

Analyzes quality reports and categorizes issues by type, severity, and priority.
Zero coupling - pure function design with dependency injection.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class IssueType(Enum):
    """Known issue types from quality checker"""
    GENERIC_EXCEPTION = "generic_exception"
    NESTED_TRY_EXCEPT = "nested_try_except"
    NESTED_FUNCTION = "nested_function"
    PLACEHOLDER_DOCSTRING = "placeholder_docstring"
    DUPLICATE_IMPORTS = "duplicate_imports"
    MISSING_SELF = "missing_self"
    MISSING_ERROR_FIELD = "missing_error_field"
    MISSING_FILE_SIZE_CHECK = "missing_file_size_check"
    RETURN_FORMAT_INCONSISTENT = "return_format_inconsistent"
    UNKNOWN = "unknown"


@dataclass
class AnalyzedIssue:
    """
    Analyzed issue with metadata

    Attributes:
        type: Issue type classification
        severity: Severity level (CRITICAL/HIGH/MEDIUM/LOW)
        deduction: Score deduction amount
        message: Human-readable description
        location: Code location if available
        fix_suggestion: Suggested fix approach
        priority: Fix priority (1=highest, 5=lowest)
    """
    type: str
    severity: IssueSeverity
    deduction: float
    message: str
    location: str
    fix_suggestion: str
    priority: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type,
            "severity": self.severity.name,
            "deduction": self.deduction,
            "message": self.message,
            "location": self.location,
            "fix_suggestion": self.fix_suggestion,
            "priority": self.priority
        }


class IssueAnalyzer:
    """
    Analyzes quality reports and produces prioritized issue lists

    Pure, stateless component with zero coupling.
    All dependencies injected through constructor or method parameters.
    """

    # Priority mapping: type -> base priority
    PRIORITY_MAP = {
        IssueType.NESTED_FUNCTION.value: 1,
        IssueType.GENERIC_EXCEPTION.value: 1,
        IssueType.NESTED_TRY_EXCEPT.value: 2,
        IssueType.MISSING_SELF.value: 2,
        IssueType.PLACEHOLDER_DOCSTRING.value: 3,
        IssueType.MISSING_ERROR_FIELD.value: 3,
        IssueType.MISSING_FILE_SIZE_CHECK.value: 3,
        IssueType.RETURN_FORMAT_INCONSISTENT.value: 4,
        IssueType.DUPLICATE_IMPORTS.value: 5,
        IssueType.UNKNOWN.value: 5,
    }

    # Fix suggestions by issue type
    FIX_SUGGESTIONS = {
        IssueType.NESTED_FUNCTION.value: "Remove nested function definition. Define all functions at module level.",
        IssueType.GENERIC_EXCEPTION.value: "Add specific exception types before generic Exception catch.",
        IssueType.NESTED_TRY_EXCEPT.value: "Flatten nested try-except blocks into single level.",
        IssueType.MISSING_SELF.value: "Replace bare variable names with self.variable_name.",
        IssueType.PLACEHOLDER_DOCSTRING.value: "Replace placeholder text with actual parameter descriptions.",
        IssueType.MISSING_ERROR_FIELD.value: "Ensure all return statements include 'error' field.",
        IssueType.MISSING_FILE_SIZE_CHECK.value: "Add Content-Length validation before downloading.",
        IssueType.RETURN_FORMAT_INCONSISTENT.value: "Use consistent return format: {ok, output, error, meta}.",
        IssueType.DUPLICATE_IMPORTS.value: "Remove duplicate import statements.",
        IssueType.UNKNOWN.value: "Review and fix the reported issue."
    }

    def analyze(self, quality_report: Dict[str, Any]) -> List[AnalyzedIssue]:
        """
        Analyze quality report and produce prioritized issues

        Args:
            quality_report: Quality report from QualityCheckerV2
                Expected format: {
                    "score": float,
                    "issues": List[Dict[str, Any]],
                    ...
                }

        Returns:
            List of AnalyzedIssue sorted by priority (highest first)
        """
        raw_issues = quality_report.get("issues", [])

        analyzed = []
        for issue in raw_issues:
            analyzed_issue = self._analyze_single_issue(issue)
            analyzed.append(analyzed_issue)

        # Sort by priority (1 = highest), then by deduction (highest first)
        analyzed.sort(key=lambda x: (x.priority, -x.deduction))

        return analyzed

    def _analyze_single_issue(self, issue: Dict[str, Any]) -> AnalyzedIssue:
        """
        Analyze a single issue

        Args:
            issue: Raw issue from quality report
                Expected format: {
                    "message": str,
                    "deduction": float,
                    "location": str (optional)
                }

        Returns:
            AnalyzedIssue with classification and metadata
        """
        message = issue.get("message", "")
        deduction = issue.get("deduction", 0.0)
        location = issue.get("location", "")

        # Classify issue type
        issue_type = self._classify_issue_type(message)

        # Determine severity based on deduction
        severity = self._determine_severity(deduction)

        # Get priority
        priority = self.PRIORITY_MAP.get(issue_type, 5)

        # Get fix suggestion
        fix_suggestion = self.FIX_SUGGESTIONS.get(issue_type, "Fix the reported issue.")

        return AnalyzedIssue(
            type=issue_type,
            severity=severity,
            deduction=deduction,
            message=message,
            location=location,
            fix_suggestion=fix_suggestion,
            priority=priority
        )

    def _classify_issue_type(self, message: str) -> str:
        """
        Classify issue type from message

        Args:
            message: Issue message string

        Returns:
            Issue type string (from IssueType enum)
        """
        msg_lower = message.lower()

        # Pattern matching for known issue types
        if "nested function" in msg_lower or "nested async def" in msg_lower:
            return IssueType.NESTED_FUNCTION.value

        if "generic exception" in msg_lower:
            return IssueType.GENERIC_EXCEPTION.value

        if "nested try" in msg_lower or "nested except" in msg_lower:
            return IssueType.NESTED_TRY_EXCEPT.value

        if "parameter description" in msg_lower or "parameter documentation" in msg_lower or "placeholder" in msg_lower:
            return IssueType.PLACEHOLDER_DOCSTRING.value

        if "duplicate import" in msg_lower:
            return IssueType.DUPLICATE_IMPORTS.value

        if "missing self" in msg_lower or "bare variable" in msg_lower or "self." in msg_lower:
            return IssueType.MISSING_SELF.value

        if "file size" in msg_lower and "limit" in msg_lower:
            return IssueType.MISSING_FILE_SIZE_CHECK.value

        if "error" in msg_lower and "missing" in msg_lower and "field" in msg_lower:
            return IssueType.MISSING_ERROR_FIELD.value

        if "return" in msg_lower and ("missing" in msg_lower or "inconsistent" in msg_lower):
            return IssueType.RETURN_FORMAT_INCONSISTENT.value

        return IssueType.UNKNOWN.value

    def _determine_severity(self, deduction: float) -> IssueSeverity:
        """
        Determine severity level from deduction amount

        Args:
            deduction: Score deduction amount

        Returns:
            IssueSeverity level
        """
        if deduction >= 1.0:
            return IssueSeverity.CRITICAL
        elif deduction >= 0.5:
            return IssueSeverity.HIGH
        elif deduction >= 0.2:
            return IssueSeverity.MEDIUM
        else:
            return IssueSeverity.LOW

    def filter_by_types(
        self,
        issues: List[AnalyzedIssue],
        types: List[str]
    ) -> List[AnalyzedIssue]:
        """
        Filter issues by type

        Args:
            issues: List of analyzed issues
            types: List of issue type strings to include

        Returns:
            Filtered list of issues
        """
        return [issue for issue in issues if issue.type in types]

    def has_any_type(
        self,
        issues: List[AnalyzedIssue],
        types: List[str]
    ) -> bool:
        """
        Check if any issue of given types exists

        Args:
            issues: List of analyzed issues
            types: List of issue type strings to check

        Returns:
            True if at least one issue of given types exists
        """
        return any(issue.type in types for issue in issues)

    def get_highest_priority_issues(
        self,
        issues: List[AnalyzedIssue],
        limit: int = 3
    ) -> List[AnalyzedIssue]:
        """
        Get top N highest priority issues

        Args:
            issues: List of analyzed issues
            limit: Maximum number of issues to return

        Returns:
            Top N highest priority issues
        """
        return issues[:limit]
