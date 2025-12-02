"""
Historical Comparison
Compare metrics across different time periods (week-over-week, month-over-month)
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class PeriodMetrics:
    """Metrics for a specific time period"""
    period_name: str
    start_date: str
    end_date: str
    total_runs: int
    success_rate: float
    avg_execution_time: float
    total_errors: int
    metrics_data: Dict[str, Any]


@dataclass
class Comparison:
    """Comparison between two periods"""
    metric_name: str
    current_value: float
    previous_value: float
    change: float  # Absolute change
    change_percent: float  # Percentage change
    trend: str  # "up", "down", "stable"
    is_improvement: bool


class HistoricalComparison:
    """
    Compare metrics across time periods for trend analysis
    """

    def __init__(self, metrics_dir: Path = None):
        """
        Initialize historical comparison

        Args:
            metrics_dir: Directory containing metrics files
        """
        if metrics_dir is None:
            metrics_dir = Path(__file__).parent.parent.parent.parent / "metrics"
        self.metrics_dir = Path(metrics_dir)
        self.history_file = self.metrics_dir / "historical_snapshots.json"

    def capture_snapshot(self, snapshot_name: str = None) -> str:
        """
        Capture current metrics snapshot

        Args:
            snapshot_name: Optional name for snapshot, defaults to timestamp

        Returns:
            Snapshot ID
        """
        if snapshot_name is None:
            snapshot_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Load all current metrics
        snapshot = {
            "snapshot_id": snapshot_name,
            "timestamp": datetime.now().isoformat(),
            "accuracy": self._load_metrics("accuracy_leaderboard.json"),
            "stability": self._load_metrics("stability_leaderboard.json"),
            "evolution": self._load_metrics("evolution_leaderboard.json"),
            "speed_races": self._load_metrics("speed_races.json"),
        }

        # Load existing snapshots
        history = self._load_history()
        history[snapshot_name] = snapshot

        # Save updated history
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

        return snapshot_name

    def compare_periods(
        self,
        period1_name: str,
        period2_name: str,
        metrics: List[str] = None
    ) -> List[Comparison]:
        """
        Compare metrics between two snapshots

        Args:
            period1_name: Earlier period snapshot name
            period2_name: Later period snapshot name (current)
            metrics: List of metric types to compare, defaults to all

        Returns:
            List of Comparison objects
        """
        if metrics is None:
            metrics = ["accuracy", "stability", "evolution"]

        history = self._load_history()

        if period1_name not in history or period2_name not in history:
            raise ValueError(f"Snapshot not found: {period1_name} or {period2_name}")

        period1 = history[period1_name]
        period2 = history[period2_name]

        comparisons = []

        for metric_type in metrics:
            if metric_type in period1 and metric_type in period2:
                comparisons.extend(
                    self._compare_metric_type(
                        metric_type,
                        period1[metric_type],
                        period2[metric_type]
                    )
                )

        return comparisons

    def week_over_week(self) -> List[Comparison]:
        """
        Compare this week vs last week

        Returns:
            List of week-over-week comparisons
        """
        # Create snapshots for this week and last week
        now = datetime.now()
        this_week = now.strftime("week_%Y_W%U")
        last_week = (now - timedelta(days=7)).strftime("week_%Y_W%U")

        # Capture current snapshot if not exists
        history = self._load_history()
        if this_week not in history:
            self.capture_snapshot(this_week)

        # Compare if both exist
        if last_week in history and this_week in history:
            return self.compare_periods(last_week, this_week)

        return []

    def month_over_month(self) -> List[Comparison]:
        """
        Compare this month vs last month

        Returns:
            List of month-over-month comparisons
        """
        now = datetime.now()
        this_month = now.strftime("month_%Y_%m")
        last_month = (now - timedelta(days=30)).strftime("month_%Y_%m")

        # Capture current snapshot if not exists
        history = self._load_history()
        if this_month not in history:
            self.capture_snapshot(this_month)

        # Compare if both exist
        if last_month in history and this_month in history:
            return self.compare_periods(last_month, this_month)

        return []

    def calculate_trend(
        self,
        metric_name: str,
        periods: int = 4
    ) -> Dict[str, Any]:
        """
        Calculate trend for a metric across multiple periods

        Args:
            metric_name: Name of metric to analyze
            periods: Number of recent periods to analyze

        Returns:
            Trend analysis with direction and velocity
        """
        history = self._load_history()
        snapshots = sorted(history.items(), key=lambda x: x[1]["timestamp"])

        if len(snapshots) < 2:
            return {"trend": "insufficient_data"}

        # Take most recent N snapshots
        recent = snapshots[-periods:]

        # Extract values over time
        values = []
        for name, snapshot in recent:
            # Average all values for this metric across modules
            metric_data = snapshot.get(metric_name, {})
            if metric_data:
                avg_value = self._calculate_average(metric_data)
                values.append({
                    "timestamp": snapshot["timestamp"],
                    "value": avg_value
                })

        if len(values) < 2:
            return {"trend": "insufficient_data"}

        # Calculate trend
        first_value = values[0]["value"]
        last_value = values[-1]["value"]
        change = last_value - first_value
        change_percent = (change / first_value * 100) if first_value > 0 else 0

        # Determine trend direction
        if abs(change_percent) < 5:
            direction = "stable"
        elif change > 0:
            direction = "improving"
        else:
            direction = "declining"

        return {
            "metric": metric_name,
            "periods_analyzed": len(values),
            "first_value": first_value,
            "last_value": last_value,
            "change": change,
            "change_percent": change_percent,
            "trend": direction,
            "velocity": change / len(values)  # Average change per period
        }

    def generate_comparison_report(
        self,
        period1: str,
        period2: str
    ) -> str:
        """
        Generate human-readable comparison report

        Args:
            period1: Earlier period name
            period2: Later period name (current)

        Returns:
            Formatted report string
        """
        comparisons = self.compare_periods(period1, period2)

        report = []
        report.append("=" * 70)
        report.append(f"HISTORICAL COMPARISON: {period1} → {period2}")
        report.append("=" * 70)
        report.append("")

        # Group by metric type
        accuracy_comps = [c for c in comparisons if "accuracy" in c.metric_name.lower()]
        stability_comps = [c for c in comparisons if "stability" in c.metric_name.lower()]
        evolution_comps = [c for c in comparisons if "evolution" in c.metric_name.lower()]

        def format_section(title: str, comps: List[Comparison]):
            report.append(title)
            report.append("-" * 70)
            for comp in comps:
                trend_icon = "📈" if comp.trend == "up" else "📉" if comp.trend == "down" else "➡️"
                improvement_icon = "✅" if comp.is_improvement else "⚠️" if comp.trend != "stable" else "➡️"

                report.append(f"{improvement_icon} {comp.metric_name}")
                report.append(f"   {period1}: {comp.previous_value:.2f}")
                report.append(f"   {period2}: {comp.current_value:.2f}")
                report.append(f"   Change: {comp.change:+.2f} ({comp.change_percent:+.1f}%) {trend_icon}")
            report.append("")

        if accuracy_comps:
            format_section("🎯 ACCURACY METRICS", accuracy_comps)

        if stability_comps:
            format_section("💪 STABILITY METRICS", stability_comps)

        if evolution_comps:
            format_section("🚀 EVOLUTION METRICS", evolution_comps)

        # Overall summary
        improvements = sum(1 for c in comparisons if c.is_improvement)
        declines = sum(1 for c in comparisons if not c.is_improvement and c.trend != "stable")
        stable = sum(1 for c in comparisons if c.trend == "stable")

        report.append("SUMMARY")
        report.append("-" * 70)
        report.append(f"Total metrics compared: {len(comparisons)}")
        report.append(f"  Improved: {improvements} ✅")
        report.append(f"  Declined: {declines} ⚠️")
        report.append(f"  Stable: {stable} ➡️")

        return "\n".join(report)

    # ==================== Helper Methods ====================

    def _load_history(self) -> Dict:
        """Load historical snapshots"""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return {}

    def _load_metrics(self, filename: str) -> Dict:
        """Load metrics from file"""
        filepath = self.metrics_dir / filename
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return {}

    def _compare_metric_type(
        self,
        metric_type: str,
        period1_data: Dict,
        period2_data: Dict
    ) -> List[Comparison]:
        """Compare a specific metric type between two periods"""
        comparisons = []

        # Calculate aggregate metrics for each period
        avg1 = self._calculate_average(period1_data)
        avg2 = self._calculate_average(period2_data)

        # Create comparison
        change = avg2 - avg1
        change_percent = (change / avg1 * 100) if avg1 > 0 else 0

        # Determine trend
        if abs(change_percent) < 2:
            trend = "stable"
        elif change > 0:
            trend = "up"
        else:
            trend = "down"

        # For most metrics, higher is better
        is_improvement = change > 0

        # Exception: error_rate - lower is better
        if "error" in metric_type.lower():
            is_improvement = change < 0

        comparisons.append(Comparison(
            metric_name=metric_type,
            current_value=avg2,
            previous_value=avg1,
            change=change,
            change_percent=change_percent,
            trend=trend,
            is_improvement=is_improvement
        ))

        return comparisons

    def _calculate_average(self, metrics_data: Dict) -> float:
        """Calculate average value from metrics data"""
        if not metrics_data:
            return 0.0

        # Try to extract numeric values
        values = []
        for key, value in metrics_data.items():
            if isinstance(value, dict):
                # Look for common metric fields
                for field in ["overall_accuracy", "stability_score", "evolution_index", "success_rate"]:
                    if field in value and isinstance(value[field], (int, float)):
                        values.append(value[field])
                        break
            elif isinstance(value, (int, float)):
                values.append(value)

        return sum(values) / len(values) if values else 0.0
