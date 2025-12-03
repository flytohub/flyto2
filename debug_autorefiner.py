#!/usr/bin/env python3
"""Debug AutoRefiner issue extraction"""
import os
from src.core.meta.quality_checker_v2 import QualityCheckerV2
from src.core.meta.auto_refiner import AutoRefiner

module_path = "/Library/其他專案/tickets/flyto2/src/core/modules/atomic/string/reverse.py"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("=" * 80)
print("TESTING AUTOREFINER")
print("=" * 80)

# 1. Quality check
checker = QualityCheckerV2()
pr_result = checker.review_module(module_path)

print(f"\nPR Score: {pr_result['score']}/10.0")
print(f"Issues found:")
for issue in pr_result.get("issues", []):
    print(f"  - {issue['message']} (deduction: {issue['deduction']})")

# 2. AutoRefiner extracts fixable issues
refiner = AutoRefiner()
fixable = refiner._extract_fixable_issues(pr_result)

print(f"\nFixable issues extracted by AutoRefiner:")
for issue in fixable:
    print(f"  - {issue}")

# 3. Try to refine
if OPENAI_API_KEY and fixable:
    print(f"\n🔧 Attempting to fix {len(fixable)} issues...")
    result = refiner.refine_module(
        module_path=module_path,
        pr_result=pr_result,
        openai_api_key=OPENAI_API_KEY
    )

    print(f"\nRefine result:")
    print(f"  Success: {result['success']}")
    print(f"  Fixed issues: {result['fixed_issues']}")

    # Re-check quality
    if result['success']:
        pr_result_after = checker.review_module(module_path)
        print(f"\nScore after refinement: {pr_result_after['score']}/10.0")
        print(f"Improvement: +{pr_result_after['score'] - pr_result['score']}")
else:
    print("\nSkipping refinement (no API key or no fixable issues)")
