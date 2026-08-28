"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_kpi_prediction

Purpose:
    Provide deterministic KPI prediction over Process Intelligence data.

Milestone:
    Milestone 5 - Process Intelligence

Phase:
    Phase 5.6 - KPI Prediction

Responsibilities:
    - Validate KPI prediction inputs.
    - Calculate deterministic KPI forecasts from historical values.
    - Provide prediction metadata and confidence information.
    - Preserve immutability of prediction results.
    - Avoid modification of source Process Intelligence data.

This module intentionally provides a deterministic statistical foundation.
It does not invoke an LLM, modify process data, or perform process
optimization.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Iterable


# =============================================================================
# Errors
# =============================================================================


class ProcessKpiPredictionError(ValueError):
    """
    Raised when a KPI prediction operation cannot be completed.
    """


# =============================================================================
# KPI Prediction Contract
# =============================================================================


@dataclass(frozen=True)
class KpiPrediction:
    """
    Represent one deterministic KPI prediction.

    Attributes:
        kpi_name:
            Name of the KPI being predicted.

        predicted_value:
            Predicted KPI value.

        historical_average:
            Arithmetic mean of the historical observations.

        observation_count:
            Number of historical observations used.

        confidence:
            Deterministic confidence score between 0.0 and 1.0.

        method:
            Prediction method used.
    """

    kpi_name: str
    predicted_value: float
    historical_average: float
    observation_count: int
    confidence: float
    method: str = "historical_mean"

    def __post_init__(self) -> None:
        if not isinstance(self.kpi_name, str) or not self.kpi_name.strip():
            raise ProcessKpiPredictionError(
                "kpi_name must be a non-empty string."
            )

        if not isinstance(self.predicted_value, (int, float)):
            raise ProcessKpiPredictionError(
                "predicted_value must be numeric."
            )

        if not isinstance(self.historical_average, (int, float)):
            raise ProcessKpiPredictionError(
                "historical_average must be numeric."
            )

        if not isinstance(self.observation_count, int):
            raise ProcessKpiPredictionError(
                "observation_count must be an integer."
            )

        if self.observation_count <= 0:
            raise ProcessKpiPredictionError(
                "observation_count must be greater than zero."
            )

        if not isinstance(self.confidence, (int, float)):
            raise ProcessKpiPredictionError(
                "confidence must be numeric."
            )

        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ProcessKpiPredictionError(
                "confidence must be between 0.0 and 1.0."
            )

        if not isinstance(self.method, str) or not self.method.strip():
            raise ProcessKpiPredictionError(
                "method must be a non-empty string."
            )

    def to_dict(self) -> dict[str, object]:
        """
        Return a serializable representation of the prediction.
        """
        return {
            "kpi_name": self.kpi_name,
            "predicted_value": self.predicted_value,
            "historical_average": self.historical_average,
            "observation_count": self.observation_count,
            "confidence": self.confidence,
            "method": self.method,
        }


# =============================================================================
# KPI Prediction Result
# =============================================================================


@dataclass(frozen=True)
class ProcessKpiPredictionResult:
    """
    Represent the complete deterministic KPI prediction result.
    """

    predictions: tuple[KpiPrediction, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.predictions, tuple):
            raise ProcessKpiPredictionError(
                "predictions must be a tuple of KpiPrediction objects."
            )

        for prediction in self.predictions:
            if not isinstance(prediction, KpiPrediction):
                raise ProcessKpiPredictionError(
                    "predictions must contain only KpiPrediction objects."
                )

    @property
    def count(self) -> int:
        """
        Return the number of predictions.
        """
        return len(self.predictions)

    def to_dict(self) -> dict[str, object]:
        """
        Return a serializable representation of the result.
        """
        return {
            "predictions": [
                prediction.to_dict()
                for prediction in self.predictions
            ]
        }


# =============================================================================
# KPI Predictor
# =============================================================================


class ProcessKpiPredictor:
    """
    Perform deterministic KPI prediction.

    The initial Phase 5.6 implementation uses historical mean prediction.
    This establishes a stable prediction foundation without introducing
    nondeterministic machine-learning behavior.
    """

    def predict(
        self,
        kpi_name: str,
        historical_values: Iterable[float],
    ) -> KpiPrediction:
        """
        Predict the next KPI value from historical observations.

        The prediction is the arithmetic mean of the supplied historical
        observations.

        Confidence increases with the number of observations and decreases
        with historical variability.
        """
        if not isinstance(kpi_name, str) or not kpi_name.strip():
            raise ProcessKpiPredictionError(
                "kpi_name must be a non-empty string."
            )

        values = self._validate_values(historical_values)

        historical_average = mean(values)

        standard_deviation = self._population_standard_deviation(
            values,
            historical_average,
        )

        confidence = self._calculate_confidence(
            len(values),
            standard_deviation,
            historical_average,
        )

        return KpiPrediction(
            kpi_name=kpi_name.strip(),
            predicted_value=float(historical_average),
            historical_average=float(historical_average),
            observation_count=len(values),
            confidence=confidence,
        )

    def predict_many(
        self,
        historical_kpis: dict[str, Iterable[float]],
    ) -> ProcessKpiPredictionResult:
        """
        Predict multiple KPIs deterministically.
        """
        if not isinstance(historical_kpis, dict):
            raise ProcessKpiPredictionError(
                "historical_kpis must be a dictionary."
            )

        predictions = tuple(
            self.predict(kpi_name, values)
            for kpi_name, values in historical_kpis.items()
        )

        return ProcessKpiPredictionResult(
            predictions=predictions,
        )

    @staticmethod
    def _validate_values(
        historical_values: Iterable[float],
    ) -> tuple[float, ...]:
        if isinstance(historical_values, (str, bytes)):
            raise ProcessKpiPredictionError(
                "historical_values must be an iterable of numeric values."
            )

        try:
            values = tuple(historical_values)
        except TypeError as exc:
            raise ProcessKpiPredictionError(
                "historical_values must be an iterable of numeric values."
            ) from exc

        if not values:
            raise ProcessKpiPredictionError(
                "historical_values must contain at least one value."
            )

        validated: list[float] = []

        for value in values:
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise ProcessKpiPredictionError(
                    "historical_values must contain only numeric values."
                )

            validated.append(float(value))

        return tuple(validated)

    @staticmethod
    def _population_standard_deviation(
        values: tuple[float, ...],
        average: float,
    ) -> float:
        if len(values) == 1:
            return 0.0

        variance = sum(
            (value - average) ** 2
            for value in values
        ) / len(values)

        return sqrt(variance)

    @staticmethod
    def _calculate_confidence(
        observation_count: int,
        standard_deviation: float,
        historical_average: float,
    ) -> float:
        """
        Calculate a deterministic confidence score.

        Confidence is deliberately conservative:

        - More observations increase confidence.
        - Greater relative variability decreases confidence.
        - A stable series with sufficient observations approaches 1.0.
        """
        observation_factor = observation_count / (
            observation_count + 4.0
        )

        scale = abs(historical_average)

        if scale == 0.0:
            variability_factor = (
                1.0 if standard_deviation == 0.0 else 0.0
            )
        else:
            coefficient_of_variation = (
                standard_deviation / scale
            )
            variability_factor = 1.0 / (
                1.0 + coefficient_of_variation
            )

        confidence = observation_factor * variability_factor

        return round(
            max(0.0, min(1.0, confidence)),
            6,
        )


# =============================================================================
# Convenience API
# =============================================================================


def predict_kpi(
    kpi_name: str,
    historical_values: Iterable[float],
) -> KpiPrediction:
    """
    Convenience function for deterministic KPI prediction.
    """
    return ProcessKpiPredictor().predict(
        kpi_name,
        historical_values,
    )


def predict_kpis(
    historical_kpis: dict[str, Iterable[float]],
) -> ProcessKpiPredictionResult:
    """
    Convenience function for predicting multiple KPIs.
    """
    return ProcessKpiPredictor().predict_many(
        historical_kpis,
    )


# =============================================================================
# Public Module API
# =============================================================================


__all__ = [
    "ProcessKpiPredictionError",
    "KpiPrediction",
    "ProcessKpiPredictionResult",
    "ProcessKpiPredictor",
    "predict_kpi",
    "predict_kpis",
]