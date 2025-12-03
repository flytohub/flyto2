"""
Test Executor - Auto-run generated tests in Flyto2 Engine
Atomic, zero coupling implementation for V3.0
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import subprocess
import tempfile


class TestExecutor:
    """
    Atomic test executor with zero coupling.

    Automatically executes YAML tests in Flyto2 Engine and reports results.

    Features:
    - Executes YAML test files
    - Captures test output and results
    - Provides detailed test reports
    - Supports timeout configuration
    """

    def __init__(self, engine_path: Optional[str] = None):
        """
        Initialize test executor.

        Args:
            engine_path: Path to Flyto2 Engine CLI (defaults to auto-detect)
        """
        if engine_path:
            self.engine_path = engine_path
        else:
            # Auto-detect engine path
            self.engine_path = self._find_engine_path()

    def execute_test(
        self,
        test_yaml: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Execute a YAML test and return results.

        Args:
            test_yaml: YAML test content as string
            timeout: Maximum execution time in seconds (default: 60)

        Returns:
            {
                "success": bool,
                "passed": int,
                "failed": int,
                "total": int,
                "duration": float,
                "results": List[Dict],
                "output": str,
                "error": str or None
            }
        """
        # Validate YAML
        try:
            test_dict = yaml.safe_load(test_yaml)
        except yaml.YAMLError as e:
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "total": 0,
                "duration": 0.0,
                "results": [],
                "output": "",
                "error": f"Invalid YAML: {str(e)}"
            }

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        ) as f:
            f.write(test_yaml)
            temp_path = f.name

        try:
            # Execute test using Flyto2 Engine
            result = subprocess.run(
                ['python3', '-m', 'flyto2.src.cli.main', temp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent.parent.parent.parent
            )

            # Parse results
            output = result.stdout
            error = result.stderr if result.returncode != 0 else None

            # Analyze output for test results
            test_results = self._parse_test_output(output, test_dict)

            return {
                "success": result.returncode == 0,
                "passed": test_results["passed"],
                "failed": test_results["failed"],
                "total": test_results["total"],
                "duration": test_results["duration"],
                "results": test_results["details"],
                "output": output,
                "error": error
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "total": 0,
                "duration": timeout,
                "results": [],
                "output": "",
                "error": f"Test execution timeout after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "total": 0,
                "duration": 0.0,
                "results": [],
                "output": "",
                "error": f"Execution error: {str(e)}"
            }
        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

    def execute_test_file(
        self,
        test_file_path: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Execute a YAML test file.

        Args:
            test_file_path: Path to YAML test file
            timeout: Maximum execution time in seconds

        Returns:
            Same format as execute_test()
        """
        path = Path(test_file_path)

        if not path.exists():
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "total": 0,
                "duration": 0.0,
                "results": [],
                "output": "",
                "error": f"Test file not found: {test_file_path}"
            }

        test_yaml = path.read_text()
        return self.execute_test(test_yaml, timeout)

    def _find_engine_path(self) -> str:
        """Auto-detect Flyto2 Engine CLI path."""
        # Default path relative to this file
        return str(Path(__file__).parent.parent.parent / "cli" / "main.py")

    def _parse_test_output(
        self,
        output: str,
        test_dict: Dict
    ) -> Dict[str, Any]:
        """
        Parse test execution output.

        Args:
            output: Raw output from engine
            test_dict: Parsed YAML test dict

        Returns:
            {
                "passed": int,
                "failed": int,
                "total": int,
                "duration": float,
                "details": List[Dict]
            }
        """
        steps = test_dict.get("steps", [])
        total = len(steps)

        # Simple parsing based on output patterns
        # This is a basic implementation - can be enhanced based on actual engine output
        passed = 0
        failed = 0
        details = []

        # Check for common success/failure indicators in output
        lines = output.split('\n')
        for step in steps:
            step_id = step.get('id', '')
            step_result = {
                "step_id": step_id,
                "passed": False,
                "message": ""
            }

            # Look for step ID in output
            for line in lines:
                if step_id in line:
                    if any(keyword in line.lower() for keyword in ['pass', 'success', 'ok']):
                        step_result["passed"] = True
                        passed += 1
                    elif any(keyword in line.lower() for keyword in ['fail', 'error']):
                        step_result["passed"] = False
                        failed += 1
                        step_result["message"] = line.strip()
                    break

            details.append(step_result)

        # If no explicit pass/fail found, assume all passed if no errors
        if passed == 0 and failed == 0:
            if "error" not in output.lower() and "fail" not in output.lower():
                passed = total
            else:
                failed = total

        return {
            "passed": passed,
            "failed": failed,
            "total": total,
            "duration": 0.0,  # Would need to parse from output
            "details": details
        }

    def validate_test_format(self, test_yaml: str) -> Dict[str, Any]:
        """
        Validate test YAML format before execution.

        Args:
            test_yaml: YAML test content

        Returns:
            {
                "valid": bool,
                "issues": List[str]
            }
        """
        issues = []

        try:
            test_dict = yaml.safe_load(test_yaml)
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "issues": [f"Invalid YAML syntax: {str(e)}"]
            }

        # Check required fields
        if "name" not in test_dict:
            issues.append("Missing 'name' field")
        if "steps" not in test_dict:
            issues.append("Missing 'steps' field")
        else:
            steps = test_dict["steps"]
            if not isinstance(steps, list):
                issues.append("'steps' must be a list")
            elif len(steps) == 0:
                issues.append("'steps' cannot be empty")
            else:
                # Check each step
                for i, step in enumerate(steps):
                    if not isinstance(step, dict):
                        issues.append(f"Step {i} must be a dictionary")
                        continue
                    if "id" not in step:
                        issues.append(f"Step {i} missing 'id' field")
                    if "module" not in step:
                        issues.append(f"Step {i} missing 'module' field")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
