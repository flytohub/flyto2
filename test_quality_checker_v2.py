"""
Test suite for quality_checker_v2.py
Verifies all 10 quality checks work correctly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.meta.quality_checker_v2 import (
    QualityCheckerV2,
    UnifiedReturnFormatCheck,
    NoDuplicateImportsCheck,
    ProperVariableReferencesCheck,
    NoNestedFunctionsCheck,
    CleanSeparationCheck,
    AsyncIOCheck,
    ComprehensiveErrorHandlingCheck,
    SecurityValidationsCheck,
    NoPlaceholderCodeCheck,
    CompleteDocumentationCheck,
)


def test_unified_return_format():
    """Test Check 1: Unified Return Format"""
    print("Testing Check 1: Unified Return Format...")

    check = UnifiedReturnFormatCheck()

    # Test PASS case
    good_code = '''
    return {
        "ok": True,
        "output": {"data": "test"},
        "error": None,
        "meta": {"module": "test"}
    }
    '''
    score = check.check(good_code, "test.py")
    assert score == 2.0, f"Expected 2.0, got {score}"
    assert len(check.issues) == 0, "Should have no issues"
    print("  [PASS] Correct format recognized")

    # Test FAIL case (wrong format)
    bad_code = '''
    return {
        "status": "success",
        "data": "test"
    }
    '''
    check2 = UnifiedReturnFormatCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 < 2.0, f"Should fail, got {score2}"
    assert len(check2.issues) > 0, "Should have issues"
    print("  [PASS] Wrong format detected")

    print("✅ Check 1 PASSED\n")


def test_no_duplicate_imports():
    """Test Check 2: No Duplicate Imports"""
    print("Testing Check 2: No Duplicate Imports...")

    check = NoDuplicateImportsCheck()

    # Test PASS case
    good_code = '''
import httpx
from pathlib import Path

async def execute(self):
    client = httpx.AsyncClient()
    '''
    score = check.check(good_code, "test.py")
    assert score == 1.0, f"Expected 1.0, got {score}"
    print("  [PASS] No duplicate imports")

    # Test FAIL case
    bad_code = '''
import httpx

async def execute(self):
    import httpx
    '''
    check2 = NoDuplicateImportsCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 == 0.0, f"Expected 0.0, got {score2}"
    print("  [PASS] Duplicate import detected")

    print("✅ Check 2 PASSED\n")


def test_proper_variable_references():
    """Test Check 3: Proper Variable References"""
    print("Testing Check 3: Proper Variable References...")

    check = ProperVariableReferencesCheck()

    # Test PASS case
    good_code = '''
def validate_params(self):
    self.url = self.params["url"]

async def execute(self):
    if self.url.startswith("http"):
        pass
    '''
    score = check.check(good_code, "test.py")
    assert score == 1.0, f"Expected 1.0, got {score}"
    print("  [PASS] Proper self. usage")

    print("✅ Check 3 PASSED\n")


def test_no_nested_functions():
    """Test Check 4: No Nested Functions"""
    print("Testing Check 4: No Nested Functions...")

    check = NoNestedFunctionsCheck()

    # Test PASS case
    good_code = '''
async def execute(self):
    result = await self.helper()
    return result
    '''
    score = check.check(good_code, "test.py")
    assert score == 0.5, f"Expected 0.5, got {score}"
    print("  [PASS] No nested functions")

    # Test FAIL case
    bad_code = '''
async def execute(self):
        def helper():
            pass
    '''
    check2 = NoNestedFunctionsCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 == 0.0, f"Expected 0.0, got {score2}"
    print("  [PASS] Nested function detected")

    print("✅ Check 4 PASSED\n")


def test_clean_separation():
    """Test Check 5: Clean Separation"""
    print("Testing Check 5: Clean Separation...")

    check = CleanSeparationCheck()

    # Test PASS case
    good_code = '''
def validate_params(self):
    if "url" not in self.params:
        raise ValueError("Missing url")
    self.url = self.params["url"]
    '''
    score = check.check(good_code, "test.py")
    assert score == 1.0, f"Expected 1.0, got {score}"
    print("  [PASS] Clean validation")

    # Test FAIL case
    bad_code = '''
def validate_params(self):
    self.url = self.params["url"]
    response = await httpx.get(self.url)
    '''
    check2 = CleanSeparationCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 < 1.0, f"Should fail, got {score2}"
    print("  [PASS] Business logic detected")

    print("✅ Check 5 PASSED\n")


def test_async_io():
    """Test Check 6: Async I/O"""
    print("Testing Check 6: Async I/O...")

    check = AsyncIOCheck()

    # Test PASS case
    good_code = '''
import httpx

async def execute(self):
    async with httpx.AsyncClient() as client:
        pass
    '''
    score = check.check(good_code, "test.py")
    assert score == 1.0, f"Expected 1.0, got {score}"
    print("  [PASS] Async I/O used")

    # Test FAIL case
    bad_code = '''
import requests

def execute(self):
    requests.get(url)
    '''
    check2 = AsyncIOCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 == 0.0, f"Expected 0.0, got {score2}"
    print("  [PASS] Blocking I/O detected")

    print("✅ Check 6 PASSED\n")


def test_comprehensive_error_handling():
    """Test Check 7: Comprehensive Error Handling"""
    print("Testing Check 7: Comprehensive Error Handling...")

    check = ComprehensiveErrorHandlingCheck()

    # Test PASS case
    good_code = '''
try:
    result = await client.get(url)
except httpx.HTTPStatusError as e:
    pass
except httpx.RequestError as e:
    pass
except IOError as e:
    pass
    '''
    score = check.check(good_code, "test.py")
    assert score == 1.0, f"Expected 1.0, got {score}"
    print("  [PASS] Multiple specific exceptions")

    # Test FAIL case
    bad_code = '''
try:
    result = await client.get(url)
except Exception as e:
    pass
    '''
    check2 = ComprehensiveErrorHandlingCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 < 1.0, f"Should fail, got {score2}"
    print("  [PASS] Generic exception detected")

    print("✅ Check 7 PASSED\n")


def test_security_validations():
    """Test Check 8: Security Validations"""
    print("Testing Check 8: Security Validations...")

    check = SecurityValidationsCheck()

    # Test PASS case
    good_code = '''
if not (self.url.startswith("http://") or self.url.startswith("https://")):
    return error

content_type = response.headers.get("content-type")
content_length = response.headers.get("content-length")
    '''
    score = check.check(good_code, "download.py")
    assert score == 1.5, f"Expected 1.5, got {score}"
    print("  [PASS] All security checks present")

    # Test FAIL case
    bad_code = '''
self.url = self.params["url"]
response = await client.get(self.url)
    '''
    check2 = SecurityValidationsCheck()
    score2 = check2.check(bad_code, "download.py")
    assert score2 < 1.5, f"Should fail, got {score2}"
    print("  [PASS] Missing security checks detected")

    print("✅ Check 8 PASSED\n")


def test_no_placeholder_code():
    """Test Check 9: No Placeholder Code"""
    print("Testing Check 9: No Placeholder Code...")

    check = NoPlaceholderCodeCheck()

    # Test PASS case
    good_code = '''
async def execute(self):
    result = await self.process()
    return result
    '''
    score = check.check(good_code, "test.py")
    assert score == 0.5, f"Expected 0.5, got {score}"
    print("  [PASS] No placeholders")

    # Test FAIL case
    bad_code = '''
async def execute(self):
    # TODO: implement here
    raise NotImplementedError
    '''
    check2 = NoPlaceholderCodeCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 == 0.0, f"Expected 0.0, got {score2}"
    print("  [PASS] Placeholder detected")

    print("✅ Check 9 PASSED\n")


def test_complete_documentation():
    """Test Check 10: Complete Documentation"""
    print("Testing Check 10: Complete Documentation...")

    check = CompleteDocumentationCheck()

    # Test PASS case
    good_code = '''
"""
Module description

Parameters:
    url (str): The URL

Returns:
    Dict: Result
"""
    '''
    score = check.check(good_code, "test.py")
    assert score == 0.5, f"Expected 0.5, got {score}"
    print("  [PASS] Complete documentation")

    # Test FAIL case
    bad_code = '''
def execute(self):
    pass
    '''
    check2 = CompleteDocumentationCheck()
    score2 = check2.check(bad_code, "test.py")
    assert score2 < 0.5, f"Should fail, got {score2}"
    print("  [PASS] Missing documentation detected")

    print("✅ Check 10 PASSED\n")


def test_full_integration():
    """Test full integration with QualityCheckerV2"""
    print("Testing Full Integration...")

    # Create a sample module with various issues
    sample_code = '''
"""
Sample module for testing
"""
import httpx

class TestModule:
    def validate_params(self):
        self.url = self.params["url"]

    async def execute(self):
        return {
            "ok": True,
            "output": {},
            "error": None,
            "meta": {}
        }
'''

    # Write to temp file
    temp_file = Path("/tmp/test_module.py")
    temp_file.write_text(sample_code)

    # Run full check
    checker = QualityCheckerV2()
    result = checker.review_module(str(temp_file))

    assert "score" in result, "Result should have score"
    assert "grade" in result, "Result should have grade"
    assert "pass" in result, "Result should have pass status"
    assert "checks" in result, "Result should have checks"
    assert len(result["checks"]) == 10, "Should have 10 checks"

    print(f"  Score: {result['score']}/10.0 ({result['grade']})")
    print(f"  Pass: {result['pass']}")
    print(f"  Checks: {len(result['checks'])}")

    # Clean up
    temp_file.unlink()

    print("✅ Full Integration PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("Quality Checker V2 - Test Suite")
    print("=" * 80)
    print()

    tests = [
        test_unified_return_format,
        test_no_duplicate_imports,
        test_proper_variable_references,
        test_no_nested_functions,
        test_clean_separation,
        test_async_io,
        test_comprehensive_error_handling,
        test_security_validations,
        test_no_placeholder_code,
        test_complete_documentation,
        test_full_integration,
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
