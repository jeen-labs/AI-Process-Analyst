"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_optimization

Purpose:
    Provide deterministic process optimization recommendations.

Milestone:
    Milestone 5 - Process Intelligence

Phase:
    Phase 5.7 - Process Optimization

Responsibilities:
    - Validate optimization inputs.
    - Identify deterministic improvement opportunities.
    - Generate optimization recommendations.
    - Calculate expected impact.
    - Assign deterministic confidence scores.
    - Preserve source-data immutability.

This module provides a deterministic optimization foundation.
It does not invoke an LLM, modify source process data, or execute
recommendations automatically.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


# =============================================================================
# Errors
# =============================================================================


class ProcessOptimizationError(ValueError):
    """
    Raised when a process optimization operation cannot be completed.
    """


# =============================================================================
# Optimization Recommendation
# =============================================================================


@dataclass(frozen=True)
class OptimizationRecommendation:
    """
    Represent one deterministic process optimization recommendation.

    Attributes:
        target:
            Name of the process element or KPI being optimized.

        current_value:
            Current observed value.

        target_value:
            Desired or improved value.

        expected_impact:
            Absolute expected improvement.

        improvement_percentage:
            Expected improvement expressed as a percentage.

        confidence:
            Deterministic confidence score between 0.0 and 1.0.

        recommendation:
            Human-readable optimization recommendation.

        method:
            Optimization method used.
    """

    target: str
    current_value: float
    target_value: float
    expected_impact: float
    improvement_percentage: float
    confidence: float
    recommendation: str
    method: str = "threshold_reduction"

    def __post_init__(self) -> None:
        if not isinstance(self.target, str) or not self.target.strip():
            raise ProcessOptimizationError(
                "target must be a non-empty string."
            )

        for field_name, value in (
            ("current_value", self.current_value),
            ("target_value", self.target_value),
            ("expected_impact", self.expected_impact),
            ("improvement_percentage", self.improvement_percentage),
            ("confidence", self.confidence),
        ):
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise ProcessOptimizationError(
                    f"{field_name} must be numeric."
                )

        if self.current_value < 0:
            raise ProcessOptimizationError(
                "current_value must be greater than or equal to zero."
            )

        if self.target_value < 0:
            raise ProcessOptimizationError(
                "target_value must be greater than or equal to zero."
            )

        if self.expected_impact < 0:
            raise ProcessOptimizationError(
                "expected_impact must be greater than or equal to zero."
            )

        if self.improvement_percentage < 0:
            raise ProcessOptimizationError(
                "improvement_percentage must be greater than or equal to zero."
            )

        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ProcessOptimizationError(
                "confidence must be between 0.0 and 1.0."
            )

        if (
            not isinstance(self.recommendation, str)
            or not self.recommendation.strip()
        ):
            raise ProcessOptimizationError(
                "recommendation must be a non-empty string."
            )

        if not isinstance(self.method, str) or not self.method.strip():
            raise ProcessOptimizationError(
                "method must be a non-empty string."
            )

    def to_dict(self) -> dict[str, object]:
        """
        Return a serializable representation of the recommendation.
        """
        return {
            "target": self.target,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "expected_impact": self.expected_impact,
            "improvement_percentage": self.improvement_percentage,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "method": self.method,
        }


# =============================================================================
# Optimization Result
# =============================================================================


@dataclass(frozen=True)
class ProcessOptimizationResult:
    """
    Represent the complete deterministic optimization result.
    """

    recommendations: tuple[OptimizationRecommendation, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.recommendations, tuple):
            raise ProcessOptimizationError(
                "recommendations must be a tuple of "
                "OptimizationRecommendation objects."
            )

        for recommendation in self.recommendations:
            if not isinstance(
                recommendation,
                OptimizationRecommendation,
            ):
                raise ProcessOptimizationError(
                    "recommendations must contain only "
                    "OptimizationRecommendation objects."
                )

    @property
    def count(self) -> int:
        """
        Return the number of optimization recommendations.
        """
        return len(self.recommendations)

    def to_dict(self) -> dict[str, object]:
        """
        Return a serializable representation of the optimization result.
        """
        return {
            "recommendations": [
                recommendation.to_dict()
                for recommendation in self.recommendations
            ]
        }


# =============================================================================
# Process Optimizer
# =============================================================================


class ProcessOptimizer:
    """
    Perform deterministic process optimization.

    The Phase 5.7 implementation identifies opportunities where a current
    value exceeds the desired target value. The optimizer recommends reducing
    the value to the target and calculates the expected impact.
    """

    def optimize(
        self,
        target: str,
        current_value: float,
        target_value: float,
        confidence: float = 0.8,
    ) -> OptimizationRecommendation:
        """
        Generate one deterministic optimization recommendation.
        """
        validated_target = self._validate_target(target)

        current = self._validate_numeric(
            "current_value",
            current_value,
        )

        desired = self._validate_numeric(
            "target_value",
            target_value,
        )

        validated_confidence = self._validate_confidence(
            confidence,
        )

        if current < 0:
            raise ProcessOptimizationError(
                "current_value must be greater than or equal to zero."
            )

        if desired < 0:
            raise ProcessOptimizationError(
                "target_value must be greater than or equal to zero."
            )

        if desired > current:
            raise ProcessOptimizationError(
                "target_value must not be greater than current_value."
            )

        expected_impact = current - desired

        improvement_percentage = self._calculate_improvement_percentage(
            current,
            expected_impact,
        )

        recommendation = self._build_recommendation(
            validated_target,
            current,
            desired,
            expected_impact,
        )

        return OptimizationRecommendation(
            target=validated_target,
            current_value=current,
            target_value=desired,
            expected_impact=expected_impact,
            improvement_percentage=improvement_percentage,
            confidence=validated_confidence,
            recommendation=recommendation,
        )

    def optimize_many(
        self,
        opportunities: dict[str, tuple[float, float]],
        confidence: float = 0.8,
    ) -> ProcessOptimizationResult:
        """
        Generate deterministic optimization recommendations for multiple
        optimization opportunities.

        Each dictionary value must contain:

            (current_value, target_value)
        """
        if not isinstance(opportunities, dict):
            raise ProcessOptimizationError(
                "opportunities must be a dictionary."
            )

        recommendations = tuple(
            self.optimize(
                target,
                values[0],
                values[1],
                confidence=confidence,
            )
            for target, values in opportunities.items()
        )

        return ProcessOptimizationResult(
            recommendations=recommendations,
        )

    @staticmethod
    def _validate_target(
        target: str,
    ) -> str:
        if not isinstance(target, str) or not target.strip():
            raise ProcessOptimizationError(
                "target must be a non-empty string."
            )

        return target.strip()

    @staticmethod
    def _validate_numeric(
        field_name: str,
        value: float,
    ) -> float:
        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise ProcessOptimizationError(
                f"{field_name} must be numeric."
            )

        return float(value)

    @staticmethod
    def _validate_confidence(
        confidence: float,
    ) -> float:
        if isinstance(confidence, bool) or not isinstance(
            confidence,
            (int, float),
        ):
            raise ProcessOptimizationError(
                "confidence must be numeric."
            )

        validated = float(confidence)

        if not 0.0 <= validated <= 1.0:
            raise ProcessOptimizationError(
                "confidence must be between 0.0 and 1.0."
            )

        return validated

    @staticmethod
    def _calculate_improvement_percentage(
        current_value: float,
        expected_impact: float,
    ) -> float:
        if current_value == 0.0:
            return 0.0

        return round(
            (expected_impact / current_value) * 100.0,
            6,
        )

    @staticmethod
    def _build_recommendation(
        target: str,
        current_value: float,
        target_value: float,
        expected_impact: float,
    ) -> str:
        if expected_impact == 0.0:
            return (
                f"{target} already meets the target value "
                f"of {target_value}."
            )

        return (
            f"Reduce {target} from {current_value} "
            f"to {target_value} to achieve an expected "
            f"improvement of {expected_impact}."
        )


# =============================================================================
# Convenience API
# =============================================================================


def optimize_process(
    target: str,
    current_value: float,
    target_value: float,
    confidence: float = 0.8,
) -> OptimizationRecommendation:
    """
    Convenience function for one deterministic optimization recommendation.
    """
    return ProcessOptimizer().optimize(
        target,
        current_value,
        target_value,
        confidence=confidence,
    )


def optimize_processes(
    opportunities: dict[str, tuple[float, float]],
    confidence: float = 0.8,
) -> ProcessOptimizationResult:
    """
    Convenience function for multiple deterministic recommendations.
    """
    return ProcessOptimizer().optimize_many(
        opportunities,
        confidence=confidence,
    )


# =============================================================================
# Public Module API
# =============================================================================


__all__ = [
    "ProcessOptimizationError",
    "OptimizationRecommendation",
    "ProcessOptimizationResult",
    "ProcessOptimizer",
    "optimize_process",
    "optimize_processes",
]