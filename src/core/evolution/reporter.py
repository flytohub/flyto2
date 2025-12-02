"""
Evolution Reporter
Tracks and reports on system evolution progress
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class EvolutionReporter:
    """
    Reporter for tracking system evolution and generating reports
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.evolution_log = self.metrics_dir / "evolution_history.json"

        # Initialize evolution history if doesn't exist
        if not self.evolution_log.exists():
            self._initialize_evolution_log()

    def _initialize_evolution_log(self):
        """Initialize evolution history file"""
        initial_data = {
            "start_date": datetime.now().isoformat(),
            "evolution_events": [],
            "statistics": {
                "total_proposals": 0,
                "accepted_proposals": 0,
                "rejected_proposals": 0,
                "modules_generated": 0,
                "modules_improved": 0,
                "bugs_fixed": 0
            }
        }
        with open(self.evolution_log, 'w') as f:
            json.dump(initial_data, f, indent=2)

    def log_evolution_event(
        self,
        event_type: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        impact: str = "medium"
    ):
        """
        Log an evolution event

        Args:
            event_type: Type of event (proposal, improvement, bugfix, etc.)
            description: Human-readable description
            details: Additional event details
            impact: Impact level (low, medium, high, critical)
        """
        with open(self.evolution_log, 'r') as f:
            data = json.load(f)

        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "details": details or {},
            "impact": impact
        }

        data["evolution_events"].append(event)

        # Update statistics
        if event_type == "proposal_accepted":
            data["statistics"]["accepted_proposals"] += 1
            data["statistics"]["total_proposals"] += 1
        elif event_type == "proposal_rejected":
            data["statistics"]["rejected_proposals"] += 1
            data["statistics"]["total_proposals"] += 1
        elif event_type == "module_generated":
            data["statistics"]["modules_generated"] += 1
        elif event_type == "module_improved":
            data["statistics"]["modules_improved"] += 1
        elif event_type == "bug_fixed":
            data["statistics"]["bugs_fixed"] += 1

        with open(self.evolution_log, 'w') as f:
            json.dump(data, f, indent=2)

    def get_evolution_history(
        self,
        event_type: Optional[str] = None,
        days: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get evolution history

        Args:
            event_type: Filter by event type
            days: Get events from last N days
            limit: Maximum number of events to return

        Returns:
            List of evolution events
        """
        if not self.evolution_log.exists():
            return []

        with open(self.evolution_log, 'r') as f:
            data = json.load(f)

        events = data.get("evolution_events", [])

        # Filter by event type
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]

        # Filter by date range
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            events = [e for e in events if datetime.fromisoformat(e["timestamp"]) > cutoff]

        # Apply limit
        if limit:
            events = events[-limit:]

        return events

    def generate_evolution_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive evolution report

        Args:
            days: Number of days to include in report

        Returns:
            Evolution report with statistics and highlights
        """
        if not self.evolution_log.exists():
            self._initialize_evolution_log()

        with open(self.evolution_log, 'r') as f:
            data = json.load(f)

        # Get recent events
        recent_events = self.get_evolution_history(days=days)

        # Calculate time-based statistics
        stats_by_type = {}
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            stats_by_type[event_type] = stats_by_type.get(event_type, 0) + 1

        # Identify high-impact events
        high_impact_events = [e for e in recent_events if e.get("impact") in ["high", "critical"]]

        report = {
            "report_period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "overall_statistics": data.get("statistics", {}),
            "recent_activity": {
                "total_events": len(recent_events),
                "events_by_type": stats_by_type,
                "high_impact_events": len(high_impact_events)
            },
            "highlights": self._generate_highlights(recent_events),
            "recent_events": recent_events[-20:],  # Last 20 events
            "recommendations": self._generate_recommendations(data)
        }

        return report

    def get_evolution_statistics(self) -> Dict[str, Any]:
        """
        Get cumulative evolution statistics

        Returns:
            Overall statistics
        """
        if not self.evolution_log.exists():
            self._initialize_evolution_log()

        with open(self.evolution_log, 'r') as f:
            data = json.load(f)

        stats = data.get("statistics", {})
        events = data.get("evolution_events", [])

        # Calculate acceptance rate
        total_proposals = stats.get("total_proposals", 0)
        accepted = stats.get("accepted_proposals", 0)
        acceptance_rate = (accepted / total_proposals * 100) if total_proposals > 0 else 0

        # Calculate activity metrics
        if events:
            first_event = datetime.fromisoformat(events[0]["timestamp"])
            last_event = datetime.fromisoformat(events[-1]["timestamp"])
            days_active = (last_event - first_event).days + 1
            events_per_day = len(events) / max(days_active, 1)
        else:
            days_active = 0
            events_per_day = 0

        return {
            **stats,
            "acceptance_rate": acceptance_rate,
            "total_events": len(events),
            "days_active": days_active,
            "average_events_per_day": events_per_day
        }

    def _generate_highlights(self, events: List[Dict]) -> List[str]:
        """Generate highlights from recent events"""
        highlights = []

        # Count event types
        event_counts = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        if event_counts.get("module_generated", 0) > 0:
            highlights.append(f"✨ {event_counts['module_generated']} new modules generated")

        if event_counts.get("module_improved", 0) > 0:
            highlights.append(f"🔧 {event_counts['module_improved']} modules improved")

        if event_counts.get("bug_fixed", 0) > 0:
            highlights.append(f"🐛 {event_counts['bug_fixed']} bugs fixed")

        if event_counts.get("proposal_accepted", 0) > 0:
            highlights.append(f"✅ {event_counts['proposal_accepted']} proposals accepted")

        return highlights

    def _generate_recommendations(self, data: Dict) -> List[str]:
        """Generate recommendations based on evolution history"""
        recommendations = []
        stats = data.get("statistics", {})

        # Check proposal acceptance rate
        total_proposals = stats.get("total_proposals", 0)
        accepted = stats.get("accepted_proposals", 0)
        if total_proposals > 10:
            acceptance_rate = (accepted / total_proposals) * 100
            if acceptance_rate < 50:
                recommendations.append("Low proposal acceptance rate - review proposal quality")
            elif acceptance_rate > 90:
                recommendations.append("High acceptance rate - system is evolving effectively")

        # Check activity level
        events = data.get("evolution_events", [])
        if len(events) < 10:
            recommendations.append("Low evolution activity - consider more frequent improvements")

        # Check recent activity
        recent_events = self.get_evolution_history(days=7)
        if len(recent_events) == 0:
            recommendations.append("No recent evolution activity - activate auto-evolution mode")

        return recommendations


# Global reporter instance
_global_reporter = None

def get_reporter() -> EvolutionReporter:
    """Get or create global reporter instance"""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = EvolutionReporter()
    return _global_reporter


class ErrorCenter:
    """
    Error Center - Phase 1 Core Infrastructure

    Unified error management system that tracks, logs, and analyzes all errors.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.error_log = self.metrics_dir / "error_events.jsonl"

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        module_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> str:
        """
        Log an error event

        Args:
            error: Exception object
            context: Error context (params, state, etc.)
            module_id: Module where error occurred
            workflow_id: Workflow where error occurred

        Returns:
            Error signature (hash)
        """
        import hashlib

        error_signature = self._generate_error_signature(error, module_id)

        error_event = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_signature": error_signature,
            "module_id": module_id,
            "workflow_id": workflow_id,
            "context": context or {},
            "stack_trace": self._get_stack_trace(error)
        }

        # Append to JSONL file
        with open(self.error_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_event) + '\n')

        return error_signature

    def get_errors(
        self,
        limit: Optional[int] = None,
        module_id: Optional[str] = None,
        hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get error events

        Args:
            limit: Max number of errors to return
            module_id: Filter by module
            hours: Get errors from last N hours

        Returns:
            List of error events
        """
        if not self.error_log.exists():
            return []

        errors = []
        cutoff_time = None
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)

        with open(self.error_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    error_event = json.loads(line.strip())

                    # Filter by module
                    if module_id and error_event.get('module_id') != module_id:
                        continue

                    # Filter by time
                    if cutoff_time:
                        event_time = datetime.fromisoformat(error_event['timestamp'])
                        if event_time < cutoff_time:
                            continue

                    errors.append(error_event)
                except:
                    continue

        # Sort by timestamp (newest first)
        errors.sort(key=lambda x: x['timestamp'], reverse=True)

        if limit:
            errors = errors[:limit]

        return errors

    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get error statistics

        Args:
            hours: Time window for statistics

        Returns:
            Error statistics
        """
        errors = self.get_errors(hours=hours)

        error_types = {}
        error_signatures = {}
        module_errors = {}

        for error in errors:
            # Count by type
            error_type = error.get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

            # Count by signature
            sig = error.get('error_signature', 'unknown')
            error_signatures[sig] = error_signatures.get(sig, 0) + 1

            # Count by module
            module = error.get('module_id', 'unknown')
            module_errors[module] = module_errors.get(module, 0) + 1

        return {
            "total_errors": len(errors),
            "time_window_hours": hours,
            "error_by_type": error_types,
            "error_by_signature": error_signatures,
            "error_by_module": module_errors,
            "most_common_errors": sorted(
                error_signatures.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    def get_errors_by_signature(
        self,
        error_signature: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all errors with specific signature

        Args:
            error_signature: Error signature to filter by
            limit: Max number of errors to return

        Returns:
            List of error events with matching signature
        """
        if not self.error_log.exists():
            return []

        errors = []
        with open(self.error_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    error_event = json.loads(line.strip())
                    if error_event.get('error_signature') == error_signature:
                        errors.append(error_event)
                except:
                    continue

        # Sort by timestamp (newest first)
        errors.sort(key=lambda x: x['timestamp'], reverse=True)

        if limit:
            errors = errors[:limit]

        return errors

    def _generate_error_signature(self, error: Exception, module_id: Optional[str]) -> str:
        """Generate unique error signature"""
        import hashlib

        signature_parts = [
            type(error).__name__,
            str(error)[:100],
            module_id or ""
        ]

        signature_str = "|".join(signature_parts)
        return hashlib.md5(signature_str.encode()).hexdigest()[:12]

    def _get_stack_trace(self, error: Exception) -> str:
        """Extract stack trace from exception"""
        import traceback
        return "".join(traceback.format_exception(type(error), error, error.__traceback__))


class DebugEngine:
    """
    Debug Engine - Phase 1 Core Infrastructure

    System health analyzer that detects patterns and suggests fixes.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.error_center = ErrorCenter(project_root)

    async def analyze_system_health(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze system health over time window

        Args:
            hours: Time window for analysis

        Returns:
            Health analysis report
        """
        stats = self.error_center.get_error_statistics(hours=hours)
        errors = self.error_center.get_errors(hours=hours)

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "time_window_hours": hours,
            "summary": self._generate_summary(stats, errors),
            "priority_issues": self._identify_priority_issues(stats, errors),
            "recommendations": self._generate_recommendations(stats, errors),
            "health_score": self._calculate_health_score(stats)
        }

        return analysis

    def _generate_summary(self, stats: Dict, errors: List[Dict]) -> str:
        """Generate health summary"""
        total_errors = stats.get('total_errors', 0)
        hours = stats.get('time_window_hours', 24)

        if total_errors == 0:
            return f"System is healthy. No errors in the last {hours} hours."
        elif total_errors < 5:
            return f"System is mostly stable. {total_errors} errors in the last {hours} hours."
        elif total_errors < 20:
            return f"System has moderate issues. {total_errors} errors detected. Review recommended."
        else:
            return f"System health critical. {total_errors} errors detected. Immediate action required."

    def _identify_priority_issues(self, stats: Dict, errors: List[Dict]) -> List[Dict[str, Any]]:
        """Identify high priority issues"""
        issues = []

        # Most common errors
        most_common = stats.get('most_common_errors', [])
        for sig, count in most_common[:3]:
            if count >= 3:
                # Find an example error with this signature
                example = next((e for e in errors if e.get('error_signature') == sig), None)

                issues.append({
                    "type": "recurring_error",
                    "signature": sig,
                    "count": count,
                    "error_type": example.get('error_type') if example else 'Unknown',
                    "error_message": example.get('error_message') if example else 'Unknown',
                    "module_id": example.get('module_id') if example else None,
                    "priority": "high" if count >= 10 else "medium"
                })

        # Module with most errors
        module_errors = stats.get('error_by_module', {})
        if module_errors:
            worst_module = max(module_errors.items(), key=lambda x: x[1])
            if worst_module[1] >= 5:
                issues.append({
                    "type": "problematic_module",
                    "module_id": worst_module[0],
                    "error_count": worst_module[1],
                    "priority": "high"
                })

        return issues

    def _generate_recommendations(self, stats: Dict, errors: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        total_errors = stats.get('total_errors', 0)

        if total_errors >= 20:
            recommendations.append("Critical: Run full system diagnostic")
            recommendations.append("Consider rolling back recent changes")

        most_common = stats.get('most_common_errors', [])
        if most_common:
            top_error_sig = most_common[0][0]
            top_error_count = most_common[0][1]

            if top_error_count >= 5:
                recommendations.append(f"Priority: Fix recurring error (signature: {top_error_sig}, {top_error_count} occurrences)")

        module_errors = stats.get('error_by_module', {})
        if module_errors:
            worst_module = max(module_errors.items(), key=lambda x: x[1])
            if worst_module[1] >= 5:
                recommendations.append(f"Review module: {worst_module[0]} ({worst_module[1]} errors)")

        if not recommendations:
            recommendations.append("System is stable. Continue monitoring.")

        return recommendations

    def _calculate_health_score(self, stats: Dict) -> float:
        """
        Calculate health score (0-100)

        Higher score = better health
        """
        total_errors = stats.get('total_errors', 0)

        # Base score
        if total_errors == 0:
            return 100.0
        elif total_errors < 5:
            return 90.0 - (total_errors * 2)
        elif total_errors < 20:
            return 80.0 - (total_errors - 5)
        else:
            return max(0.0, 60.0 - (total_errors - 20))


# Global instances
_error_center = None
_debug_engine = None

def get_error_center() -> ErrorCenter:
    """Get singleton error center instance"""
    global _error_center
    if _error_center is None:
        _error_center = ErrorCenter()
    return _error_center

def get_debug_engine() -> DebugEngine:
    """Get singleton debug engine instance"""
    global _debug_engine
    if _debug_engine is None:
        _debug_engine = DebugEngine()
    return _debug_engine
