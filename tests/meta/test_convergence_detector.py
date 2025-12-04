"""
Unit tests for ConvergenceDetector component

Tests the convergence detection functionality for refinement process.
"""

import pytest
from src.core.meta.convergence_detector import (
    ConvergenceDetector,
    ConvergenceReason,
    ConvergenceResult
)


class TestConvergenceDetector:
    """Test suite for ConvergenceDetector"""

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return ConvergenceDetector()

    @pytest.fixture
    def sample_history_target_reached(self):
        """Sample history with target reached"""
        return [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 9.0, "code": "code2"},
            {"attempt": 3, "score": 9.6, "code": "code3"}
        ]

    @pytest.fixture
    def sample_history_plateau(self):
        """Sample history with score plateau"""
        return [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 8.05, "code": "code2"},
            {"attempt": 3, "score": 8.08, "code": "code3"}
        ]

    @pytest.fixture
    def sample_history_no_improvement(self):
        """Sample history with no improvement"""
        return [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 7.9, "code": "code2"},
            {"attempt": 3, "score": 7.8, "code": "code3"}
        ]

    def test_detect_returns_convergence_result(self, detector):
        """Test that detect returns ConvergenceResult"""
        history = [{"attempt": 1, "score": 8.0, "code": "code1"}]
        result = detector.detect(history)

        assert isinstance(result, ConvergenceResult)

    def test_detect_empty_history(self, detector):
        """Test detect with empty history"""
        result = detector.detect([])

        assert result.has_converged is False
        assert result.reason is None

    def test_detect_target_reached(self, detector, sample_history_target_reached):
        """Test detection when target score is reached"""
        result = detector.detect(sample_history_target_reached, target_score=9.5)

        assert result.has_converged is True
        assert result.reason == ConvergenceReason.TARGET_REACHED
        assert result.confidence == 1.0

    def test_detect_score_plateau(self, detector, sample_history_plateau):
        """Test detection of score plateau"""
        result = detector.detect(sample_history_plateau, target_score=9.5)

        assert result.has_converged is True
        assert result.reason == ConvergenceReason.SCORE_PLATEAU

    def test_detect_no_improvement(self, detector, sample_history_no_improvement):
        """Test detection of no improvement"""
        result = detector.detect(sample_history_no_improvement, target_score=9.5)

        assert result.has_converged is True
        assert result.reason == ConvergenceReason.NO_IMPROVEMENT

    def test_detect_minimal_changes(self, detector):
        """Test detection of minimal changes"""
        history = [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 8.1, "code": "code2", "similarity_to_previous": 0.995}
        ]

        result = detector.detect(history, target_score=9.5)

        assert result.has_converged is True
        assert result.reason == ConvergenceReason.MINIMAL_CHANGES

    def test_detect_infinite_loop(self, detector):
        """Test detection of infinite loop"""
        same_code = "def test():\n    pass"
        history = [
            {"attempt": 1, "score": 8.0, "code": same_code},
            {"attempt": 2, "score": 8.1, "code": "different code"},
            {"attempt": 3, "score": 8.2, "code": same_code}
        ]

        result = detector.detect(history, target_score=9.5)

        assert result.has_converged is True
        assert result.reason == ConvergenceReason.INFINITE_LOOP

    def test_detect_single_attempt(self, detector):
        """Test detect with single attempt"""
        history = [{"attempt": 1, "score": 8.0, "code": "code1"}]
        result = detector.detect(history, target_score=9.5)

        assert result.has_converged is False

    def test_convergence_result_to_dict(self):
        """Test ConvergenceResult.to_dict()"""
        result = ConvergenceResult(
            has_converged=True,
            reason=ConvergenceReason.TARGET_REACHED,
            confidence=1.0,
            details={"score": 9.6}
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["has_converged"] is True
        assert result_dict["reason"] == "target_reached"
        assert result_dict["confidence"] == 1.0

    def test_should_stop_refining_target_reached(self, detector):
        """Test should_stop_refining when target reached"""
        result = ConvergenceResult(
            has_converged=True,
            reason=ConvergenceReason.TARGET_REACHED,
            confidence=1.0
        )

        should_stop = detector.should_stop_refining(result, attempt_number=2, max_attempts=5)

        assert should_stop is True

    def test_should_stop_refining_max_attempts(self, detector):
        """Test should_stop_refining when max attempts reached"""
        result = ConvergenceResult(has_converged=False)

        should_stop = detector.should_stop_refining(result, attempt_number=5, max_attempts=5)

        assert should_stop is True

    def test_should_stop_refining_high_confidence(self, detector):
        """Test should_stop_refining with high confidence convergence"""
        result = ConvergenceResult(
            has_converged=True,
            reason=ConvergenceReason.SCORE_PLATEAU,
            confidence=0.9
        )

        should_stop = detector.should_stop_refining(result, attempt_number=3, max_attempts=5)

        assert should_stop is True

    def test_should_stop_refining_low_confidence(self, detector):
        """Test should_stop_refining with low confidence convergence"""
        result = ConvergenceResult(
            has_converged=True,
            reason=ConvergenceReason.SCORE_PLATEAU,
            confidence=0.5
        )

        should_stop = detector.should_stop_refining(result, attempt_number=3, max_attempts=5)

        assert should_stop is False

    def test_should_stop_refining_continue(self, detector):
        """Test should_stop_refining when should continue"""
        result = ConvergenceResult(has_converged=False)

        should_stop = detector.should_stop_refining(result, attempt_number=2, max_attempts=5)

        assert should_stop is False

    def test_custom_thresholds(self):
        """Test detector with custom thresholds"""
        detector = ConvergenceDetector(
            score_plateau_threshold=0.05,
            min_similarity_for_loop=0.9,
            lookback_window=2
        )

        assert detector.score_plateau_threshold == 0.05
        assert detector.min_similarity_for_loop == 0.9
        assert detector.lookback_window == 2

    def test_detect_plateau_insufficient_history(self, detector):
        """Test plateau detection with insufficient history"""
        history = [
            {"attempt": 1, "score": 8.0, "code": "code1"}
        ]

        result = detector._detect_score_plateau(history)

        assert result.has_converged is False

    def test_detect_minimal_changes_insufficient_history(self, detector):
        """Test minimal changes detection with insufficient history"""
        history = [{"attempt": 1, "score": 8.0, "code": "code1"}]

        result = detector._detect_minimal_changes(history)

        assert result.has_converged is False

    def test_detect_loop_insufficient_history(self, detector):
        """Test loop detection with insufficient history"""
        history = [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 8.1, "code": "code2"}
        ]

        result = detector._detect_infinite_loop(history)

        assert result.has_converged is False

    def test_calculate_code_similarity(self, detector):
        """Test code similarity calculation"""
        code1 = "def test():\n    pass"
        code2 = "def test():\n    pass"

        similarity = detector._calculate_code_similarity(code1, code2)

        assert similarity == 1.0

    def test_calculate_code_similarity_different(self, detector):
        """Test code similarity with different codes"""
        code1 = "def test1():\n    pass"
        code2 = "def test2():\n    return 1"

        similarity = detector._calculate_code_similarity(code1, code2)

        assert 0.0 < similarity < 1.0

    def test_detect_with_improving_scores(self, detector):
        """Test detect with steadily improving scores"""
        history = [
            {"attempt": 1, "score": 8.0, "code": "code1"},
            {"attempt": 2, "score": 8.5, "code": "code2"},
            {"attempt": 3, "score": 9.0, "code": "code3"}
        ]

        result = detector.detect(history, target_score=9.5)

        assert result.has_converged is False

    def test_convergence_result_with_none_reason(self):
        """Test ConvergenceResult with None reason"""
        result = ConvergenceResult(has_converged=False)

        result_dict = result.to_dict()

        assert result_dict["reason"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
