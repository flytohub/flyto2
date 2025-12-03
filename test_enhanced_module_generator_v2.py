"""
Test enhanced_module_generator with quality_checker_v2
Verify integration works correctly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.meta.enhanced_module_generator import EnhancedModuleGenerator
from src.core.meta.quality_checker_v2 import QualityCheckerV2


def test_initialization():
    """Test that EnhancedModuleGenerator initializes correctly"""
    print("Testing initialization...")

    generator = EnhancedModuleGenerator()

    # Check that quality_checker is initialized
    assert hasattr(generator, 'quality_checker'), "Missing quality_checker attribute"
    assert isinstance(generator.quality_checker, QualityCheckerV2), "quality_checker is not QualityCheckerV2"
    assert generator.REQUIRED_SUCCESS_COUNT == 3, "REQUIRED_SUCCESS_COUNT should be 3"
    assert generator.MIN_PR_SCORE == 9.8, "MIN_PR_SCORE should be 9.8"

    print("  [PASS] Initialization successful")
    print(f"  quality_checker: {type(generator.quality_checker).__name__}")
    print(f"  REQUIRED_SUCCESS_COUNT: {generator.REQUIRED_SUCCESS_COUNT}")
    print(f"  MIN_PR_SCORE: {generator.MIN_PR_SCORE}")


def test_quality_checker_has_correct_checks():
    """Test that QualityCheckerV2 has all 10 checks"""
    print("\nTesting quality checker has 10 checks...")

    checker = QualityCheckerV2()
    assert len(checker.checks) == 10, f"Expected 10 checks, got {len(checker.checks)}"

    print("  [PASS] QualityCheckerV2 has 10 checks")
    for i, check in enumerate(checker.checks, 1):
        print(f"  {i}. {check.name} ({check.weight} points)")


def test_quality_checker_review_module():
    """Test that review_module method exists and works"""
    print("\nTesting quality checker review_module method...")

    checker = QualityCheckerV2()

    # Create a simple test module file
    test_file = Path("/tmp/test_module_v2.py")
    test_code = '''"""Test module"""
from typing import Any, Dict

async def execute(self) -> Dict[str, Any]:
    return {
        "ok": True,
        "output": {"data": "test"},
        "error": None,
        "meta": {"module": "test"}
    }
'''
    test_file.write_text(test_code)

    # Test review_module
    result = checker.review_module(str(test_file))

    assert "score" in result, "Result should have 'score'"
    assert "grade" in result, "Result should have 'grade'"
    assert "pass" in result, "Result should have 'pass'"
    assert "checks" in result, "Result should have 'checks'"

    print(f"  [PASS] review_module works")
    print(f"  Score: {result['score']}/10.0 ({result['grade']})")
    print(f"  Pass: {result['pass']}")

    # Clean up
    test_file.unlink()


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("Enhanced Module Generator V2 - Integration Test")
    print("=" * 80)
    print()

    tests = [
        test_initialization,
        test_quality_checker_has_correct_checks,
        test_quality_checker_review_module,
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
