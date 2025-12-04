"""
Metrics Collector for Module Generation and Auto-Refine Performance

Collects and stores metrics to cloud PostgreSQL database.
Zero coupling - pure function design with dependency injection.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .db_manager import DatabaseManager


class MetricsCollector:
    """
    Collects and stores metrics for module generation and auto-refine performance

    Pure, stateless component with zero coupling.
    All dependencies injected through constructor.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize metrics collector

        Args:
            db_manager: DatabaseManager instance (defaults to new instance)
        """
        self.db_manager = db_manager or DatabaseManager()

    def record_module_metric(
        self,
        module_name: str,
        task_description: str,
        initial_score: float,
        final_score: float,
        attempts: int,
        success: bool,
        model_used: str,
        total_time_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Record module generation metric

        Args:
            module_name: Name of the module
            task_description: Task description
            initial_score: Initial quality score
            final_score: Final quality score
            attempts: Number of attempts
            success: Whether generation succeeded
            model_used: Model name used
            total_time_seconds: Total time taken
            metadata: Additional metadata

        Returns:
            ID of inserted record
        """
        return self.db_manager.insert_module_metric(
            module_name=module_name,
            task_description=task_description,
            initial_score=initial_score,
            final_score=final_score,
            attempts=attempts,
            success=success,
            model_used=model_used,
            total_time_seconds=total_time_seconds,
            metadata=metadata
        )

    def record_refine_iteration(
        self,
        module_metrics_id: int,
        iteration_number: int,
        score_before: float,
        score_after: float,
        issues_before: List[Dict[str, Any]],
        issues_after: List[Dict[str, Any]],
        strategy_used: str,
        code_similarity: Optional[float] = None
    ) -> int:
        """
        Record refine iteration metric

        Args:
            module_metrics_id: Foreign key to module_metrics
            iteration_number: Iteration number
            score_before: Score before iteration
            score_after: Score after iteration
            issues_before: Issues before iteration
            issues_after: Issues after iteration
            strategy_used: Strategy used for refinement
            code_similarity: Code similarity ratio

        Returns:
            ID of inserted record
        """
        return self.db_manager.insert_refine_iteration(
            module_metrics_id=module_metrics_id,
            iteration_number=iteration_number,
            score_before=score_before,
            score_after=score_after,
            issues_before=issues_before,
            issues_after=issues_after,
            strategy_used=strategy_used,
            code_similarity=code_similarity
        )

    def get_recent_modules(
        self,
        limit: int = 100,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent module metrics

        Args:
            limit: Maximum number of records to return
            min_score: Minimum score filter (optional)

        Returns:
            List of module metric records
        """
        sql = """
            SELECT
                id,
                module_name,
                task_description,
                initial_score,
                final_score,
                attempts,
                success,
                model_used,
                total_time_seconds,
                created_at
            FROM module_metrics
            WHERE 1=1
        """
        params = []

        if min_score is not None:
            sql += " AND final_score >= %s"
            params.append(min_score)

        sql += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        return self.db_manager.query(sql, tuple(params))

    def get_module_iterations(
        self,
        module_metrics_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all refine iterations for a module

        Args:
            module_metrics_id: Module metrics ID

        Returns:
            List of refine iteration records
        """
        sql = """
            SELECT
                id,
                iteration_number,
                score_before,
                score_after,
                strategy_used,
                code_similarity,
                created_at
            FROM refine_iterations
            WHERE module_metrics_id = %s
            ORDER BY iteration_number ASC
        """
        return self.db_manager.query(sql, (module_metrics_id,))

    def get_summary_stats(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get summary statistics for recent metrics

        Args:
            days: Number of days to look back

        Returns:
            Dictionary of summary statistics
        """
        sql = """
            SELECT
                COUNT(*) as total_runs,
                SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) as successful_runs,
                AVG(final_score) as avg_final_score,
                AVG(attempts) as avg_attempts,
                AVG(total_time_seconds) as avg_time_seconds,
                MIN(final_score) as min_score,
                MAX(final_score) as max_score
            FROM module_metrics
            WHERE created_at >= NOW() - INTERVAL '%s days'
        """

        results = self.db_manager.query(sql, (days,))

        if not results:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "success_rate": 0.0,
                "avg_final_score": 0.0,
                "avg_attempts": 0.0,
                "avg_time_seconds": 0.0,
                "min_score": 0.0,
                "max_score": 0.0
            }

        stats = results[0]
        total = stats.get("total_runs", 0)
        successful = stats.get("successful_runs", 0)

        return {
            "total_runs": total,
            "successful_runs": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_final_score": float(stats.get("avg_final_score") or 0.0),
            "avg_attempts": float(stats.get("avg_attempts") or 0.0),
            "avg_time_seconds": float(stats.get("avg_time_seconds") or 0.0),
            "min_score": float(stats.get("min_score") or 0.0),
            "max_score": float(stats.get("max_score") or 0.0)
        }

    def get_model_comparison(self) -> List[Dict[str, Any]]:
        """
        Get performance comparison across different models

        Returns:
            List of model performance statistics
        """
        sql = """
            SELECT
                model_used,
                COUNT(*) as total_runs,
                SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) as successful_runs,
                AVG(final_score) as avg_score,
                AVG(attempts) as avg_attempts,
                AVG(total_time_seconds) as avg_time_seconds
            FROM module_metrics
            GROUP BY model_used
            ORDER BY avg_score DESC
        """

        results = self.db_manager.query(sql)

        for row in results:
            total = row.get("total_runs", 0)
            successful = row.get("successful_runs", 0)
            row["success_rate"] = successful / total if total > 0 else 0.0

        return results
