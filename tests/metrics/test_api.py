"""
Unit tests for Metrics API Server

Tests the FastAPI endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock

from src.core.metrics.api import app


class TestMetricsAPI:
    """Test suite for Metrics API"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_collector(self):
        """Create mock MetricsCollector"""
        with patch("src.core.metrics.api.collector") as mock:
            yield mock

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_get_modules(self, client, mock_collector):
        """Test GET /api/metrics/modules"""
        mock_collector.get_recent_modules.return_value = [
            {
                "id": 1,
                "module_name": "test.module1",
                "final_score": 9.5
            },
            {
                "id": 2,
                "module_name": "test.module2",
                "final_score": 9.8
            }
        ]

        response = client.get("/api/metrics/modules")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["modules"]) == 2
        assert data["modules"][0]["module_name"] == "test.module1"

    def test_get_modules_with_limit(self, client, mock_collector):
        """Test GET /api/metrics/modules with limit parameter"""
        mock_collector.get_recent_modules.return_value = []

        response = client.get("/api/metrics/modules?limit=50")

        assert response.status_code == 200
        mock_collector.get_recent_modules.assert_called_once()
        call_kwargs = mock_collector.get_recent_modules.call_args[1]
        assert call_kwargs["limit"] == 50

    def test_get_modules_with_min_score(self, client, mock_collector):
        """Test GET /api/metrics/modules with min_score parameter"""
        mock_collector.get_recent_modules.return_value = []

        response = client.get("/api/metrics/modules?min_score=9.0")

        assert response.status_code == 200
        call_kwargs = mock_collector.get_recent_modules.call_args[1]
        assert call_kwargs["min_score"] == 9.0

    def test_get_modules_invalid_limit(self, client, mock_collector):
        """Test GET /api/metrics/modules with invalid limit"""
        response = client.get("/api/metrics/modules?limit=0")

        assert response.status_code == 422

    def test_get_modules_error(self, client, mock_collector):
        """Test GET /api/metrics/modules with database error"""
        mock_collector.get_recent_modules.side_effect = Exception("Database error")

        response = client.get("/api/metrics/modules")

        assert response.status_code == 500

    def test_get_module_iterations(self, client, mock_collector):
        """Test GET /api/metrics/modules/{id}/iterations"""
        mock_collector.get_module_iterations.return_value = [
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

        response = client.get("/api/metrics/modules/123/iterations")

        assert response.status_code == 200
        data = response.json()
        assert data["module_metrics_id"] == 123
        assert data["total_iterations"] == 2
        assert len(data["iterations"]) == 2

    def test_get_summary(self, client, mock_collector):
        """Test GET /api/metrics/summary"""
        mock_collector.get_summary_stats.return_value = {
            "total_runs": 100,
            "successful_runs": 85,
            "success_rate": 0.85,
            "avg_final_score": 9.45,
            "avg_attempts": 1.8,
            "avg_time_seconds": 22.5,
            "min_score": 8.0,
            "max_score": 10.0
        }

        response = client.get("/api/metrics/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_runs"] == 100
        assert data["success_rate"] == 0.85
        assert data["avg_final_score"] == 9.45

    def test_get_summary_with_days(self, client, mock_collector):
        """Test GET /api/metrics/summary with days parameter"""
        mock_collector.get_summary_stats.return_value = {
            "total_runs": 50,
            "successful_runs": 40,
            "success_rate": 0.8,
            "avg_final_score": 9.3,
            "avg_attempts": 2.0,
            "avg_time_seconds": 25.0,
            "min_score": 7.5,
            "max_score": 10.0
        }

        response = client.get("/api/metrics/summary?days=7")

        assert response.status_code == 200
        mock_collector.get_summary_stats.assert_called_once_with(days=7)

    def test_get_model_comparison(self, client, mock_collector):
        """Test GET /api/metrics/models"""
        mock_collector.get_model_comparison.return_value = [
            {
                "model_used": "gpt-4o",
                "total_runs": 100,
                "success_rate": 0.95
            },
            {
                "model_used": "gpt-3.5-turbo",
                "total_runs": 50,
                "success_rate": 0.80
            }
        ]

        response = client.get("/api/metrics/models")

        assert response.status_code == 200
        data = response.json()
        assert data["total_models"] == 2
        assert len(data["models"]) == 2
        assert data["models"][0]["model_used"] == "gpt-4o"

    def test_record_module_metric(self, client, mock_collector):
        """Test POST /api/metrics/modules"""
        mock_collector.record_module_metric.return_value = 123

        payload = {
            "module_name": "test.module",
            "task_description": "Test task",
            "initial_score": 8.5,
            "final_score": 9.6,
            "attempts": 2,
            "success": True,
            "model_used": "gpt-4o",
            "total_time_seconds": 15.3
        }

        response = client.post("/api/metrics/modules", params=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["status"] == "created"

    def test_record_module_metric_minimal(self, client, mock_collector):
        """Test POST /api/metrics/modules with minimal parameters"""
        mock_collector.record_module_metric.return_value = 456

        payload = {
            "module_name": "simple.module",
            "task_description": "Simple task",
            "initial_score": 8.0,
            "final_score": 9.0,
            "attempts": 1,
            "success": True,
            "model_used": "gpt-4o"
        }

        response = client.post("/api/metrics/modules", params=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 456

    def test_record_refine_iteration(self, client, mock_collector):
        """Test POST /api/metrics/iterations"""
        mock_collector.record_refine_iteration.return_value = 789

        payload = {
            "module_metrics_id": 123,
            "iteration_number": 1,
            "score_before": 8.5,
            "score_after": 9.6,
            "issues_before": [{"type": "nested_function"}],
            "issues_after": [],
            "strategy_used": "targeted_fix",
            "code_similarity": 0.85
        }

        response = client.post("/api/metrics/iterations", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 789
        assert data["status"] == "created"

    def test_get_summary_invalid_days(self, client, mock_collector):
        """Test GET /api/metrics/summary with invalid days parameter"""
        response = client.get("/api/metrics/summary?days=0")

        assert response.status_code == 422

    def test_get_summary_error(self, client, mock_collector):
        """Test GET /api/metrics/summary with error"""
        mock_collector.get_summary_stats.side_effect = Exception("Database error")

        response = client.get("/api/metrics/summary")

        assert response.status_code == 500

    def test_get_model_comparison_error(self, client, mock_collector):
        """Test GET /api/metrics/models with error"""
        mock_collector.get_model_comparison.side_effect = Exception("Database error")

        response = client.get("/api/metrics/models")

        assert response.status_code == 500

    def test_record_module_metric_error(self, client, mock_collector):
        """Test POST /api/metrics/modules with error"""
        mock_collector.record_module_metric.side_effect = Exception("Database error")

        payload = {
            "module_name": "test.module",
            "task_description": "Test task",
            "initial_score": 8.5,
            "final_score": 9.6,
            "attempts": 2,
            "success": True,
            "model_used": "gpt-4o"
        }

        response = client.post("/api/metrics/modules", params=payload)

        assert response.status_code == 500

    def test_record_refine_iteration_error(self, client, mock_collector):
        """Test POST /api/metrics/iterations with error"""
        mock_collector.record_refine_iteration.side_effect = Exception("Database error")

        payload = {
            "module_metrics_id": 123,
            "iteration_number": 1,
            "score_before": 8.5,
            "score_after": 9.6,
            "issues_before": [],
            "issues_after": [],
            "strategy_used": "targeted_fix"
        }

        response = client.post("/api/metrics/iterations", json=payload)

        assert response.status_code == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
