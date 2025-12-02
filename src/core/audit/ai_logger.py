"""
AI Audit Logger
Records AI decision-making processes and reasoning
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class AIAuditLogger:
    """
    Logger for AI decision-making processes
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.log_file = self.metrics_dir / "ai_audit.jsonl"

    def log_decision(
        self,
        decision_type: str,
        context: Dict[str, Any],
        reasoning: str,
        outcome: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an AI decision

        Args:
            decision_type: Type of decision (e.g., 'escalation', 'module_proposal', 'test_strategy')
            context: Context information that led to the decision
            reasoning: AI reasoning process
            outcome: The decision outcome
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "context": context,
            "reasoning": reasoning,
            "outcome": outcome,
            "confidence": confidence,
            "metadata": metadata or {}
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def log_thought_process(
        self,
        step: str,
        thought: str,
        alternatives: Optional[list] = None,
        selected: Optional[str] = None
    ):
        """
        Log AI thought process step

        Args:
            step: Current step in the process
            thought: The thought or consideration
            alternatives: Alternative approaches considered
            selected: Which alternative was selected
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "thought_process",
            "step": step,
            "thought": thought,
            "alternatives": alternatives or [],
            "selected": selected
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_recent_logs(self, limit: int = 100) -> list:
        """
        Get recent audit log entries

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []

        entries = []
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        return entries[-limit:]

    def get_decisions_by_type(self, decision_type: str) -> list:
        """
        Get all decisions of a specific type

        Args:
            decision_type: Type of decision to filter by

        Returns:
            List of matching log entries
        """
        if not self.log_file.exists():
            return []

        entries = []
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get('decision_type') == decision_type:
                        entries.append(entry)

        return entries


# Global logger instance
_global_logger = None

def get_logger() -> AIAuditLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AIAuditLogger()
    return _global_logger
