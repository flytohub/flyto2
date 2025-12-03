"""
Test suite for test_generator.py
Verifies YAML test generation works correctly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.meta.test_generator import TestGenerator, TestStep
import yaml


def test_test_step_creation():
    """Test TestStep creation and to_dict conversion"""
    print("Testing TestStep creation...")

    step = TestStep(
        step_id="test_basic",
        module="image.download",
        params={"url": "https://example.com/image.jpg", "save_path": "/tmp/test.jpg"},
        description="Test basic image download"
    )

    assert step.id == "test_basic"
    assert step.module == "image.download"
    assert step.description == "Test basic image download"

    step_dict = step.to_dict()
    assert "id" in step_dict
    assert "module" in step_dict
    assert "params" in step_dict
    assert "description" in step_dict

    print("  [PASS] TestStep creation works")


def test_generate_basic_test():
    """Test generating a basic test with minimal parameters"""
    print("\nTesting basic test generation...")

    generator = TestGenerator()
    test_yaml = generator.generate_test(
        module_id="string.uppercase",
        module_description="Convert string to uppercase",
        params={"text": "hello world"}
    )

    assert test_yaml, "Generated YAML should not be empty"
    assert "name:" in test_yaml
    assert "description:" in test_yaml
    assert "steps:" in test_yaml
    assert "string.uppercase" in test_yaml

    print("  [PASS] Basic test generation works")
    print(f"  Generated {len(test_yaml)} bytes of YAML")


def test_generate_test_with_error_case():
    """Test generating a test with both success and error cases"""
    print("\nTesting test generation with error case...")

    generator = TestGenerator()
    test_yaml = generator.generate_test(
        module_id="image.download",
        module_description="Download image from URL",
        params={
            "url": "https://example.com/image.jpg",
            "save_path": "/tmp/image.jpg"
        },
        invalid_params={
            "url": "invalid_url",
            "save_path": "/tmp/invalid.jpg"
        }
    )

    # Parse YAML to verify structure
    test_dict = yaml.safe_load(test_yaml)

    assert "name" in test_dict
    assert "description" in test_dict
    assert "steps" in test_dict

    steps = test_dict["steps"]
    assert len(steps) >= 5, f"Expected at least 5 steps, got {len(steps)}"

    # Check for required test types
    step_ids = [step["id"] for step in steps]
    assert "test_basic" in step_ids, "Missing basic test"
    assert "verify_return_format" in step_ids, "Missing format verification"
    assert "test_error" in step_ids, "Missing error test"

    print("  [PASS] Test with error case generated")
    print(f"  Generated {len(steps)} test steps")


def test_yaml_validity():
    """Test that generated YAML is valid and parseable"""
    print("\nTesting YAML validity...")

    generator = TestGenerator()
    test_yaml = generator.generate_test(
        module_id="test.module",
        module_description="Test module",
        params={"param1": "value1"},
        invalid_params={"param1": "invalid"}
    )

    try:
        test_dict = yaml.safe_load(test_yaml)
        assert isinstance(test_dict, dict)
        assert "steps" in test_dict
        assert isinstance(test_dict["steps"], list)
        print("  [PASS] Generated YAML is valid")
    except yaml.YAMLError as e:
        raise AssertionError(f"Invalid YAML generated: {e}")


def test_variable_references():
    """Test that variable references are correctly formatted"""
    print("\nTesting variable references...")

    generator = TestGenerator()
    test_yaml = generator.generate_test(
        module_id="test.module",
        module_description="Test module",
        params={"param1": "value1"}
    )

    # Check for ${step_id.result} pattern
    assert "${test_basic.result}" in test_yaml, "Missing variable reference"
    assert "${test_basic.result.ok}" in test_yaml, "Missing ok verification"
    assert "${test_basic.result.meta}" in test_yaml, "Missing meta verification"

    print("  [PASS] Variable references are correct")


def test_coverage_requirements():
    """Test that generated tests meet coverage requirements"""
    print("\nTesting coverage requirements...")

    generator = TestGenerator()
    test_yaml = generator.generate_test(
        module_id="test.module",
        module_description="Test module",
        params={"param1": "value1"},
        invalid_params={"param1": "invalid"}
    )

    test_dict = yaml.safe_load(test_yaml)
    steps = test_dict["steps"]

    # Check minimum 5 steps
    assert len(steps) >= 5, f"Expected at least 5 steps, got {len(steps)}"

    # Check for required verifications
    modules_used = [step["module"] for step in steps]
    assert "test.assert_structure" in modules_used, "Missing structure assertion"
    assert "test.assert_equals" in modules_used, "Missing equals assertion"

    # Check descriptions
    for step in steps:
        assert "description" in step, f"Step {step.get('id')} missing description"
        assert len(step["description"]) > 0, f"Empty description in step {step.get('id')}"

    print("  [PASS] Coverage requirements met")


def test_validate_test_function():
    """Test the validate_test function"""
    print("\nTesting validate_test function...")

    generator = TestGenerator()
    test_yaml = generator.generate_test(
        module_id="test.module",
        module_description="Test module",
        params={"param1": "value1"},
        invalid_params={"param1": "invalid"}
    )

    # Validate the generated test
    validation = generator.validate_test(test_yaml)

    assert "valid" in validation
    assert "issues" in validation
    assert "stats" in validation

    if not validation["valid"]:
        print(f"  Issues found: {validation['issues']}")

    print(f"  [PASS] Validation works")
    print(f"  Stats: {validation['stats']}")


def test_invalid_yaml_detection():
    """Test that validate_test catches invalid YAML"""
    print("\nTesting invalid YAML detection...")

    generator = TestGenerator()

    # Test with invalid YAML
    invalid_yaml = "{ this is not valid yaml ]"
    validation = generator.validate_test(invalid_yaml)

    assert validation["valid"] == False
    assert len(validation["issues"]) > 0
    assert "YAML" in validation["issues"][0] or "syntax" in validation["issues"][0].lower()

    print("  [PASS] Invalid YAML detected")


def test_minimum_step_requirement():
    """Test that validator checks minimum step requirement"""
    print("\nTesting minimum step requirement...")

    generator = TestGenerator()

    # Create YAML with only 2 steps (below minimum of 5)
    minimal_yaml = """
name: Test module
description: Minimal test
steps:
  - id: step1
    module: test.module
    params: {}
    description: First step
  - id: step2
    module: test.module
    params: {}
    description: Second step
"""

    validation = generator.validate_test(minimal_yaml)

    assert validation["valid"] == False
    assert any("5" in issue or "minimum" in issue.lower() for issue in validation["issues"])

    print("  [PASS] Minimum step requirement checked")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("Test Generator - Test Suite")
    print("=" * 80)
    print()

    tests = [
        test_test_step_creation,
        test_generate_basic_test,
        test_generate_test_with_error_case,
        test_yaml_validity,
        test_variable_references,
        test_coverage_requirements,
        test_validate_test_function,
        test_invalid_yaml_detection,
        test_minimum_step_requirement,
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
