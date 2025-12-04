#!/usr/bin/env python3
"""
E2E Task Runner

Executes end-to-end tasks defined in YAML specifications and validates
results against expected outcomes.

Design Principles:
1. Atomic components with zero coupling
2. Dependency injection for testability
3. Cloud PostgreSQL (Neon) for metrics storage
4. Comprehensive validation checks
"""
import asyncio
import glob
import json
import sys
import time
import uuid
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class CheckResult:
    """Result of a validation check"""
    check_id: str
    check_type: str
    passed: bool
    description: str
    error_message: Optional[str] = None
    actual_value: Optional[Any] = None
    expected_value: Optional[Any] = None


@dataclass
class E2EExecutionResult:
    """Result of E2E task execution"""
    execution_id: str
    task_id: str
    task_name: str
    status: str
    success: bool
    execution_time_seconds: float
    checks: List[CheckResult]
    modules_used: List[str]
    workflow_steps: int
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def checks_total(self) -> int:
        return len(self.checks)

    @property
    def checks_passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def checks_failed(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    @property
    def failed_check_ids(self) -> List[str]:
        return [c.check_id for c in self.checks if not c.passed]


class CheckValidator(Protocol):
    """Protocol for validation checks"""
    def validate(self, spec: Dict[str, Any], working_dir: Path) -> CheckResult:
        ...


class FileExistsCheck:
    """Validates that a file exists"""

    def validate(self, spec: Dict[str, Any], working_dir: Path) -> CheckResult:
        check_id = spec.get("id", "unknown")
        path = working_dir / spec["path"]
        description = spec.get("description", "File should exist")

        exists = path.exists()

        return CheckResult(
            check_id=check_id,
            check_type="file_exists",
            passed=exists,
            description=description,
            error_message=None if exists else f"File not found: {path}",
            actual_value=exists,
            expected_value=True
        )


class FileGlobAnyCheck:
    """Validates that at least one file matches a glob pattern"""

    def validate(self, spec: Dict[str, Any], working_dir: Path) -> CheckResult:
        check_id = spec.get("id", "unknown")
        pattern = spec["pattern"]
        description = spec.get("description", "At least one file should match pattern")

        full_pattern = str(working_dir / pattern)
        matches = glob.glob(full_pattern)
        passed = len(matches) > 0

        return CheckResult(
            check_id=check_id,
            check_type="file_glob_any",
            passed=passed,
            description=description,
            error_message=None if passed else f"No files match pattern: {pattern}",
            actual_value=len(matches),
            expected_value=">0"
        )


class FileSizeCheck:
    """Validates file size meets minimum requirement"""

    def validate(self, spec: Dict[str, Any], working_dir: Path) -> CheckResult:
        check_id = spec.get("id", "unknown")
        path = working_dir / spec["path"]
        min_bytes = spec.get("min_bytes", 0)
        description = spec.get("description", "File size should meet minimum")

        if not path.exists():
            return CheckResult(
                check_id=check_id,
                check_type="file_size",
                passed=False,
                description=description,
                error_message=f"File not found: {path}",
                actual_value=None,
                expected_value=f">={min_bytes} bytes"
            )

        actual_size = path.stat().st_size
        passed = actual_size >= min_bytes

        return CheckResult(
            check_id=check_id,
            check_type="file_size",
            passed=passed,
            description=description,
            error_message=None if passed else f"File too small: {actual_size} < {min_bytes} bytes",
            actual_value=actual_size,
            expected_value=f">={min_bytes} bytes"
        )


class FileContentStartswithCheck:
    """Validates file content starts with expected prefix"""

    def validate(self, spec: Dict[str, Any], working_dir: Path) -> CheckResult:
        check_id = spec.get("id", "unknown")
        path = working_dir / spec["path"]
        prefix = spec["prefix"]
        description = spec.get("description", "File content should start with prefix")

        if not path.exists():
            return CheckResult(
                check_id=check_id,
                check_type="file_content_startswith",
                passed=False,
                description=description,
                error_message=f"File not found: {path}",
                actual_value=None,
                expected_value=f"starts with '{prefix}'"
            )

        try:
            content = path.read_text()
            passed = content.startswith(prefix)

            return CheckResult(
                check_id=check_id,
                check_type="file_content_startswith",
                passed=passed,
                description=description,
                error_message=None if passed else f"Content does not start with '{prefix}'",
                actual_value=content[:50] if len(content) > 50 else content,
                expected_value=f"starts with '{prefix}'"
            )
        except Exception as e:
            return CheckResult(
                check_id=check_id,
                check_type="file_content_startswith",
                passed=False,
                description=description,
                error_message=f"Error reading file: {e}",
                actual_value=None,
                expected_value=f"starts with '{prefix}'"
            )


class ModuleUsageCheck:
    """Validates that specific modules were used during execution"""

    def validate(self, spec: Dict[str, Any], working_dir: Path, execution_result: Dict[str, Any]) -> CheckResult:
        check_id = spec.get("id", "unknown")
        required_modules = spec.get("includes", [])
        description = spec.get("description", "Required modules should be used")

        # Extract modules used from execution result
        modules_used = execution_result.get("generated_modules", [])
        module_names = [m.get("module_name", "") for m in modules_used]

        # Check if all required modules are present
        missing_modules = [m for m in required_modules if m not in module_names]
        passed = len(missing_modules) == 0

        return CheckResult(
            check_id=check_id,
            check_type="module_usage",
            passed=passed,
            description=description,
            error_message=None if passed else f"Missing modules: {missing_modules}",
            actual_value=module_names,
            expected_value=required_modules
        )


class CheckValidatorFactory:
    """Factory for creating check validators"""

    @staticmethod
    def create(check_type: str) -> Optional[CheckValidator]:
        validators = {
            "file_exists": FileExistsCheck(),
            "file_glob_any": FileGlobAnyCheck(),
            "file_size": FileSizeCheck(),
            "file_content_startswith": FileContentStartswithCheck(),
            "module_usage": ModuleUsageCheck(),
        }
        return validators.get(check_type)


class E2ETaskRunner:
    """
    E2E Task Runner - Executes tasks and validates results

    Zero coupling design with dependency injection for:
    - Smart executor (task execution)
    - Metrics collector (optional metrics tracking)
    """

    def __init__(
        self,
        smart_executor,
        metrics_collector=None,
        project_root: Optional[Path] = None
    ):
        self.smart_executor = smart_executor
        self.metrics_collector = metrics_collector
        self.project_root = project_root or Path(__file__).parent.parent

    async def run_task(self, task_spec_path: Path) -> E2EExecutionResult:
        """Run a single E2E task from YAML specification"""

        # Load task specification
        with open(task_spec_path) as f:
            spec = yaml.safe_load(f)

        task_id = spec.get("id", "unknown")
        task_name = spec.get("name", "Unnamed task")

        print(f"\n{'='*60}")
        print(f"Running E2E Task: {task_name}")
        print(f"Task ID: {task_id}")
        print(f"{'='*60}\n")

        execution_id = str(uuid.uuid4())
        start_time = time.time()

        # Setup working directory
        working_dir_rel = spec.get("entry", {}).get("working_dir", "tmp/e2e")
        working_dir = self.project_root / working_dir_rel
        working_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Execute task using SmartExecutor
            user_prompt = spec.get("input", {}).get("user_prompt", "")

            print(f"Executing task: {user_prompt}\n")
            execution_result = await self.smart_executor.execute_task(user_prompt)

            # Validate expectations
            expectations = spec.get("expectations", {})
            checks = []

            for check_spec in expectations.get("checks", []):
                check_type = check_spec.get("type")
                validator = CheckValidatorFactory.create(check_type)

                if validator:
                    # Special handling for module_usage check
                    if check_type == "module_usage":
                        result = validator.validate(check_spec, working_dir, execution_result)
                    else:
                        result = validator.validate(check_spec, working_dir)

                    checks.append(result)

                    # Print check result
                    status_icon = "✅" if result.passed else "❌"
                    print(f"{status_icon} {result.check_id}: {result.description}")
                    if not result.passed:
                        print(f"   Error: {result.error_message}")
                else:
                    print(f"⚠️  Unknown check type: {check_type}")

            # Determine overall success
            success_mode = expectations.get("success_mode", "all")
            if success_mode == "all":
                success = all(c.passed for c in checks)
            else:
                success = any(c.passed for c in checks)

            # Extract modules used
            modules_used = [
                m.get("module_name", "")
                for m in execution_result.get("generated_modules", [])
            ]

            workflow_steps = len(execution_result.get("attempts", []))

            execution_time = time.time() - start_time

            result = E2EExecutionResult(
                execution_id=execution_id,
                task_id=task_id,
                task_name=task_name,
                status="success" if success else "failed",
                success=success,
                execution_time_seconds=execution_time,
                checks=checks,
                modules_used=modules_used,
                workflow_steps=workflow_steps
            )

            # Record metrics if collector is available
            if self.metrics_collector:
                self._record_metrics(result)

            # Print summary
            print(f"\n{'='*60}")
            print(f"Task {task_id} - {'✅ SUCCESS' if success else '❌ FAILED'}")
            print(f"Execution time: {execution_time:.2f}s")
            print(f"Checks: {result.checks_passed}/{result.checks_total} passed")
            print(f"{'='*60}\n")

            return result

        except Exception as e:
            import traceback

            execution_time = time.time() - start_time
            error_traceback = traceback.format_exc()

            result = E2EExecutionResult(
                execution_id=execution_id,
                task_id=task_id,
                task_name=task_name,
                status="error",
                success=False,
                execution_time_seconds=execution_time,
                checks=[],
                modules_used=[],
                workflow_steps=0,
                error_message=str(e),
                error_traceback=error_traceback
            )

            # Record metrics even for failures
            if self.metrics_collector:
                self._record_metrics(result)

            print(f"\n❌ Task {task_id} failed with error:")
            print(f"   {e}")

            return result

    def _record_metrics(self, result: E2EExecutionResult) -> None:
        """Record execution metrics to database"""
        try:
            self.metrics_collector.record_e2e_execution(
                execution_id=result.execution_id,
                task_id=result.task_id,
                task_name=result.task_name,
                success=result.success,
                status=result.status,
                execution_time=result.execution_time_seconds,
                checks_total=result.checks_total,
                checks_passed=result.checks_passed,
                failed_checks=result.failed_check_ids,
                modules_used=result.modules_used,
                workflow_steps=result.workflow_steps,
                error_message=result.error_message,
                agent_mode="autonomous",
                llm_model="gpt-4o"
            )
        except Exception as e:
            print(f"⚠️  Warning: Failed to record metrics: {e}")

    async def run_all_tasks(self, tasks_dir: Path) -> List[E2EExecutionResult]:
        """Run all E2E tasks in a directory"""

        task_files = list(tasks_dir.glob("*.yaml"))

        if not task_files:
            print(f"No task files found in {tasks_dir}")
            return []

        print(f"\nFound {len(task_files)} E2E task(s)")

        results = []
        for task_file in task_files:
            result = await self.run_task(task_file)
            results.append(result)

        # Print overall summary
        total = len(results)
        passed = sum(1 for r in results if r.success)
        failed = total - passed

        print(f"\n{'='*60}")
        print(f"E2E Test Summary")
        print(f"{'='*60}")
        print(f"Total tasks:  {total}")
        print(f"Passed:       {passed} ({passed/total*100:.1f}%)")
        print(f"Failed:       {failed} ({failed/total*100:.1f}%)")
        print(f"{'='*60}\n")

        return results


async def main():
    """CLI entry point for E2E Runner"""
    import argparse

    parser = argparse.ArgumentParser(
        description="E2E Task Runner - Execute and validate end-to-end tasks"
    )
    parser.add_argument(
        "--task",
        type=Path,
        help="Path to a single task YAML file"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        help="Path to directory containing task YAML files"
    )
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Disable metrics collection"
    )

    args = parser.parse_args()

    # Import dependencies
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from src.core.executor.smart_executor import SmartExecutor

    # Optional metrics collector
    metrics_collector = None
    if not args.no_metrics:
        try:
            from src.core.metrics.collector import MetricsCollector
            metrics_collector = MetricsCollector()
            print("✅ Metrics collection enabled")
        except Exception as e:
            print(f"⚠️  Metrics collection disabled: {e}")

    # Create smart executor
    smart_executor = SmartExecutor()

    # Create E2E runner
    runner = E2ETaskRunner(
        smart_executor=smart_executor,
        metrics_collector=metrics_collector
    )

    # Run tasks
    if args.task:
        await runner.run_task(args.task)
    elif args.dir:
        await runner.run_all_tasks(args.dir)
    else:
        # Default: run all tasks in workflows/e2e
        default_dir = Path(__file__).parent.parent / "workflows" / "e2e"
        if default_dir.exists():
            await runner.run_all_tasks(default_dir)
        else:
            print(f"No E2E tasks found. Create tasks in {default_dir}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
