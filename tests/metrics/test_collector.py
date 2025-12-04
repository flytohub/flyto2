"""
Unit tests for MetricsCollector component

Tests the metrics collection functionality using mocked database.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.core.metrics.collector import MetricsCollector
from src.core.metrics.db_manager import DatabaseManager


class TestMetricsCollector:
    """Test suite for MetricsCollector"""

    @pytest.fixture
    def mock_db_manager(self):
        """Create mock DatabaseManager"""
        mock = Mock(spec=DatabaseManager)
        return mock

    @pytest.fixture
    def collector(self, mock_db_manager):
        """Create MetricsCollector with mock database"""
        return MetricsCollector(db_manager=mock_db_manager)

    def test_collector_initialization(self):
        """Test collector can be initialized"""
        collector = MetricsCollector()
        assert collector is not None
        assert collector.db_manager is not None

    def test_collector_initialization_with_custom_db(self, mock_db_manager):
        """Test collector can be initialized with custom db_manager"""
        collector = MetricsCollector(db_manager=mock_db_manager)
        assert collector.db_manager == mock_db_manager

    def test_record_module_metric(self, collector, mock_db_manager):
        """Test recording module metric"""
        mock_db_manager.insert_module_metric.return_value = 123

        result = collector.record_module_metric(
            module_name="test.module",
            task_description="Test task",
            initial_score=8.5,
            final_score=9.6,
            attempts=2,
            success=True,
            model_used="gpt-4o",
            total_time_seconds=15.3,
            metadata={"key": "value"}
        )

        assert result == 123
        mock_db_manager.insert_module_metric.assert_called_once()
        call_args = mock_db_manager.insert_module_metric.call_args[1]
        assert call_args["module_name"] == "test.module"
        assert call_args["initial_score"] == 8.5
        assert call_args["final_score"] == 9.6

    def test_record_module_metric_minimal_params(self, collector, mock_db_manager):
        """Test recording module metric with minimal parameters"""
        mock_db_manager.insert_module_metric.return_value = 456

        result = collector.record_module_metric(
            module_name="simple.module",
            task_description="Simple task",
            initial_score=7.0,
            final_score=9.0,
            attempts=1,
            success=True,
            model_used="gpt-4o"
        )

        assert result == 456
        mock_db_manager.insert_module_metric.assert_called_once()

    def test_record_refine_iteration(self, collector, mock_db_manager):
        """Test recording refine iteration"""
        mock_db_manager.insert_refine_iteration.return_value = 789

        issues_before = [{"type": "nested_function", "deduction": 0.5}]
        issues_after = []

        result = collector.record_refine_iteration(
            module_metrics_id=123,
            iteration_number=1,
            score_before=8.5,
            score_after=9.6,
            issues_before=issues_before,
            issues_after=issues_after,
            strategy_used="targeted_fix",
            code_similarity=0.85
        )

        assert result == 789
        mock_db_manager.insert_refine_iteration.assert_called_once()
        call_args = mock_db_manager.insert_refine_iteration.call_args[1]
        assert call_args["module_metrics_id"] == 123
        assert call_args["iteration_number"] == 1
        assert call_args["score_before"] == 8.5
        assert call_args["score_after"] == 9.6

    def test_get_recent_modules(self, collector, mock_db_manager):
        """Test getting recent modules"""
        mock_results = [
            {
                "id": 1,
                "module_name": "test.module1",
                "final_score": 9.5,
                "success": True
            },
            {
                "id": 2,
                "module_name": "test.module2",
                "final_score": 9.8,
                "success": True
            }
        ]
        mock_db_manager.query.return_value = mock_results

        results = collector.get_recent_modules(limit=100)

        assert len(results) == 2
        assert results[0]["module_name"] == "test.module1"
        assert results[1]["module_name"] == "test.module2"
        mock_db_manager.query.assert_called_once()

    def test_get_recent_modules_with_min_score(self, collector, mock_db_manager):
        """Test getting recent modules with minimum score filter"""
        mock_db_manager.query.return_value = []

        collector.get_recent_modules(limit=50, min_score=9.0)

        mock_db_manager.query.assert_called_once()
        sql, params = mock_db_manager.query.call_args[0]
        assert "final_score >=" in sql
        assert 9.0 in params

    def test_get_module_iterations(self, collector, mock_db_manager):
        """Test getting module iterations"""
        mock_iterations = [
            {
                "id": 1,
                "iteration_number": 1,
                "score_before": 8.5,
                "score_after": 9.0
            },
            {
                "id": 2,
                "iteration_number": 2,
                "score_before": 9.0,
                "score_after": 9.6
            }
        ]
        mock_db_manager.query.return_value = mock_iterations

        results = collector.get_module_iterations(module_metrics_id=123)

        assert len(results) == 2
        assert results[0]["iteration_number"] == 1
        assert results[1]["iteration_number"] == 2
        mock_db_manager.query.assert_called_once()

    def test_get_summary_stats(self, collector, mock_db_manager):
        """Test getting summary statistics"""
        mock_db_manager.query.return_value = [{
            "total_runs": 100,
            "successful_runs": 85,
            "avg_final_score": 9.45,
            "avg_attempts": 1.8,
            "avg_time_seconds": 22.5,
            "min_score": 8.0,
            "max_score": 10.0
        }]

        stats = collector.get_summary_stats(days=30)

        assert stats["total_runs"] == 100
        assert stats["successful_runs"] == 85
        assert stats["success_rate"] == 0.85
        assert stats["avg_final_score"] == 9.45
        assert stats["avg_attempts"] == 1.8
        assert stats["avg_time_seconds"] == 22.5
        assert stats["min_score"] == 8.0
        assert stats["max_score"] == 10.0

    def test_get_summary_stats_empty_results(self, collector, mock_db_manager):
        """Test getting summary stats with no results"""
        mock_db_manager.query.return_value = []

        stats = collector.get_summary_stats(days=30)

        assert stats["total_runs"] == 0
        assert stats["successful_runs"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["avg_final_score"] == 0.0

    def test_get_summary_stats_with_none_values(self, collector, mock_db_manager):
        """Test getting summary stats with None values"""
        mock_db_manager.query.return_value = [{
            "total_runs": 10,
            "successful_runs": 5,
            "avg_final_score": None,
            "avg_attempts": None,
            "avg_time_seconds": None,
            "min_score": None,
            "max_score": None
        }]

        stats = collector.get_summary_stats(days=30)

        assert stats["total_runs"] == 10
        assert stats["success_rate"] == 0.5
        assert stats["avg_final_score"] == 0.0
        assert stats["avg_attempts"] == 0.0

    def test_get_model_comparison(self, collector, mock_db_manager):
        """Test getting model comparison"""
        mock_db_manager.query.return_value = [
            {
                "model_used": "gpt-4o",
                "total_runs": 100,
                "successful_runs": 95,
                "avg_score": 9.7,
                "avg_attempts": 1.5,
                "avg_time_seconds": 20.0
            },
            {
                "model_used": "gpt-3.5-turbo",
                "total_runs": 50,
                "successful_runs": 40,
                "avg_score": 9.2,
                "avg_attempts": 2.0,
                "avg_time_seconds": 18.0
            }
        ]

        results = collector.get_model_comparison()

        assert len(results) == 2
        assert results[0]["model_used"] == "gpt-4o"
        assert results[0]["success_rate"] == 0.95
        assert results[1]["model_used"] == "gpt-3.5-turbo"
        assert results[1]["success_rate"] == 0.80

    def test_get_model_comparison_zero_runs(self, collector, mock_db_manager):
        """Test model comparison with zero runs"""
        mock_db_manager.query.return_value = [
            {
                "model_used": "test-model",
                "total_runs": 0,
                "successful_runs": 0,
                "avg_score": 0.0,
                "avg_attempts": 0.0,
                "avg_time_seconds": 0.0
            }
        ]

        results = collector.get_model_comparison()

        assert len(results) == 1
        assert results[0]["success_rate"] == 0.0

    def test_record_module_metric_with_failure(self, collector, mock_db_manager):
        """Test recording failed module generation"""
        mock_db_manager.insert_module_metric.return_value = 999

        result = collector.record_module_metric(
            module_name="failed.module",
            task_description="Failed task",
            initial_score=8.0,
            final_score=8.2,
            attempts=5,
            success=False,
            model_used="gpt-4o"
        )

        assert result == 999
        call_args = mock_db_manager.insert_module_metric.call_args[1]
        assert call_args["success"] is False
        assert call_args["attempts"] == 5

    def test_get_recent_modules_empty_results(self, collector, mock_db_manager):
        """Test getting recent modules with no results"""
        mock_db_manager.query.return_value = []

        results = collector.get_recent_modules()

        assert len(results) == 0

    def test_get_module_iterations_empty_results(self, collector, mock_db_manager):
        """Test getting iterations with no results"""
        mock_db_manager.query.return_value = []

        results = collector.get_module_iterations(module_metrics_id=999)

        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
