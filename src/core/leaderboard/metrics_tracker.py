"""
Leaderboard Metrics Tracker
Tracks accuracy, stability, and evolution metrics for comprehensive leaderboards
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class AccuracyMetric:
    """Accuracy metrics for a module/workflow"""
    module_id: str
    data_completeness: float  # 0-100%
    format_correctness: float  # 0-100%
    error_rate: float  # 0-100%
    overall_accuracy: float  # Calculated from above
    total_runs: int
    last_updated: str


@dataclass
class StabilityMetric:
    """Stability metrics for a module/workflow"""
    module_id: str
    consecutive_successes: int
    max_consecutive_successes: int
    error_recovery_rate: float  # 0-100%
    uptime_hours: float
    stability_score: float  # Calculated composite score
    total_runs: int
    last_updated: str


@dataclass
class EvolutionMetric:
    """Evolution progress metrics"""
    module_id: str
    modules_added: int
    test_coverage_growth: float  # Percentage point increase
    bugs_fixed: int
    avg_fix_time_hours: float
    evolution_index: float  # Calculated composite score
    period_start: str
    period_end: str


class MetricsTracker:
    """
    Track and manage leaderboard metrics
    """

    def __init__(self, metrics_dir: Path = None):
        """
        Initialize metrics tracker

        Args:
            metrics_dir: Directory to store metrics files
        """
        if metrics_dir is None:
            metrics_dir = Path(__file__).parent.parent.parent.parent / "metrics"
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.accuracy_file = self.metrics_dir / "accuracy_leaderboard.json"
        self.stability_file = self.metrics_dir / "stability_leaderboard.json"
        self.evolution_file = self.metrics_dir / "evolution_leaderboard.json"

    # ==================== Accuracy Tracking ====================

    def record_accuracy(
        self,
        module_id: str,
        data_completeness: float,
        format_correctness: float,
        error_rate: float
    ):
        """
        Record accuracy metrics for a module

        Args:
            module_id: Module identifier
            data_completeness: Data completeness percentage (0-100)
            format_correctness: Format correctness percentage (0-100)
            error_rate: Error rate percentage (0-100)
        """
        # Calculate overall accuracy
        overall_accuracy = (
            (data_completeness * 0.4) +
            (format_correctness * 0.4) +
            ((100 - error_rate) * 0.2)
        )

        # Load existing data
        data = self._load_json(self.accuracy_file)
        if module_id not in data:
            data[module_id] = {
                "total_runs": 0,
                "data_completeness": 0,
                "format_correctness": 0,
                "error_rate": 0,
                "overall_accuracy": 0
            }

        # Update with running average
        prev = data[module_id]
        runs = prev["total_runs"]
        new_runs = runs + 1

        data[module_id] = {
            "module_id": module_id,
            "data_completeness": (prev["data_completeness"] * runs + data_completeness) / new_runs,
            "format_correctness": (prev["format_correctness"] * runs + format_correctness) / new_runs,
            "error_rate": (prev["error_rate"] * runs + error_rate) / new_runs,
            "overall_accuracy": (prev["overall_accuracy"] * runs + overall_accuracy) / new_runs,
            "total_runs": new_runs,
            "last_updated": datetime.now().isoformat()
        }

        self._save_json(self.accuracy_file, data)

    def get_accuracy_leaderboard(self, limit: int = 10) -> List[AccuracyMetric]:
        """
        Get accuracy leaderboard

        Args:
            limit: Number of top entries to return

        Returns:
            List of AccuracyMetric sorted by overall_accuracy (desc)
        """
        data = self._load_json(self.accuracy_file)
        metrics = [AccuracyMetric(**entry) for entry in data.values()]
        metrics.sort(key=lambda x: x.overall_accuracy, reverse=True)
        return metrics[:limit]

    # ==================== Stability Tracking ====================

    def record_stability(
        self,
        module_id: str,
        success: bool,
        recovered_from_error: bool = False,
        runtime_hours: float = 0.0
    ):
        """
        Record stability event for a module

        Args:
            module_id: Module identifier
            success: Whether this run succeeded
            recovered_from_error: Whether this was a recovery from previous error
            runtime_hours: Runtime duration in hours
        """
        data = self._load_json(self.stability_file)
        if module_id not in data:
            data[module_id] = {
                "consecutive_successes": 0,
                "max_consecutive_successes": 0,
                "total_runs": 0,
                "successful_recoveries": 0,
                "error_events": 0,
                "uptime_hours": 0.0
            }

        entry = data[module_id]

        # Ensure all required fields exist (backward compatibility)
        entry.setdefault("consecutive_successes", 0)
        entry.setdefault("max_consecutive_successes", 0)
        entry.setdefault("total_runs", 0)
        entry.setdefault("successful_recoveries", 0)
        entry.setdefault("error_events", 0)
        entry.setdefault("uptime_hours", 0.0)

        # Update consecutive successes
        if success:
            entry["consecutive_successes"] += 1
            entry["max_consecutive_successes"] = max(
                entry["max_consecutive_successes"],
                entry["consecutive_successes"]
            )
            if recovered_from_error:
                entry["successful_recoveries"] += 1
        else:
            entry["consecutive_successes"] = 0
            entry["error_events"] += 1

        # Update runtime
        entry["uptime_hours"] += runtime_hours
        entry["total_runs"] += 1

        # Calculate stability score
        recovery_rate = 0
        if entry["error_events"] > 0:
            recovery_rate = (entry["successful_recoveries"] / entry["error_events"]) * 100

        success_rate = ((entry["total_runs"] - entry["error_events"]) / entry["total_runs"]) * 100
        uptime_score = min(entry["uptime_hours"] / 24.0, 1.0) * 100  # Cap at 100% for 24h+

        stability_score = (
            (success_rate * 0.5) +
            (recovery_rate * 0.3) +
            (uptime_score * 0.2)
        )

        data[module_id] = {
            "module_id": module_id,
            "consecutive_successes": entry["consecutive_successes"],
            "max_consecutive_successes": entry["max_consecutive_successes"],
            "error_recovery_rate": recovery_rate,
            "uptime_hours": entry["uptime_hours"],
            "stability_score": stability_score,
            "total_runs": entry["total_runs"],
            "last_updated": datetime.now().isoformat()
        }

        self._save_json(self.stability_file, data)

    def get_stability_leaderboard(self, limit: int = 10) -> List[StabilityMetric]:
        """
        Get stability leaderboard

        Args:
            limit: Number of top entries to return

        Returns:
            List of StabilityMetric sorted by stability_score (desc)
        """
        data = self._load_json(self.stability_file)
        metrics = [StabilityMetric(**entry) for entry in data.values()]
        metrics.sort(key=lambda x: x.stability_score, reverse=True)
        return metrics[:limit]

    # ==================== Evolution Tracking ====================

    def record_evolution(
        self,
        module_id: str,
        modules_added: int = 0,
        test_coverage_growth: float = 0.0,
        bugs_fixed: int = 0,
        fix_time_hours: float = 0.0,
        period_days: int = 7
    ):
        """
        Record evolution metrics

        Args:
            module_id: Module/system identifier
            modules_added: Number of modules added in period
            test_coverage_growth: Test coverage increase (percentage points)
            bugs_fixed: Number of bugs fixed
            fix_time_hours: Average time to fix bugs (hours)
            period_days: Period length in days
        """
        data = self._load_json(self.evolution_file)
        now = datetime.now()
        period_start = (now - timedelta(days=period_days)).isoformat()

        if module_id not in data:
            data[module_id] = {
                "modules_added": 0,
                "test_coverage_growth": 0.0,
                "bugs_fixed": 0,
                "total_fix_time_hours": 0.0,
                "fix_count": 0
            }

        entry = data[module_id]

        # Ensure all required fields exist (backward compatibility)
        entry.setdefault("modules_added", 0)
        entry.setdefault("test_coverage_growth", 0.0)
        entry.setdefault("bugs_fixed", 0)
        entry.setdefault("total_fix_time_hours", 0.0)
        entry.setdefault("fix_count", 0)

        # Update metrics
        entry["modules_added"] += modules_added
        entry["test_coverage_growth"] += test_coverage_growth
        entry["bugs_fixed"] += bugs_fixed

        if bugs_fixed > 0:
            entry["total_fix_time_hours"] += fix_time_hours
            entry["fix_count"] += bugs_fixed

        avg_fix_time = 0
        if entry["fix_count"] > 0:
            avg_fix_time = entry["total_fix_time_hours"] / entry["fix_count"]

        # Calculate evolution index
        # Higher module growth, coverage growth, and bug fixes = better
        # Lower fix time = better
        module_score = min(entry["modules_added"] * 10, 100)  # Cap at 100
        coverage_score = min(entry["test_coverage_growth"] * 2, 100)  # Cap at 100
        bug_fix_score = min(entry["bugs_fixed"] * 5, 100)  # Cap at 100

        # Fix time score: faster is better (inverse relationship)
        fix_time_score = 100
        if avg_fix_time > 0:
            fix_time_score = max(0, 100 - (avg_fix_time / 24.0) * 100)  # 24h = 0 score

        evolution_index = (
            (module_score * 0.3) +
            (coverage_score * 0.3) +
            (bug_fix_score * 0.2) +
            (fix_time_score * 0.2)
        )

        data[module_id] = {
            "module_id": module_id,
            "modules_added": entry["modules_added"],
            "test_coverage_growth": entry["test_coverage_growth"],
            "bugs_fixed": entry["bugs_fixed"],
            "avg_fix_time_hours": avg_fix_time,
            "evolution_index": evolution_index,
            "period_start": period_start,
            "period_end": now.isoformat()
        }

        self._save_json(self.evolution_file, data)

    def get_evolution_leaderboard(self, limit: int = 10) -> List[EvolutionMetric]:
        """
        Get evolution leaderboard

        Args:
            limit: Number of top entries to return

        Returns:
            List of EvolutionMetric sorted by evolution_index (desc)
        """
        data = self._load_json(self.evolution_file)
        metrics = [EvolutionMetric(**entry) for entry in data.values()]
        metrics.sort(key=lambda x: x.evolution_index, reverse=True)
        return metrics[:limit]

    # ==================== Helper Methods ====================

    def _load_json(self, filepath: Path) -> Dict:
        """Load JSON file or return empty dict"""
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return {}

    def _save_json(self, filepath: Path, data: Dict):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    # ==================== Reporting ====================

    def generate_report(self) -> str:
        """
        Generate comprehensive leaderboard report

        Returns:
            Formatted report string
        """
        accuracy = self.get_accuracy_leaderboard(5)
        stability = self.get_stability_leaderboard(5)
        evolution = self.get_evolution_leaderboard(5)

        report = []
        report.append("=" * 70)
        report.append("COMPREHENSIVE LEADERBOARD REPORT")
        report.append("=" * 70)
        report.append("")

        # Accuracy Leaderboard
        report.append("🎯 TOP 5 ACCURACY")
        report.append("-" * 70)
        for i, metric in enumerate(accuracy, 1):
            report.append(f"{i}. {metric.module_id}")
            report.append(f"   Overall: {metric.overall_accuracy:.1f}% | "
                         f"Completeness: {metric.data_completeness:.1f}% | "
                         f"Correctness: {metric.format_correctness:.1f}% | "
                         f"Error Rate: {metric.error_rate:.1f}%")
        report.append("")

        # Stability Leaderboard
        report.append("💪 TOP 5 STABILITY")
        report.append("-" * 70)
        for i, metric in enumerate(stability, 1):
            report.append(f"{i}. {metric.module_id}")
            report.append(f"   Score: {metric.stability_score:.1f} | "
                         f"Max Streak: {metric.max_consecutive_successes} | "
                         f"Recovery: {metric.error_recovery_rate:.1f}% | "
                         f"Uptime: {metric.uptime_hours:.1f}h")
        report.append("")

        # Evolution Leaderboard
        report.append("🚀 TOP 5 EVOLUTION")
        report.append("-" * 70)
        for i, metric in enumerate(evolution, 1):
            report.append(f"{i}. {metric.module_id}")
            report.append(f"   Index: {metric.evolution_index:.1f} | "
                         f"Modules: +{metric.modules_added} | "
                         f"Coverage: +{metric.test_coverage_growth:.1f}% | "
                         f"Bugs Fixed: {metric.bugs_fixed}")
        report.append("")

        return "\n".join(report)
