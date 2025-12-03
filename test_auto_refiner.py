"""
Test suite for auto_refiner.py
Verifies automatic code refining works correctly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.meta.auto_refiner import AutoRefiner


def test_initialization():
    """Test that AutoRefiner initializes correctly"""
    print("Testing initialization...")

    refiner = AutoRefiner()

    assert hasattr(refiner, 'fixable_issues'), "Missing fixable_issues attribute"
    assert len(refiner.fixable_issues) > 0, "fixable_issues should not be empty"

    print("  [PASS] AutoRefiner initialized correctly")
    print(f"  Fixable issue types: {len(refiner.fixable_issues)}")


def test_extract_fixable_issues():
    """Test extracting fixable issues from PR result"""
    print("\nTesting extract fixable issues...")

    refiner = AutoRefiner()

    # Mock PR result with some fixable and unfixable issues
    pr_result = {
        "score": 8.5,
        "checks": [
            {
                "name": "NoDuplicateImportsCheck",
                "passed": False,
                "description": "duplicate imports found inside execute()"
            },
            {
                "name": "ProperVariableReferencesCheck",
                "passed": False,
                "description": "missing self prefix on variables"
            },
            {
                "name": "SecurityValidationsCheck",
                "passed": False,
                "description": "missing URL validation"  # Not auto-fixable
            }
        ]
    }

    fixable = refiner._extract_fixable_issues(pr_result)

    assert len(fixable) >= 1, "Should find at least 1 fixable issue"
    assert any("duplicate" in issue.lower() for issue in fixable), "Should find duplicate imports"

    print("  [PASS] Fixable issues extracted")
    print(f"  Found {len(fixable)} fixable issues")


def test_get_unfixable_issues():
    """Test separating unfixable issues"""
    print("\nTesting get unfixable issues...")

    refiner = AutoRefiner()

    pr_result = {
        "checks": [
            {"passed": False, "description": "duplicate imports"},
            {"passed": False, "description": "missing security validation"},
            {"passed": False, "description": "nested function found"}
        ]
    }

    fixed = ["duplicate imports", "nested function found"]
    unfixable = refiner._get_unfixable_issues(pr_result, fixed)

    assert len(unfixable) == 1, f"Should have 1 unfixable issue, got {len(unfixable)}"
    assert "security" in unfixable[0].lower(), "Should keep security validation issue"

    print("  [PASS] Unfixable issues separated correctly")


def test_refine_module_file_not_found():
    """Test handling non-existent module file"""
    print("\nTesting non-existent file handling...")

    refiner = AutoRefiner()

    result = refiner.refine_module(
        module_path="/nonexistent/path.py",
        pr_result={},
        openai_api_key="fake-key"
    )

    assert result["success"] == False, "Should fail for non-existent file"
    assert "not found" in result.get("error", "").lower(), "Should have 'not found' error"

    print("  [PASS] Non-existent file handled correctly")


def test_refine_module_no_fixable_issues():
    """Test handling when there are no fixable issues"""
    print("\nTesting no fixable issues...")

    refiner = AutoRefiner()

    # Create a temporary test file
    test_file = Path("/tmp/test_perfect_module.py")
    test_file.write_text('"""Perfect module"""\nprint("test")')

    pr_result = {
        "score": 10.0,
        "checks": [
            {"passed": True, "name": "All checks passed"}
        ]
    }

    result = refiner.refine_module(
        module_path=str(test_file),
        pr_result=pr_result,
        openai_api_key="fake-key"
    )

    assert result["success"] == True, "Should succeed even with no fixes needed"
    assert len(result["fixed_issues"]) == 0, "Should have 0 fixed issues"

    # Clean up
    test_file.unlink()

    print("  [PASS] No fixable issues handled correctly")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("Auto-Refiner - Test Suite")
    print("=" * 80)
    print()

    tests = [
        test_initialization,
        test_extract_fixable_issues,
        test_get_unfixable_issues,
        test_refine_module_file_not_found,
        test_refine_module_no_fixable_issues,
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
