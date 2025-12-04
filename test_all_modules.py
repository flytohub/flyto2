#!/usr/bin/env python3
"""
Comprehensive Module Test
測試所有模組是否正常運行
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def test_module(test_file: Path) -> dict:
    """測試單個模組"""
    print(f"\n{'='*80}")
    print(f"Testing: {test_file.name}")
    print(f"{'='*80}")

    cmd = ["python3", "-m", "src.cli.main", str(test_file)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    passed = result.returncode == 0

    if passed:
        print(f"✅ PASSED: {test_file.name}")
    else:
        print(f"❌ FAILED: {test_file.name}")
        print(f"Error output:\n{result.stderr[-500:]}")  # Last 500 chars

    return {
        "test_file": test_file.name,
        "passed": passed,
        "returncode": result.returncode,
        "stderr": result.stderr if not passed else None
    }

def main():
    """主測試流程"""

    print("="*80)
    print("🧪 Comprehensive Module Test")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Get all test files
    test_dir = Path("workflows/_test")
    test_files = sorted(test_dir.glob("*.yaml"))

    if not test_files:
        print("❌ No test files found")
        return False

    print(f"\nFound {len(test_files)} test files:")
    for tf in test_files:
        print(f"  - {tf.name}")
    print()

    # Run all tests
    results = []
    for test_file in test_files:
        result = test_module(test_file)
        results.append(result)

    # Summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)

    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count

    print(f"Total tests: {len(results)}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print()

    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} {result['test_file']}")
        if not result["passed"] and result["stderr"]:
            print(f"     Error: {result['stderr'][:100]}...")

    print("\n" + "="*80)

    return failed_count == 0

if __name__ == "__main__":
    start_time = datetime.now()

    success = main()

    elapsed = (datetime.now() - start_time).total_seconds()

    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
    print()

    sys.exit(0 if success else 1)
