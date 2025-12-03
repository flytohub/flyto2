"""
V3.0 Evolution System - Complete quality automation
Composites: AutoRefiner + TestExecutor + MetricsTracker
Zero coupling atomic design
"""
from typing import Dict, Any, Optional
from pathlib import Path

from src.core.meta.auto_refiner import AutoRefiner
from src.core.meta.test_executor import TestExecutor
from src.core.meta.metrics_tracker import MetricsTracker


class V3Evolution:
    """
    Complete V3.0 evolution system combining all quality features.

    Atomic composition of:
    - AutoRefiner: Automatic quality fixing
    - TestExecutor: Test execution and validation
    - MetricsTracker: Real-time quality metrics

    Zero coupling - each component works independently.
    """

    def __init__(
        self,
        metrics_file: Optional[str] = None,
        engine_path: Optional[str] = None
    ):
        """
        Initialize V3.0 evolution system.

        Args:
            metrics_file: Path to metrics storage (optional)
            engine_path: Path to Flyto2 Engine CLI (optional)
        """
        self.refiner = AutoRefiner()
        self.test_executor = TestExecutor(engine_path=engine_path)
        self.metrics = MetricsTracker(metrics_file=metrics_file)

    def evolve_module(
        self,
        module_path: str,
        module_name: str,
        pr_result: Dict[str, Any],
        test_yaml: Optional[str],
        openai_api_key: str,
        attempt_number: int = 1
    ) -> Dict[str, Any]:
        """
        Complete evolution cycle: refine + test + track.

        Args:
            module_path: Path to module file
            module_name: Module identifier
            pr_result: PR review result from StrictPRReviewer
            test_yaml: YAML test content (optional)
            openai_api_key: OpenAI API key for refinement
            attempt_number: Current attempt number

        Returns:
            {
                "ok": bool,
                "score": float,
                "refined": bool,
                "test_passed": bool,
                "output": {
                    "refinement": Dict or None,
                    "test_result": Dict or None,
                    "summary": Dict
                },
                "error": str or None
            }
        """
        score = pr_result.get("score", 0.0)
        success = score >= 9.8
        issues = self._extract_issues(pr_result)

        # Record initial generation
        self.metrics.record_generation(
            module_name=module_name,
            success=success,
            score=score,
            attempt_number=attempt_number,
            issues=issues
        )

        refinement_result = None
        test_result = None

        # Auto-refine if needed
        if not success:
            refinement_result = self.refiner.refine_module(
                module_path=module_path,
                pr_result=pr_result,
                openai_api_key=openai_api_key
            )

            if refinement_result["ok"]:
                original_score = score
                refined_score = refinement_result["new_score"]
                fixed_issues = refinement_result["fixed_issues"]

                self.metrics.record_refinement(
                    module_name=module_name,
                    original_score=original_score,
                    refined_score=refined_score,
                    fixed_issues=fixed_issues
                )

                score = refined_score
                success = score >= 9.8

        # Execute tests if provided and module passed
        if test_yaml and success:
            test_result = self.test_executor.execute_test(
                test_yaml=test_yaml,
                timeout=60
            )

            if test_result["success"]:
                self.metrics.record_test_execution(
                    module_name=module_name,
                    passed=test_result["passed"],
                    failed=test_result["failed"],
                    total=test_result["total"],
                    duration=test_result["duration"]
                )

        # Get summary
        summary = self.metrics.get_summary()

        return {
            "ok": success and (test_result is None or test_result["success"]),
            "score": score,
            "refined": refinement_result is not None and refinement_result["ok"],
            "test_passed": test_result is not None and test_result["success"],
            "output": {
                "refinement": refinement_result,
                "test_result": test_result,
                "summary": summary
            },
            "error": None
        }

    def validate_test(self, test_yaml: str) -> Dict[str, Any]:
        """
        Validate test YAML format.

        Args:
            test_yaml: YAML test content

        Returns:
            {"valid": bool, "issues": List[str]}
        """
        return self.test_executor.validate_test_format(test_yaml)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get current metrics summary.

        Returns:
            Summary statistics from MetricsTracker
        """
        return self.metrics.get_summary()

    def get_recent_failures(self, limit: int = 10) -> list:
        """
        Get recent failed generations.

        Args:
            limit: Maximum number of failures to return

        Returns:
            List of failure records
        """
        return self.metrics.get_recent_failures(limit=limit)

    def get_common_issues(self, limit: int = 5) -> list:
        """
        Get most common quality issues.

        Args:
            limit: Maximum number of issues to return

        Returns:
            List of {issue: str, count: int}
        """
        return self.metrics.get_common_issues(limit=limit)

    def clear_metrics(self) -> None:
        """Clear all stored metrics."""
        self.metrics.clear_metrics()

    def _extract_issues(self, pr_result: Dict[str, Any]) -> list:
        """Extract issue descriptions from PR result."""
        issues = []
        for check in pr_result.get("checks", []):
            if not check.get("passed", True):
                issues.append(check.get("name", "unknown issue"))
        return issues
