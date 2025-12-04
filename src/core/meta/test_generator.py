"""
Test Generator - Auto-generate YAML tests for Flyto2 modules
Atomic, zero coupling implementation based on TEST_GENERATOR_PROMPT.md
"""
from typing import Dict, List, Any, Optional
import yaml


class TestStep:
    """
    Atomic test step with zero dependencies.
    Represents a single step in a YAML test.
    """

    def __init__(
        self,
        step_id: str,
        module: str,
        params: Dict[str, Any],
        description: str
    ):
        self.id = step_id
        self.module = module
        self.params = params
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "id": self.id,
            "module": self.module,
            "params": self.params,
            "description": self.description
        }


class TestGenerator:
    """
    Atomic test generator with zero coupling.

    Generates complete YAML test suites for Flyto2 modules following
    TEST_GENERATOR_PROMPT.md specification.

    Requirements:
    - At least 5 test steps
    - Tests both success and error cases
    - Verifies return format
    - Uses variable references
    - Clear descriptions
    """

    def __init__(self):
        self.steps: List[TestStep] = []

    def generate_test(
        self,
        module_id: str,
        module_description: str,
        params: Dict[str, Any],
        invalid_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a complete YAML test for a module.

        Args:
            module_id: Module identifier (e.g., "image.download")
            module_description: Human-readable description
            params: Valid parameters for success case
            invalid_params: Invalid parameters for error case (optional)

        Returns:
            YAML test string
        """
        self.steps = []

        # Step 1: Basic functionality test
        self._add_basic_test(module_id, params)

        # Step 2: Verify return format
        self._add_format_verification("test_basic", module_id)

        # Step 3: Verify success case
        self._add_success_verification("test_basic", module_id)

        # Step 4: Test error handling (if invalid params provided)
        if invalid_params:
            self._add_error_test(module_id, invalid_params)
            self._add_error_format_verification("test_error", module_id)
            self._add_error_details_verification("test_error", module_id)

        # Step 5: Verify metadata
        self._add_metadata_verification("test_basic", module_id)

        # Build final YAML structure
        test_dict = {
            "name": f"Test {module_id}",
            "description": f"{module_description} - Auto-generated test",
            "steps": [step.to_dict() for step in self.steps]
        }

        # Convert to YAML string
        return yaml.dump(test_dict, default_flow_style=False, sort_keys=False)

    def _add_basic_test(self, module_id: str, params: Dict[str, Any]):
        """Add basic functionality test step"""
        step = TestStep(
            step_id="test_basic",
            module=module_id,
            params=params,
            description=f"Test basic functionality of {module_id} with valid inputs"
        )
        self.steps.append(step)

    def _add_format_verification(self, ref_step_id: str, module_id: str):
        """Add return format verification step"""
        step = TestStep(
            step_id="verify_return_format",
            module="test.assert_structure",
            params={
                "value": f"${{{ref_step_id}}}",
                "required_keys": ["ok", "output", "error", "meta"],
                "message": f"{module_id} must return unified format with ok, output, error, meta"
            },
            description="Verify response has required keys: ok, output, error, meta"
        )
        self.steps.append(step)

    def _add_success_verification(self, ref_step_id: str, module_id: str):
        """Add success case verification step"""
        step = TestStep(
            step_id="verify_success",
            module="test.assert_equals",
            params={
                "actual": f"${{{ref_step_id}.ok}}",
                "expected": True,
                "message": f"{module_id} should return ok=true for valid input"
            },
            description="Verify ok=true for successful execution"
        )
        self.steps.append(step)

    def _add_error_test(self, module_id: str, invalid_params: Dict[str, Any]):
        """Add error handling test step"""
        step = TestStep(
            step_id="test_error",
            module=module_id,
            params=invalid_params,
            description=f"Test error handling of {module_id} with invalid inputs"
        )
        self.steps.append(step)

    def _add_error_format_verification(self, ref_step_id: str, module_id: str):
        """Add error format verification step"""
        step = TestStep(
            step_id="verify_error_format",
            module="test.assert_structure",
            params={
                "value": f"${{{ref_step_id}}}",
                "required_keys": ["ok", "output", "error", "meta"],
                "message": f"{module_id} error response must have unified format"
            },
            description="Verify error response has required format"
        )
        self.steps.append(step)

    def _add_error_details_verification(self, ref_step_id: str, module_id: str):
        """Add error details verification step"""
        step = TestStep(
            step_id="verify_error_details",
            module="test.assert_equals",
            params={
                "actual": f"${{{ref_step_id}.ok}}",
                "expected": False,
                "message": f"{module_id} should return ok=false for invalid input"
            },
            description="Verify ok=false for error case"
        )
        self.steps.append(step)

    def _add_metadata_verification(self, ref_step_id: str, module_id: str):
        """Add metadata verification step"""
        step = TestStep(
            step_id="verify_metadata",
            module="test.assert_structure",
            params={
                "value": f"${{{ref_step_id}.meta}}",
                "required_keys": ["module", "execution_time"],
                "message": f"{module_id} metadata must have module name and execution_time"
            },
            description="Verify metadata contains module name and execution_time"
        )
        self.steps.append(step)

    def validate_test(self, test_yaml: str) -> Dict[str, Any]:
        """
        Validate generated test meets requirements.

        Args:
            test_yaml: YAML test string

        Returns:
            Dictionary with validation results:
            {
                "valid": bool,
                "issues": List[str],
                "stats": {
                    "step_count": int,
                    "has_success_test": bool,
                    "has_error_test": bool,
                    "has_format_verification": bool
                }
            }
        """
        issues = []

        try:
            test_dict = yaml.safe_load(test_yaml)
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "issues": [f"Invalid YAML syntax: {str(e)}"],
                "stats": {}
            }

        # Check required fields
        if "name" not in test_dict:
            issues.append("Missing 'name' field")
        if "description" not in test_dict:
            issues.append("Missing 'description' field")
        if "steps" not in test_dict:
            issues.append("Missing 'steps' field")
            return {"valid": False, "issues": issues, "stats": {}}

        steps = test_dict["steps"]

        # Check minimum step count
        if len(steps) < 5:
            issues.append(f"Test has {len(steps)} steps, minimum is 5")

        # Analyze test coverage
        has_success_test = False
        has_error_test = False
        has_format_verification = False

        for step in steps:
            if not isinstance(step, dict):
                continue

            step_id = step.get("id", "")
            module = step.get("module", "")

            if "test_basic" in step_id or "test_success" in step_id:
                has_success_test = True
            if "test_error" in step_id:
                has_error_test = True
            if "assert_structure" in module or "verify_format" in step_id:
                has_format_verification = True

        # Check coverage
        if not has_success_test:
            issues.append("Missing success case test")
        if not has_format_verification:
            issues.append("Missing return format verification")

        stats = {
            "step_count": len(steps),
            "has_success_test": has_success_test,
            "has_error_test": has_error_test,
            "has_format_verification": has_format_verification
        }

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "stats": stats
        }
