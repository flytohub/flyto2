"""
Test suite for V3Evolution
Verifies the complete V3.0 quality automation system
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.meta.v3_evolution import V3Evolution


def test_initialization():
    """Test V3Evolution initializes correctly"""
    print("Testing V3Evolution initialization...")

    evolution = V3Evolution()

    assert hasattr(evolution, 'refiner'), "Missing refiner"
    assert hasattr(evolution, 'test_executor'), "Missing test_executor"
    assert hasattr(evolution, 'metrics'), "Missing metrics"

    print("  [PASS] V3Evolution initialized with all components")


def test_validate_test():
    """Test test validation"""
    print("\nTesting test validation...")

    evolution = V3Evolution()

    valid_yaml = """
name: Test Module
description: Test description
steps:
  - id: test_step
    module: test.module
    params: {}
    description: Test step
"""

    result = evolution.validate_test(valid_yaml)

    assert result["valid"] == True, "Valid YAML should pass"
    assert len(result["issues"]) == 0, "Should have no issues"

    print("  [PASS] Test validation works")


def test_get_metrics_summary():
    """Test getting metrics summary"""
    print("\nTesting metrics summary...")

    evolution = V3Evolution(metrics_file="/tmp/test_v3_metrics.json")
    evolution.clear_metrics()

    # Record some test data
    evolution.metrics.record_generation("test.module", True, 9.8, 1, [])
    evolution.metrics.record_test_execution("test.module", 5, 0, 5, 1.5)

    summary = evolution.get_metrics_summary()

    assert summary["total_generations"] == 1, "Should have 1 generation"
    assert summary["total_tests"] == 1, "Should have 1 test"

    print("  [PASS] Metrics summary works")
    print(f"  Summary: {summary}")


def test_get_recent_failures():
    """Test getting recent failures"""
    print("\nTesting recent failures...")

    evolution = V3Evolution(metrics_file="/tmp/test_v3_failures.json")
    evolution.clear_metrics()

    # Record some failures
    evolution.metrics.record_generation("fail1", False, 5.0, 1, ["bad code"])
    evolution.metrics.record_generation("fail2", False, 6.0, 1, ["missing docs"])
    evolution.metrics.record_generation("success", True, 10.0, 1, [])

    failures = evolution.get_recent_failures(limit=5)

    assert len(failures) == 2, "Should have 2 failures"
    assert failures[0]["module_name"] == "fail1"
    assert failures[1]["module_name"] == "fail2"

    print("  [PASS] Recent failures tracking works")


def test_get_common_issues():
    """Test getting common issues"""
    print("\nTesting common issues...")

    evolution = V3Evolution(metrics_file="/tmp/test_v3_issues.json")
    evolution.clear_metrics()

    # Record modules with issues
    evolution.metrics.record_generation("mod1", False, 7.0, 1, ["duplicate imports", "missing docs"])
    evolution.metrics.record_generation("mod2", False, 8.0, 1, ["duplicate imports"])
    evolution.metrics.record_generation("mod3", False, 6.0, 1, ["missing docs", "bad format"])

    common = evolution.get_common_issues(limit=3)

    assert len(common) > 0, "Should have common issues"
    # Most common should be "duplicate imports" (2x) or "missing docs" (2x)
    assert common[0]["count"] >= 2, "Top issue should appear at least twice"

    print("  [PASS] Common issues tracking works")
    print(f"  Common issues: {common}")


def test_extract_issues():
    """Test extracting issues from PR result"""
    print("\nTesting issue extraction...")

    evolution = V3Evolution()

    pr_result = {
        "score": 7.5,
        "checks": [
            {"name": "Format Check", "passed": True},
            {"name": "Duplicate Imports", "passed": False},
            {"name": "Missing Docs", "passed": False}
        ]
    }

    issues = evolution._extract_issues(pr_result)

    assert len(issues) == 2, "Should extract 2 failed checks"
    assert "Duplicate Imports" in issues
    assert "Missing Docs" in issues

    print("  [PASS] Issue extraction works")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("V3Evolution - Test Suite")
    print("=" * 80)
    print()

    tests = [
        test_initialization,
        test_validate_test,
        test_get_metrics_summary,
        test_get_recent_failures,
        test_get_common_issues,
        test_extract_issues,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {e}\n")
            failed += 1

    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()

    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
