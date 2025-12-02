"""
Code Duplication Analyzer
Scans codebase for duplicate code patterns and suggests abstractions
"""
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
import difflib


class CodeBlock:
    """Represents a code block for comparison"""

    def __init__(self, code: str, file_path: Path, start_line: int, end_line: int):
        self.code = code
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.hash = hashlib.md5(code.encode()).hexdigest()
        self.normalized = self._normalize(code)
        self.normalized_hash = hashlib.md5(self.normalized.encode()).hexdigest()

    def _normalize(self, code: str) -> str:
        """Normalize code for comparison (remove whitespace, comments)"""
        lines = []
        for line in code.split('\n'):
            # Remove comments
            line = line.split('#')[0]
            # Strip whitespace
            line = line.strip()
            if line:
                lines.append(line)
        return '\n'.join(lines)

    def similarity(self, other: 'CodeBlock') -> float:
        """Calculate similarity with another code block (0-1)"""
        if self.normalized_hash == other.normalized_hash:
            return 1.0

        # Use difflib for similarity
        matcher = difflib.SequenceMatcher(None, self.normalized, other.normalized)
        return matcher.ratio()


class CodeDuplicationAnalyzer:
    """Analyzes codebase for duplicate code patterns"""

    def __init__(self, project_root: Path, min_lines: int = 5, similarity_threshold: float = 0.8):
        """
        Initialize analyzer

        Args:
            project_root: Root directory of project
            min_lines: Minimum lines to consider as duplication
            similarity_threshold: Similarity threshold (0-1)
        """
        self.project_root = project_root
        self.min_lines = min_lines
        self.similarity_threshold = similarity_threshold
        self.code_blocks: List[CodeBlock] = []
        self.duplicates: List[Tuple[CodeBlock, CodeBlock, float]] = []

    def analyze_directory(self, directory: Path = None) -> Dict[str, Any]:
        """
        Analyze directory for code duplication

        Args:
            directory: Directory to analyze (defaults to project_root)

        Returns:
            Analysis report
        """
        if directory is None:
            directory = self.project_root

        print(f"Scanning {directory} for Python files...")

        # Collect all Python files
        python_files = list(directory.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip(f)]

        print(f"Found {len(python_files)} Python files to analyze")

        # Extract code blocks from each file
        for file_path in python_files:
            self._extract_code_blocks(file_path)

        print(f"Extracted {len(self.code_blocks)} code blocks")

        # Find duplicates
        self._find_duplicates()

        print(f"Found {len(self.duplicates)} duplicate pairs")

        # Group duplicates
        groups = self._group_duplicates()

        # Generate report
        report = {
            "files_analyzed": len(python_files),
            "code_blocks": len(self.code_blocks),
            "duplicate_pairs": len(self.duplicates),
            "duplicate_groups": len(groups),
            "groups": groups,
            "summary": self._generate_summary(groups)
        }

        return report

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '__pycache__',
            '.pyc',
            'test_',
            '__init__.py',
            'venv',
            'env',
            '.git'
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def _extract_code_blocks(self, file_path: Path):
        """Extract code blocks from file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start_line = node.lineno
                    end_line = node.end_lineno or start_line

                    if end_line - start_line + 1 >= self.min_lines:
                        # Extract function code
                        lines = content.split('\n')[start_line - 1:end_line]
                        code = '\n'.join(lines)

                        block = CodeBlock(
                            code=code,
                            file_path=file_path,
                            start_line=start_line,
                            end_line=end_line
                        )
                        self.code_blocks.append(block)

        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")

    def _find_duplicates(self):
        """Find duplicate code blocks"""
        # Compare all pairs
        for i, block1 in enumerate(self.code_blocks):
            for block2 in self.code_blocks[i + 1:]:
                # Skip same file comparisons for exact duplicates
                if block1.file_path == block2.file_path:
                    continue

                similarity = block1.similarity(block2)

                if similarity >= self.similarity_threshold:
                    self.duplicates.append((block1, block2, similarity))

    def _group_duplicates(self) -> List[Dict[str, Any]]:
        """Group duplicate blocks"""
        # Build graph of similar blocks
        graph = defaultdict(set)
        for block1, block2, similarity in self.duplicates:
            graph[id(block1)].add((id(block2), block2, similarity))
            graph[id(block2)].add((id(block1), block1, similarity))

        # Find connected components (groups)
        visited = set()
        groups = []

        for block in self.code_blocks:
            block_id = id(block)
            if block_id in visited or block_id not in graph:
                continue

            # BFS to find group
            group_blocks = []
            queue = [block]
            visited.add(block_id)

            while queue:
                current = queue.pop(0)
                group_blocks.append(current)

                for neighbor_id, neighbor, _ in graph[id(current)]:
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append(neighbor)

            if len(group_blocks) > 1:
                groups.append({
                    "size": len(group_blocks),
                    "blocks": [
                        {
                            "file": str(b.file_path.relative_to(self.project_root)),
                            "lines": f"{b.start_line}-{b.end_line}",
                            "code_preview": b.code[:100] + "..." if len(b.code) > 100 else b.code
                        }
                        for b in group_blocks
                    ]
                })

        # Sort by group size (largest first)
        groups.sort(key=lambda g: g["size"], reverse=True)

        return groups

    def _generate_summary(self, groups: List[Dict[str, Any]]) -> str:
        """Generate summary text"""
        if not groups:
            return "✅ No significant code duplication found!"

        total_duplicates = sum(g["size"] for g in groups)
        largest_group = groups[0]["size"] if groups else 0

        summary = [
            f"Found {len(groups)} groups of duplicate code",
            f"Total duplicate instances: {total_duplicates}",
            f"Largest duplication group: {largest_group} instances",
            "",
            "Top 3 duplication groups:"
        ]

        for i, group in enumerate(groups[:3], 1):
            files = set(b["file"] for b in group["blocks"])
            summary.append(f"  {i}. {group['size']} duplicates across {len(files)} files")

        return "\n".join(summary)

    def generate_report(self, output_file: Path = None) -> str:
        """Generate detailed report"""
        report_lines = [
            "=" * 70,
            "CODE DUPLICATION ANALYSIS REPORT",
            "=" * 70,
            "",
            f"Project: {self.project_root.name}",
            f"Min lines for duplication: {self.min_lines}",
            f"Similarity threshold: {self.similarity_threshold * 100}%",
            "",
            "=" * 70,
            "SUMMARY",
            "=" * 70,
            ""
        ]

        result = self.analyze_directory()

        report_lines.append(result["summary"])
        report_lines.append("")
        report_lines.append("=" * 70)
        report_lines.append("DETAILED GROUPS")
        report_lines.append("=" * 70)
        report_lines.append("")

        for i, group in enumerate(result["groups"], 1):
            report_lines.append(f"Group {i}: {group['size']} duplicates")
            report_lines.append("-" * 70)

            for j, block in enumerate(group["blocks"], 1):
                report_lines.append(f"  {j}. {block['file']}:{block['lines']}")

            report_lines.append("")

        report_text = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report_text, encoding='utf-8')
            print(f"\nReport saved to: {output_file}")

        return report_text


def main():
    """Main execution"""
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent.parent
    analyzer = CodeDuplicationAnalyzer(
        project_root=project_root,
        min_lines=5,
        similarity_threshold=0.85
    )

    # Analyze src/core/modules/atomic
    modules_dir = project_root / "src" / "core" / "modules" / "atomic"

    report = analyzer.generate_report()
    print(report)

    # Save report
    report_file = project_root / "metrics" / "code_duplication_report.txt"
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report, encoding='utf-8')

    print(f"\n✅ Report saved to: {report_file}")


if __name__ == "__main__":
    main()
