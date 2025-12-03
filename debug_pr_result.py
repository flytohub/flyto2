#!/usr/bin/env python3
"""Debug script to see PR result structure"""
import json
from src.core.meta.quality_checker_v2 import QualityCheckerV2

module_path = "/Library/其他專案/tickets/flyto2/src/core/modules/atomic/string/reverse.py"

checker = QualityCheckerV2()
pr_result = checker.review_module(module_path)

print("=" * 80)
print("PR RESULT STRUCTURE")
print("=" * 80)
print(json.dumps(pr_result, indent=2))
