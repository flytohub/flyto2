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
