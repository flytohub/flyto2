"""
Convergence Detector Component

Detects when refinement process has converged or is stuck.
Zero coupling - pure function design with dependency injection.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ConvergenceReason(Enum):
    """Reasons for convergence"""
    SCORE_PLATEAU = "score_plateau"
    MINIMAL_CHANGES = "minimal_changes"
    INFINITE_LOOP = "infinite_loop"
    NO_IMPROVEMENT = "no_improvement"
    TARGET_REACHED = "target_reached"


@dataclass
class ConvergenceResult:
    """
    Result of convergence detection

    Attributes:
        has_converged: Whether convergence has been detected
        reason: Reason for convergence (if converged)
        confidence: Confidence level (0.0 to 1.0)
        details: Additional details about the convergence
    """
    has_converged: bool
    reason: Optional[ConvergenceReason] = None
    confidence: float = 0.0
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "has_converged": self.has_converged,
            "reason": self.reason.value if self.reason else None,
            "confidence": self.confidence,
            "details": self.details or {}
        }


class ConvergenceDetector:
    """
    Detects convergence in refinement process

    Pure, stateless component with zero coupling.
    All dependencies injected through constructor or method parameters.
    """

    def __init__(
        self,
        score_plateau_threshold: float = 0.1,
        min_similarity_for_loop: float = 0.95,
        lookback_window: int = 3
    ):
        """
        Initialize detector with thresholds

        Args:
            score_plateau_threshold: Max score change to consider as plateau
            min_similarity_for_loop: Min code similarity to detect loop
            lookback_window: Number of previous attempts to analyze
        """
        self.score_plateau_threshold = score_plateau_threshold
        self.min_similarity_for_loop = min_similarity_for_loop
        self.lookback_window = lookback_window

    def detect(
        self,
        attempt_history: List[Dict[str, Any]],
        target_score: float = 9.5,
        max_attempts: int = 5
    ) -> ConvergenceResult:
        """
        Detect if refinement has converged

        Args:
            attempt_history: List of attempt results, each containing:
                {
                    "attempt": int,
                    "score": float,
                    "code": str,
                    "issues": List[Dict],
                    "similarity_to_previous": float (optional)
                }
            target_score: Target quality score
            max_attempts: Maximum allowed attempts

        Returns:
            ConvergenceResult indicating if converged and why
        """
        if not attempt_history:
            return ConvergenceResult(has_converged=False)

        current = attempt_history[-1]
        current_score = current.get("score", 0.0)

        # Check if target reached
        if current_score >= target_score:
            return ConvergenceResult(
                has_converged=True,
                reason=ConvergenceReason.TARGET_REACHED,
                confidence=1.0,
                details={"current_score": current_score, "target_score": target_score}
            )

        # Need at least 2 attempts for other checks
        if len(attempt_history) < 2:
            return ConvergenceResult(has_converged=False)

        # Check for score plateau
        plateau_result = self._detect_score_plateau(attempt_history)
        if plateau_result.has_converged:
            return plateau_result

        # Check for minimal changes
        minimal_result = self._detect_minimal_changes(attempt_history)
        if minimal_result.has_converged:
            return minimal_result

        # Check for infinite loop
        loop_result = self._detect_infinite_loop(attempt_history)
        if loop_result.has_converged:
            return loop_result

        # Check for no improvement
        no_improvement_result = self._detect_no_improvement(attempt_history)
        if no_improvement_result.has_converged:
            return no_improvement_result

        return ConvergenceResult(has_converged=False)

    def _detect_score_plateau(
        self,
        attempt_history: List[Dict[str, Any]]
    ) -> ConvergenceResult:
        """
        Detect if score has plateaued

        Args:
            attempt_history: List of attempt results

        Returns:
            ConvergenceResult
        """
        if len(attempt_history) < self.lookback_window:
            return ConvergenceResult(has_converged=False)

        # Get recent scores
        recent_scores = [
            attempt.get("score", 0.0)
            for attempt in attempt_history[-self.lookback_window:]
        ]

        # Calculate score variation
        max_score = max(recent_scores)
        min_score = min(recent_scores)
        variation = max_score - min_score

        # Check if variation is below threshold
        if variation <= self.score_plateau_threshold:
            return ConvergenceResult(
                has_converged=True,
                reason=ConvergenceReason.SCORE_PLATEAU,
                confidence=1.0 - (variation / self.score_plateau_threshold),
                details={
                    "score_variation": variation,
                    "recent_scores": recent_scores,
                    "threshold": self.score_plateau_threshold
                }
            )

        return ConvergenceResult(has_converged=False)

    def _detect_minimal_changes(
        self,
        attempt_history: List[Dict[str, Any]]
    ) -> ConvergenceResult:
        """
        Detect if code changes are minimal

        Args:
            attempt_history: List of attempt results

        Returns:
            ConvergenceResult
        """
        if len(attempt_history) < 2:
            return ConvergenceResult(has_converged=False)

        # Check similarity to previous attempt
        current = attempt_history[-1]
        similarity = current.get("similarity_to_previous", 0.0)

        # High similarity means minimal changes
        if similarity >= 0.99:
            return ConvergenceResult(
                has_converged=True,
                reason=ConvergenceReason.MINIMAL_CHANGES,
                confidence=similarity,
                details={
                    "similarity": similarity,
                    "threshold": 0.99
                }
            )

        return ConvergenceResult(has_converged=False)

    def _detect_infinite_loop(
        self,
        attempt_history: List[Dict[str, Any]]
    ) -> ConvergenceResult:
        """
        Detect if refinement is stuck in a loop

        Args:
            attempt_history: List of attempt results

        Returns:
            ConvergenceResult
        """
        if len(attempt_history) < 3:
            return ConvergenceResult(has_converged=False)

        current = attempt_history[-1]
        current_code = current.get("code", "")

        # Check if current code matches any previous attempt
        for i, prev_attempt in enumerate(attempt_history[:-1]):
            prev_code = prev_attempt.get("code", "")

            # Calculate similarity
            if current_code and prev_code:
                similarity = self._calculate_code_similarity(current_code, prev_code)

                if similarity >= self.min_similarity_for_loop:
                    return ConvergenceResult(
                        has_converged=True,
                        reason=ConvergenceReason.INFINITE_LOOP,
                        confidence=similarity,
                        details={
                            "loop_detected_at_attempt": i + 1,
                            "current_attempt": len(attempt_history),
                            "similarity": similarity
                        }
                    )

        return ConvergenceResult(has_converged=False)

    def _detect_no_improvement(
        self,
        attempt_history: List[Dict[str, Any]]
    ) -> ConvergenceResult:
        """
        Detect if there's no improvement over multiple attempts

        Args:
            attempt_history: List of attempt results

        Returns:
            ConvergenceResult
        """
        if len(attempt_history) < self.lookback_window:
            return ConvergenceResult(has_converged=False)

        # Get recent scores
        recent_scores = [
            attempt.get("score", 0.0)
            for attempt in attempt_history[-self.lookback_window:]
        ]

        # Check if all scores are the same or decreasing
        first_score = recent_scores[0]
        all_same_or_worse = all(score <= first_score for score in recent_scores[1:])

        if all_same_or_worse:
            # Calculate confidence based on how many attempts showed no improvement
            confidence = len(recent_scores) / (self.lookback_window * 2)
            confidence = min(confidence, 1.0)

            return ConvergenceResult(
                has_converged=True,
                reason=ConvergenceReason.NO_IMPROVEMENT,
                confidence=confidence,
                details={
                    "recent_scores": recent_scores,
                    "attempts_without_improvement": len(recent_scores)
                }
            )

        return ConvergenceResult(has_converged=False)

    def _calculate_code_similarity(self, code1: str, code2: str) -> float:
        """
        Calculate similarity between two code strings

        Args:
            code1: First code string
            code2: Second code string

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        import difflib
        return difflib.SequenceMatcher(None, code1, code2).ratio()

    def should_stop_refining(
        self,
        convergence_result: ConvergenceResult,
        attempt_number: int,
        max_attempts: int
    ) -> bool:
        """
        Determine if refinement should stop

        Args:
            convergence_result: Result from detect()
            attempt_number: Current attempt number
            max_attempts: Maximum allowed attempts

        Returns:
            True if refinement should stop
        """
        # Always stop if target reached
        if (convergence_result.has_converged and
            convergence_result.reason == ConvergenceReason.TARGET_REACHED):
            return True

        # Stop if max attempts reached
        if attempt_number >= max_attempts:
            return True

        # Stop if converged with high confidence
        if convergence_result.has_converged and convergence_result.confidence >= 0.8:
            return True

        return False
