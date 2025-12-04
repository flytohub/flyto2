"""
Unit tests for AutoRefiner V3 Metrics Integration

Tests that metrics are properly collected during the auto-refine process.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.core.meta.auto_refiner_v3 import (
    MultiPassRefiner,
    Issue,
    QualityReport,
    RoundResult,
    RefineResult,
)


class TestAutoRefinerMetricsIntegration:
    """Test suite for auto-refiner metrics collection"""

    @pytest.fixture
    def mock_quality_checker(self):
        """Create mock quality checker"""
        mock = Mock()
        mock.review_module.return_value = {
            "score": 9.6,
            "passed": True,
            "issues": [],
            "checks": []
        }
        return mock

    @pytest.fixture
    def mock_metrics_collector(self):
        """Create mock metrics collector"""
        mock = Mock()
        # Return a module_metrics_id when record_module_metric is called
        mock.record_module_metric.return_value = 123
        return mock

    @pytest.fixture
    def sample_code(self, tmp_path):
        """Create a sample Python module file"""
        code = '''
def test_function():
    """Test function"""
    return {"ok": True, "output": {}, "error": None, "meta": {}}
'''
        file_path = tmp_path / "test_module.py"
        file_path.write_text(code)
        return str(file_path), code

    def test_refiner_without_metrics_collector(
        self,
        mock_quality_checker,
        sample_code
    ):
        """Test that refiner works without metrics collector (backward compatibility)"""
        file_path, code = sample_code

        refiner = MultiPassRefiner(
            quality_checker=mock_quality_checker,
            openai_api_key="test-key",
            max_rounds=3,
            target_score=9.5,
            metrics_collector=None  # No metrics collection
        )

        # Mock the executor to avoid real API calls
        refiner.executor = Mock()
        refiner.executor.refine_once.return_value = code

        initial_result = {
            "score": 9.6,
            "passed": True,
            "issues": [],
            "checks": []
        }

        result = refiner.refine_module(file_path, code, initial_result)

        # Should work fine without metrics
        assert result.initial_score == 9.6
        assert result.final_score == 9.6
        assert result.achieved_target is True

    def test_refiner_with_metrics_collector(
        self,
        mock_quality_checker,
        mock_metrics_collector,
        sample_code
    ):
        """Test that refiner records metrics when collector is provided"""
        file_path, code = sample_code

        refiner = MultiPassRefiner(
            quality_checker=mock_quality_checker,
            openai_api_key="test-key",
            max_rounds=3,
            target_score=9.5,
            metrics_collector=mock_metrics_collector
        )

        # Mock the executor to return modified code (different from input)
        modified_code = code + "\n# Fixed issue"
        refiner.executor = Mock()
        refiner.executor.refine_once.return_value = modified_code

        initial_result = {
            "score": 8.5,
            "passed": False,
            "issues": [
                {"message": "Generic exception handler", "deduction": 0.5}
            ],
            "checks": []
        }

        # Mock quality checker to show improvement
        mock_quality_checker.review_module.return_value = {
            "score": 9.6,
            "passed": True,
            "issues": [],
            "checks": []
        }

        result = refiner.refine_module(file_path, code, initial_result)

        # Should have called record_module_metric
        assert mock_metrics_collector.record_module_metric.called
        call_kwargs = mock_metrics_collector.record_module_metric.call_args[1]

        # Verify module metric parameters
        assert call_kwargs["module_name"] == "test_module"
        assert call_kwargs["initial_score"] == 8.5
        assert call_kwargs["final_score"] == 9.6
        assert call_kwargs["success"] is True
        assert call_kwargs["model_used"] == "gpt-4o"
        assert "total_improvement" in call_kwargs["metadata"]

    def test_refiner_records_iterations(
        self,
        mock_quality_checker,
        mock_metrics_collector,
        sample_code
    ):
        """Test that each refine iteration is recorded"""
        file_path, code = sample_code

        refiner = MultiPassRefiner(
            quality_checker=mock_quality_checker,
            openai_api_key="test-key",
            max_rounds=2,
            target_score=9.5,
            metrics_collector=mock_metrics_collector
        )

        # Mock the executor to return different code each time
        codes = [code + "\n# Fix 1", code + "\n# Fix 2"]
        def get_next_code(*args, **kwargs):
            return codes.pop(0) if codes else code + "\n# Default"

        refiner.executor = Mock()
        refiner.executor.refine_once.side_effect = get_next_code

        initial_result = {
            "score": 8.0,
            "passed": False,
            "issues": [
                {"message": "Generic exception handler", "deduction": 0.5}
            ],
            "checks": []
        }

        # Mock quality checker to show gradual improvement
        scores = [8.5, 9.6]
        def side_effect(*args, **kwargs):
            score = scores.pop(0) if scores else 9.6
            return {
                "score": score,
                "passed": score >= 9.5,
                "issues": [],
                "checks": []
            }

        mock_quality_checker.review_module.side_effect = side_effect

        result = refiner.refine_module(file_path, code, initial_result)

        # Should have recorded module metric
        assert mock_metrics_collector.record_module_metric.called

        # Should have recorded iterations
        assert mock_metrics_collector.record_refine_iteration.called
        # At least 1 iteration should be recorded (may stop early if target reached)
        assert mock_metrics_collector.record_refine_iteration.call_count >= 1

    def test_metrics_failure_doesnt_break_refine(
        self,
        mock_quality_checker,
        mock_metrics_collector,
        sample_code
    ):
        """Test that metrics collection failure doesn't break the refine process"""
        file_path, code = sample_code

        # Make metrics collector raise an exception
        mock_metrics_collector.record_module_metric.side_effect = Exception("Database error")

        refiner = MultiPassRefiner(
            quality_checker=mock_quality_checker,
            openai_api_key="test-key",
            max_rounds=3,
            target_score=9.5,
            metrics_collector=mock_metrics_collector
        )

        # Mock the executor
        refiner.executor = Mock()
        refiner.executor.refine_once.return_value = code

        initial_result = {
            "score": 9.6,
            "passed": True,
            "issues": [],
            "checks": []
        }

        # Should not raise exception even though metrics collection fails
        result = refiner.refine_module(file_path, code, initial_result)

        assert result.initial_score == 9.6
        assert result.final_score == 9.6

    def test_metrics_records_correct_module_name(
        self,
        mock_quality_checker,
        mock_metrics_collector,
        tmp_path
    ):
        """Test that metrics correctly extracts module name from path"""
        code = 'def test(): return {"ok": True, "output": {}, "error": None, "meta": {}}'
        file_path = tmp_path / "subdir" / "my_custom_module.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code)

        refiner = MultiPassRefiner(
            quality_checker=mock_quality_checker,
            openai_api_key="test-key",
            metrics_collector=mock_metrics_collector
        )

        refiner.executor = Mock()
        refiner.executor.refine_once.return_value = code

        initial_result = {
            "score": 9.6,
            "passed": True,
            "issues": [],
            "checks": []
        }

        result = refiner.refine_module(str(file_path), code, initial_result)

        # Check that correct module name was used
        call_kwargs = mock_metrics_collector.record_module_metric.call_args[1]
        assert call_kwargs["module_name"] == "my_custom_module"

    def test_iteration_records_strategy(
        self,
        mock_quality_checker,
        mock_metrics_collector,
        sample_code
    ):
        """Test that iteration records include strategy used"""
        file_path, code = sample_code

        refiner = MultiPassRefiner(
            quality_checker=mock_quality_checker,
            openai_api_key="test-key",
            max_rounds=1,
            target_score=9.5,
            metrics_collector=mock_metrics_collector
        )

        refiner.executor = Mock()
        refiner.executor.refine_once.return_value = code

        initial_result = {
            "score": 8.0,
            "passed": False,
            "issues": [
                {"message": "Generic exception handler", "deduction": 0.5}
            ],
            "checks": []
        }

        mock_quality_checker.review_module.return_value = {
            "score": 9.6,
            "passed": True,
            "issues": [],
            "checks": []
        }

        result = refiner.refine_module(file_path, code, initial_result)

        # Check iteration recording
        if mock_metrics_collector.record_refine_iteration.called:
            call_kwargs = mock_metrics_collector.record_refine_iteration.call_args[1]
            assert "strategy_used" in call_kwargs
            assert isinstance(call_kwargs["strategy_used"], str)

    def test_custom_model_name_in_metrics(
        self,
        mock_quality_checker,
        mock_metrics_collector,
        sample_code
    ):
        """Test that custom model name is recorded in metrics"""
        file_path, code = sample_code

        refiner = MultiPassRefiner(
            quality_checker=mock_quality_checker,
            openai_api_key="test-key",
            metrics_collector=mock_metrics_collector,
            model_name="claude-3.7-sonnet"  # Custom model name
        )

        refiner.executor = Mock()
        refiner.executor.refine_once.return_value = code

        initial_result = {
            "score": 9.6,
            "passed": True,
            "issues": [],
            "checks": []
        }

        result = refiner.refine_module(file_path, code, initial_result)

        # Check that custom model name was used
        call_kwargs = mock_metrics_collector.record_module_metric.call_args[1]
        assert call_kwargs["model_used"] == "claude-3.7-sonnet"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
