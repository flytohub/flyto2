#!/usr/bin/env python
"""
Quick Code Duplication Test
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.meta.code_analyzer import CodeDuplicationAnalyzer


def test_code_duplication():
    """Test code duplication detection"""

    print("=" * 70)
    print("CODE DUPLICATION DETECTION TEST")
    print("=" * 70)
    print()

    analyzer = CodeDuplicationAnalyzer(
        project_root=project_root,
        min_lines=5,
        similarity_threshold=0.85
    )

    # Only analyze atomic modules (faster)
    modules_dir = project_root / "src" / "core" / "modules" / "atomic"

    print(f"Analyzing: {modules_dir}")
    print()

    result = analyzer.analyze_directory(modules_dir)

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(result["summary"])
    print()

    if result["duplicate_groups"] > 0:
        print("=" * 70)
        print("TOP 5 DUPLICATION GROUPS")
        print("=" * 70)
        print()

        for i, group in enumerate(result["groups"][:5], 1):
            print(f"{i}. Group with {group['size']} duplicates:")
            for j, block in enumerate(group["blocks"][:3], 1):  # Show first 3
                print(f"   {j}. {block['file']}:{block['lines']}")
            if len(group["blocks"]) > 3:
                print(f"   ... and {len(group['blocks']) - 3} more")
            print()

    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()

    if result["duplicate_groups"] == 0:
        print("✅ Code quality is excellent - no significant duplication found!")
        print("   Your atomic module design is working perfectly.")
    else:
        print(f"Found {result['duplicate_groups']} groups of similar code.")
        print()
        print("Suggestions:")
        print("  1. Review top duplication groups")
        print("  2. Consider extracting common patterns to base classes")
        print("  3. Create shared utility functions for repeated logic")
        print("  4. However, some duplication is acceptable for atomic modules")
        print("     (maintains zero-coupling principle)")

    print()


if __name__ == '__main__':
    test_code_duplication()
