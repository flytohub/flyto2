"""
Code Differ Component

Compares code between refinement attempts to track changes and detect patterns.
Zero coupling - pure function design with dependency injection.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import difflib


@dataclass
class CodeChange:
    """
    Represents a change between code versions

    Attributes:
        change_type: Type of change (added, removed, modified)
        line_number: Line number where change occurred
        old_content: Original content (if removed/modified)
        new_content: New content (if added/modified)
        context: Surrounding context lines
    """
    change_type: str
    line_number: int
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    context: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "change_type": self.change_type,
            "line_number": self.line_number,
            "old_content": self.old_content,
            "new_content": self.new_content,
            "context": self.context
        }


@dataclass
class DiffSummary:
    """
    Summary of differences between code versions

    Attributes:
        lines_added: Number of lines added
        lines_removed: Number of lines removed
        lines_modified: Number of lines modified
        total_changes: Total number of changes
        similarity_ratio: Similarity ratio (0.0 to 1.0)
        changes: List of CodeChange objects
        diff_text: Full unified diff text
    """
    lines_added: int
    lines_removed: int
    lines_modified: int
    total_changes: int
    similarity_ratio: float
    changes: List[CodeChange]
    diff_text: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "lines_modified": self.lines_modified,
            "total_changes": self.total_changes,
            "similarity_ratio": self.similarity_ratio,
            "changes": [c.to_dict() for c in self.changes],
            "diff_text": self.diff_text
        }


class CodeDiffer:
    """
    Compares code versions and analyzes changes

    Pure, stateless component with zero coupling.
    All dependencies injected through constructor or method parameters.
    """

    def compare(
        self,
        old_code: str,
        new_code: str,
        context_lines: int = 3
    ) -> DiffSummary:
        """
        Compare two code versions and return detailed diff summary

        Args:
            old_code: Original code
            new_code: Modified code
            context_lines: Number of context lines to include

        Returns:
            DiffSummary with detailed change information
        """
        # Split into lines
        old_lines = old_code.splitlines(keepends=True)
        new_lines = new_code.splitlines(keepends=True)

        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, old_code, new_code).ratio()

        # Generate unified diff
        diff_text = "".join(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile="previous",
                tofile="current",
                lineterm="",
                n=context_lines
            )
        )

        # Analyze changes
        changes = self._analyze_changes(old_lines, new_lines, context_lines)

        # Count change types
        lines_added = sum(1 for c in changes if c.change_type == "added")
        lines_removed = sum(1 for c in changes if c.change_type == "removed")
        lines_modified = sum(1 for c in changes if c.change_type == "modified")

        return DiffSummary(
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
            total_changes=len(changes),
            similarity_ratio=similarity,
            changes=changes,
            diff_text=diff_text
        )

    def _analyze_changes(
        self,
        old_lines: List[str],
        new_lines: List[str],
        context_lines: int
    ) -> List[CodeChange]:
        """
        Analyze line-by-line changes

        Args:
            old_lines: Original code lines
            new_lines: Modified code lines
            context_lines: Number of context lines

        Returns:
            List of CodeChange objects
        """
        changes = []
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            # Get context
            context_start = max(0, i1 - context_lines)
            context_end = min(len(old_lines), i2 + context_lines)
            context = old_lines[context_start:context_end]

            if tag == "delete":
                for i in range(i1, i2):
                    changes.append(
                        CodeChange(
                            change_type="removed",
                            line_number=i + 1,
                            old_content=old_lines[i].rstrip(),
                            new_content=None,
                            context=context
                        )
                    )

            elif tag == "insert":
                for j in range(j1, j2):
                    changes.append(
                        CodeChange(
                            change_type="added",
                            line_number=j + 1,
                            old_content=None,
                            new_content=new_lines[j].rstrip(),
                            context=context
                        )
                    )

            elif tag == "replace":
                # Handle replace as combination of modified/added/removed
                old_count = i2 - i1
                new_count = j2 - j1
                min_count = min(old_count, new_count)

                # Modified lines (where both old and new exist)
                for i, j in zip(range(i1, i1 + min_count), range(j1, j1 + min_count)):
                    changes.append(
                        CodeChange(
                            change_type="modified",
                            line_number=j + 1,
                            old_content=old_lines[i].rstrip(),
                            new_content=new_lines[j].rstrip(),
                            context=context
                        )
                    )

                # Extra lines in old (removed)
                for i in range(i1 + min_count, i2):
                    changes.append(
                        CodeChange(
                            change_type="removed",
                            line_number=i + 1,
                            old_content=old_lines[i].rstrip(),
                            new_content=None,
                            context=context
                        )
                    )

                # Extra lines in new (added)
                for j in range(j1 + min_count, j2):
                    changes.append(
                        CodeChange(
                            change_type="added",
                            line_number=j + 1,
                            old_content=None,
                            new_content=new_lines[j].rstrip(),
                            context=context
                        )
                    )

        return changes

    def has_significant_changes(
        self,
        diff_summary: DiffSummary,
        min_changes: int = 1,
        min_similarity: float = 0.0
    ) -> bool:
        """
        Check if there are significant changes

        Args:
            diff_summary: DiffSummary to check
            min_changes: Minimum number of changes required
            min_similarity: Minimum similarity ratio (0.0 to 1.0)

        Returns:
            True if changes are significant
        """
        return (
            diff_summary.total_changes >= min_changes and
            diff_summary.similarity_ratio >= min_similarity
        )

    def extract_added_content(self, diff_summary: DiffSummary) -> List[str]:
        """
        Extract all added content lines

        Args:
            diff_summary: DiffSummary to analyze

        Returns:
            List of added content strings
        """
        return [
            change.new_content
            for change in diff_summary.changes
            if change.change_type in ["added", "modified"] and change.new_content
        ]

    def extract_removed_content(self, diff_summary: DiffSummary) -> List[str]:
        """
        Extract all removed content lines

        Args:
            diff_summary: DiffSummary to analyze

        Returns:
            List of removed content strings
        """
        return [
            change.old_content
            for change in diff_summary.changes
            if change.change_type in ["removed", "modified"] and change.old_content
        ]

    def detect_pattern_changes(
        self,
        diff_summary: DiffSummary,
        patterns: List[str]
    ) -> Dict[str, bool]:
        """
        Detect if specific patterns were added or removed

        Args:
            diff_summary: DiffSummary to analyze
            patterns: List of patterns to search for

        Returns:
            Dictionary mapping patterns to whether they were added
        """
        added_content = " ".join(self.extract_added_content(diff_summary))
        removed_content = " ".join(self.extract_removed_content(diff_summary))

        result = {}
        for pattern in patterns:
            was_removed = pattern in removed_content
            was_added = pattern in added_content

            if was_added and not was_removed:
                result[pattern] = True
            elif was_removed and not was_added:
                result[pattern] = False
            else:
                result[pattern] = None  # No change or both added/removed

        return result

    def is_code_identical(self, old_code: str, new_code: str) -> bool:
        """
        Check if two code versions are identical

        Args:
            old_code: Original code
            new_code: Modified code

        Returns:
            True if codes are identical
        """
        return old_code.strip() == new_code.strip()
