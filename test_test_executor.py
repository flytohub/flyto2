"""
Test suite for test_executor.py
Verifies test execution works correctly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.meta.test_executor import TestExecutor


def test_initialization():
    """Test that TestExecutor initializes correctly"""
    print("Testing initialization...")

    executor = TestExecutor()

    assert hasattr(executor, 'engine_path'), "Missing engine_path attribute"
    assert executor.engine_path is not None, "engine_path should not be None"

    print("  [PASS] TestExecutor initialized")
    print(f"  Engine path: {executor.engine_path}")


def test_validate_test_format_valid():
    """Test validating valid YAML test"""
    print("\nTesting valid YAML validation...")

    executor = TestExecutor()

    valid_yaml = """
name: Test Module
description: Test description
steps:
  - id: test_step
    module: test.module
    params: {}
    description: Test step
"""

    result = executor.validate_test_format(valid_yaml)

    assert result["valid"] == True, "Valid YAML should pass validation"
    assert len(result["issues"]) == 0, "Valid YAML should have no issues"

    print("  [PASS] Valid YAML validated correctly")


def test_validate_test_format_invalid():
    """Test validating invalid YAML test"""
    print("\nTesting invalid YAML validation...")

    executor = TestExecutor()

    # Missing 'steps' field
    invalid_yaml = """
name: Test Module
description: Test description
"""

    result = executor.validate_test_format(invalid_yaml)

    assert result["valid"] == False, "Invalid YAML should fail validation"
    assert len(result["issues"]) > 0, "Invalid YAML should have issues"
    assert any("steps" in issue.lower() for issue in result["issues"]), "Should report missing steps"

    print("  [PASS] Invalid YAML detected")
    print(f"  Issues found: {len(result['issues'])}")


def test_validate_test_format_invalid_yaml_syntax():
    """Test validating YAML with syntax errors"""
    print("\nTesting YAML syntax error detection...")

    executor = TestExecutor()

    invalid_yaml = "{ this is not valid yaml ]"

    result = executor.validate_test_format(invalid_yaml)

    assert result["valid"] == False, "YAML syntax error should fail validation"
    assert len(result["issues"]) > 0, "Should report syntax error"

    print("  [PASS] YAML syntax error detected")


def test_parse_test_output():
    """Test parsing test execution output"""
    print("\nTesting test output parsing...")

    executor = TestExecutor()

    test_dict = {
        "steps": [
            {"id": "test_basic", "module": "test.module"},
            {"id": "test_verify", "module": "test.assert"}
        ]
    }

    output = """
Executing test_basic... PASS
Executing test_verify... PASS
All tests completed successfully
"""

    result = executor._parse_test_output(output, test_dict)

    assert result["total"] == 2, "Should count 2 steps"
    assert result["passed"] >= 0, "Should have passed count"
    assert result["failed"] >= 0, "Should have failed count"

    print("  [PASS] Test output parsed")
    print(f"  Total: {result['total']}, Passed: {result['passed']}, Failed: {result['failed']}")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("Test Executor - Test Suite")
    print("=" * 80)
    print()

    tests = [
        test_initialization,
        test_validate_test_format_valid,
        test_validate_test_format_invalid,
        test_validate_test_format_invalid_yaml_syntax,
        test_parse_test_output,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}\n")
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
