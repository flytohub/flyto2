"""
Metrics Tracker - Real-time quality tracking for V3.0
Atomic, zero coupling implementation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path


class MetricsTracker:
    """
    Atomic metrics tracker with zero coupling.

    Tracks module generation quality metrics in real-time:
    - Generation success/failure rates
    - Quality scores over time
    - Average attempts until success
    - Common failure patterns
    """

    def __init__(self, metrics_file: Optional[str] = None):
        """
        Initialize metrics tracker.

        Args:
            metrics_file: Path to metrics storage file (defaults to temp file)
        """
        if metrics_file:
            self.metrics_file = Path(metrics_file)
        else:
            self.metrics_file = Path("/tmp/flyto2_metrics.json")

        self.metrics = self._load_metrics()

    def record_generation(
        self,
        module_name: str,
        success: bool,
        score: float,
        attempt_number: int,
        issues: List[str] = None
    ) -> None:
        """
        Record a module generation attempt.

        Args:
            module_name: Name of the module
            success: Whether generation succeeded
            score: Quality score (0-10.0)
            attempt_number: Which attempt this was (1, 2, 3, etc.)
            issues: List of quality issues found
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "success": success,
            "score": score,
            "attempt": attempt_number,
            "issues": issues or []
        }

        if "generations" not in self.metrics:
            self.metrics["generations"] = []

        self.metrics["generations"].append(record)
        self._save_metrics()

    def record_test_execution(
        self,
        module_name: str,
        passed: int,
        failed: int,
        total: int,
        duration: float
    ) -> None:
        """
        Record test execution results.

        Args:
            module_name: Name of the module tested
            passed: Number of tests passed
            failed: Number of tests failed
            total: Total number of tests
            duration: Execution time in seconds
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "passed": passed,
            "failed": failed,
            "total": total,
            "duration": duration
        }

        if "test_executions" not in self.metrics:
            self.metrics["test_executions"] = []

        self.metrics["test_executions"].append(record)
        self._save_metrics()

    def record_refinement(
        self,
        module_name: str,
        original_score: float,
        refined_score: float,
        fixed_issues: List[str]
    ) -> None:
        """
        Record auto-refinement results.

        Args:
            module_name: Name of the module
            original_score: Score before refinement
            refined_score: Score after refinement
            fixed_issues: List of issues that were fixed
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "original_score": original_score,
            "refined_score": refined_score,
            "improvement": refined_score - original_score,
            "fixed_issues": fixed_issues
        }

        if "refinements" not in self.metrics:
            self.metrics["refinements"] = []

        self.metrics["refinements"].append(record)
        self._save_metrics()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics.

        Returns:
            {
                "total_generations": int,
                "successful_generations": int,
                "success_rate": float,
                "average_score": float,
                "average_attempts": float,
                "total_tests": int,
                "test_pass_rate": float,
                "total_refinements": int,
                "average_improvement": float
            }
        """
        generations = self.metrics.get("generations", [])
        tests = self.metrics.get("test_executions", [])
        refinements = self.metrics.get("refinements", [])

        # Generation metrics
        total_gens = len(generations)
        successful = sum(1 for g in generations if g["success"])
        success_rate = successful / total_gens if total_gens > 0 else 0.0

        scores = [g["score"] for g in generations if g["success"]]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Calculate average attempts (group by module_name)
        module_attempts = {}
        for g in generations:
            name = g["module_name"]
            if name not in module_attempts:
                module_attempts[name] = []
            module_attempts[name].append(g["attempt"])

        avg_attempts = 0.0
        if module_attempts:
            max_attempts = [max(attempts) for attempts in module_attempts.values()]
            avg_attempts = sum(max_attempts) / len(max_attempts)

        # Test metrics
        total_tests = len(tests)
        if total_tests > 0:
            total_passed = sum(t["passed"] for t in tests)
            total_run = sum(t["total"] for t in tests)
            test_pass_rate = total_passed / total_run if total_run > 0 else 0.0
        else:
            test_pass_rate = 0.0

        # Refinement metrics
        total_refinements = len(refinements)
        if total_refinements > 0:
            improvements = [r["improvement"] for r in refinements]
            avg_improvement = sum(improvements) / len(improvements)
        else:
            avg_improvement = 0.0

        return {
            "total_generations": total_gens,
            "successful_generations": successful,
            "success_rate": round(success_rate, 2),
            "average_score": round(avg_score, 2),
            "average_attempts": round(avg_attempts, 2),
            "total_tests": total_tests,
            "test_pass_rate": round(test_pass_rate, 2),
            "total_refinements": total_refinements,
            "average_improvement": round(avg_improvement, 2)
        }

    def get_recent_failures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent failed generations.

        Args:
            limit: Maximum number of failures to return

        Returns:
            List of failure records
        """
        generations = self.metrics.get("generations", [])
        failures = [g for g in generations if not g["success"]]
        return failures[-limit:] if failures else []

    def get_common_issues(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get most common quality issues.

        Args:
            limit: Maximum number of issues to return

        Returns:
            List of {issue: str, count: int}
        """
        generations = self.metrics.get("generations", [])

        issue_counts = {}
        for g in generations:
            for issue in g.get("issues", []):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        sorted_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"issue": issue, "count": count}
            for issue, count in sorted_issues[:limit]
        ]

    def clear_metrics(self) -> None:
        """Clear all stored metrics."""
        self.metrics = {
            "generations": [],
            "test_executions": [],
            "refinements": []
        }
        self._save_metrics()

    def _load_metrics(self) -> Dict:
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                return json.loads(self.metrics_file.read_text())
            except:
                return {}
        return {}

    def _save_metrics(self) -> None:
        """Save metrics to file."""
        self.metrics_file.write_text(
            json.dumps(self.metrics, indent=2)
        )
