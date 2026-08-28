"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.process_intelligence_integration

Purpose:
    Provide a deterministic integration boundary between the Process
    Intelligence subsystem and the Enterprise AI Orchestration layer.

Milestone:
    Milestone 5 - Process Intelligence
    Milestone 3 - Enterprise AI Orchestration Layer

Phase:
    Phase 5.9 - Orchestration Integration

Responsibilities:
    - Consume Process Intelligence outputs read-only.
    - Validate Process Intelligence integration inputs.
    - Preserve Process Intelligence result data.
    - Integrate KPI predictions, optimization recommendations, and
      digital-twin snapshots into an orchestration-safe analytical result.
    - Preserve governance boundaries.
    - Avoid autonomous execution.
    - Avoid modifying source Process Intelligence objects.
    - Provide deterministic integration behavior.
    - Preserve backward compatibility with the existing orchestration engine.

Important:
    This module is an integration adapter only.

    It does NOT:
        - execute orchestration requests,
        - call OrchestrationEngine.orchestrate(),
        - invoke ExecutionManager,
        - invoke GovernedExecution,
        - bypass Governance,
        - execute optimization recommendations,
        - modify Process Intelligence results,
        - modify digital-twin snapshots,
        - invoke an LLM,
        - make autonomous operational decisions.

The authoritative orchestration execution path remains:

    Request
       |
       v
    OrchestrationEngine
       |
       v
    Planner
       |
       v
    GovernedExecution
       |
       v
    GovernanceDecisionBoundary
       |
       v
    ExecutionManager
       |
       v
    Agent

Process Intelligence is consumed as analytical information only.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from src.process_intelligence import (
    DigitalTwinState,
    DigitalTwinTransition,
    ProcessDigitalTwinSnapshot,
    ProcessIntelligenceFinding,
    ProcessIntelligenceResult,
    ProcessKpiPrediction,
    ProcessOptimizationRecommendation,
)


# =============================================================================
# Exceptions
# =============================================================================


class ProcessIntelligenceOrchestrationError(ValueError):
    """
    Raised when Process Intelligence integration validation fails.
    """

    pass


# =============================================================================
# Integrated Analytical Result
# =============================================================================


@dataclass(frozen=True)
class ProcessIntelligenceOrchestrationResult:
    """
    Immutable orchestration-safe representation of Process Intelligence data.

    This object contains analytical information only.

    It does not contain an execution instruction and cannot itself trigger
    orchestration, governance, or agent execution.
    """

    process_id: str
    operation: str
    status: str
    findings: tuple[ProcessIntelligenceFinding, ...]
    metrics: dict[str, Any]
    kpi_predictions: tuple[ProcessKpiPrediction, ...]
    optimization_recommendations: tuple[
        ProcessOptimizationRecommendation,
        ...
    ]
    digital_twin_snapshot: ProcessDigitalTwinSnapshot | None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.process_id, str)
            or not self.process_id.strip()
        ):
            raise ProcessIntelligenceOrchestrationError(
                "process_id must be a non-empty string."
            )

        if (
            not isinstance(self.operation, str)
            or not self.operation.strip()
        ):
            raise ProcessIntelligenceOrchestrationError(
                "operation must be a non-empty string."
            )

        if (
            not isinstance(self.status, str)
            or not self.status.strip()
        ):
            raise ProcessIntelligenceOrchestrationError(
                "status must be a non-empty string."
            )

        if not isinstance(self.findings, tuple):
            raise ProcessIntelligenceOrchestrationError(
                "findings must be a tuple."
            )

        for finding in self.findings:
            if not isinstance(
                finding,
                ProcessIntelligenceFinding,
            ):
                raise ProcessIntelligenceOrchestrationError(
                    "findings must contain only "
                    "ProcessIntelligenceFinding objects."
                )

        if not isinstance(self.metrics, dict):
            raise ProcessIntelligenceOrchestrationError(
                "metrics must be a dictionary."
            )

        if not isinstance(self.kpi_predictions, tuple):
            raise ProcessIntelligenceOrchestrationError(
                "kpi_predictions must be a tuple."
            )

        for prediction in self.kpi_predictions:
            if not isinstance(
                prediction,
                ProcessKpiPrediction,
            ):
                raise ProcessIntelligenceOrchestrationError(
                    "kpi_predictions must contain only "
                    "ProcessKpiPrediction objects."
                )

        if not isinstance(
            self.optimization_recommendations,
            tuple,
        ):
            raise ProcessIntelligenceOrchestrationError(
                "optimization_recommendations must be a tuple."
            )

        for recommendation in self.optimization_recommendations:
            if not isinstance(
                recommendation,
                ProcessOptimizationRecommendation,
            ):
                raise ProcessIntelligenceOrchestrationError(
                    "optimization_recommendations must contain only "
                    "ProcessOptimizationRecommendation objects."
                )

        if (
            self.digital_twin_snapshot is not None
            and not isinstance(
                self.digital_twin_snapshot,
                ProcessDigitalTwinSnapshot,
            )
        ):
            raise ProcessIntelligenceOrchestrationError(
                "digital_twin_snapshot must be a "
                "ProcessDigitalTwinSnapshot or None."
            )

        object.__setattr__(
            self,
            "process_id",
            self.process_id.strip(),
        )

        object.__setattr__(
            self,
            "operation",
            self.operation.strip(),
        )

        object.__setattr__(
            self,
            "status",
            self.status.strip(),
        )

        # Defensive copy of the metrics mapping.
        object.__setattr__(
            self,
            "metrics",
            dict(self.metrics),
        )

    @property
    def finding_count(self) -> int:
        """
        Return the number of Process Intelligence findings.
        """
        return len(self.findings)

    @property
    def prediction_count(self) -> int:
        """
        Return the number of KPI predictions.
        """
        return len(self.kpi_predictions)

    @property
    def recommendation_count(self) -> int:
        """
        Return the number of optimization recommendations.
        """
        return len(self.optimization_recommendations)

    @property
    def has_digital_twin(self) -> bool:
        """
        Return whether a digital-twin snapshot is attached.
        """
        return self.digital_twin_snapshot is not None

    def to_dict(self) -> dict[str, Any]:
        """
        Return a deterministic serializable representation.
        """
        return {
            "process_id": self.process_id,
            "operation": self.operation,
            "status": self.status,
            "findings": [
                finding.to_dict()
                for finding in self.findings
            ],
            "metrics": dict(self.metrics),
            "kpi_predictions": [
                prediction.to_dict()
                for prediction in self.kpi_predictions
            ],
            "optimization_recommendations": [
                recommendation.to_dict()
                for recommendation in self.optimization_recommendations
            ],
            "digital_twin_snapshot": (
                self.digital_twin_snapshot.to_dict()
                if self.digital_twin_snapshot is not None
                else None
            ),
            "finding_count": self.finding_count,
            "prediction_count": self.prediction_count,
            "recommendation_count": self.recommendation_count,
            "has_digital_twin": self.has_digital_twin,
        }


# =============================================================================
# Process Intelligence Integration
# =============================================================================


class ProcessIntelligenceIntegration:
    """
    Deterministic read-only adapter for Process Intelligence outputs.

    The adapter does not execute anything.

    Its sole responsibility is to validate and package Process Intelligence
    outputs into a stable object that can safely be consumed by orchestration
    workflows, approval workflows, reporting layers, or future decision
    boundaries.
    """

    def integrate(
        self,
        process_intelligence_result: ProcessIntelligenceResult,
        kpi_predictions: Iterable[ProcessKpiPrediction] = (),
        optimization_recommendations: Iterable[
            ProcessOptimizationRecommendation
        ] = (),
        digital_twin_snapshot: ProcessDigitalTwinSnapshot | None = None,
    ) -> ProcessIntelligenceOrchestrationResult:
        """
        Integrate Process Intelligence outputs without executing them.

        Parameters
        ----------
        process_intelligence_result:
            Primary Process Intelligence analysis result.

        kpi_predictions:
            Optional deterministic KPI predictions.

        optimization_recommendations:
            Optional deterministic optimization recommendations.

        digital_twin_snapshot:
            Optional deterministic digital-twin snapshot.

        Returns
        -------
        ProcessIntelligenceOrchestrationResult
            Immutable orchestration-safe analytical result.

        Raises
        ------
        ProcessIntelligenceOrchestrationError
            If any input violates the integration contract.
        """

        validated_result = self._validate_process_intelligence_result(
            process_intelligence_result
        )

        validated_predictions = self._validate_kpi_predictions(
            kpi_predictions
        )

        validated_recommendations = (
            self._validate_optimization_recommendations(
                optimization_recommendations
            )
        )

        validated_snapshot = self._validate_digital_twin_snapshot(
            digital_twin_snapshot
        )

        return ProcessIntelligenceOrchestrationResult(
            process_id=validated_result.process_id,
            operation=validated_result.operation,
            status=validated_result.status,
            findings=tuple(
                self._copy_finding(finding)
                for finding in validated_result.findings
            ),
            metrics=dict(validated_result.metrics),
            kpi_predictions=tuple(
                self._copy_kpi_prediction(prediction)
                for prediction in validated_predictions
            ),
            optimization_recommendations=tuple(
                self._copy_optimization_recommendation(
                    recommendation
                )
                for recommendation in validated_recommendations
            ),
            digital_twin_snapshot=(
                self._copy_digital_twin_snapshot(
                    validated_snapshot
                )
                if validated_snapshot is not None
                else None
            ),
        )

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def _validate_process_intelligence_result(
        result: ProcessIntelligenceResult,
    ) -> ProcessIntelligenceResult:
        if not isinstance(
            result,
            ProcessIntelligenceResult,
        ):
            raise ProcessIntelligenceOrchestrationError(
                "process_intelligence_result must be a "
                "ProcessIntelligenceResult."
            )

        return result

    @staticmethod
    def _validate_kpi_predictions(
        predictions: Iterable[ProcessKpiPrediction],
    ) -> tuple[ProcessKpiPrediction, ...]:
        if isinstance(predictions, (str, bytes)):
            raise ProcessIntelligenceOrchestrationError(
                "kpi_predictions must be an iterable of "
                "ProcessKpiPrediction objects."
            )

        try:
            materialized = tuple(predictions)
        except TypeError as exc:
            raise ProcessIntelligenceOrchestrationError(
                "kpi_predictions must be an iterable of "
                "ProcessKpiPrediction objects."
            ) from exc

        for prediction in materialized:
            if not isinstance(
                prediction,
                ProcessKpiPrediction,
            ):
                raise ProcessIntelligenceOrchestrationError(
                    "kpi_predictions must contain only "
                    "ProcessKpiPrediction objects."
                )

        return materialized

    @staticmethod
    def _validate_optimization_recommendations(
        recommendations: Iterable[
            ProcessOptimizationRecommendation
        ],
    ) -> tuple[ProcessOptimizationRecommendation, ...]:
        if isinstance(recommendations, (str, bytes)):
            raise ProcessIntelligenceOrchestrationError(
                "optimization_recommendations must be an iterable of "
                "ProcessOptimizationRecommendation objects."
            )

        try:
            materialized = tuple(recommendations)
        except TypeError as exc:
            raise ProcessIntelligenceOrchestrationError(
                "optimization_recommendations must be an iterable of "
                "ProcessOptimizationRecommendation objects."
            ) from exc

        for recommendation in materialized:
            if not isinstance(
                recommendation,
                ProcessOptimizationRecommendation,
            ):
                raise ProcessIntelligenceOrchestrationError(
                    "optimization_recommendations must contain only "
                    "ProcessOptimizationRecommendation objects."
                )

        return materialized

    @staticmethod
    def _validate_digital_twin_snapshot(
        snapshot: ProcessDigitalTwinSnapshot | None,
    ) -> ProcessDigitalTwinSnapshot | None:
        if snapshot is None:
            return None

        if not isinstance(
            snapshot,
            ProcessDigitalTwinSnapshot,
        ):
            raise ProcessIntelligenceOrchestrationError(
                "digital_twin_snapshot must be a "
                "ProcessDigitalTwinSnapshot or None."
            )

        return snapshot

    # =========================================================================
    # Defensive Copies
    # =========================================================================

    @staticmethod
    def _copy_finding(
        finding: ProcessIntelligenceFinding,
    ) -> ProcessIntelligenceFinding:
        return ProcessIntelligenceFinding(
            finding_type=finding.finding_type,
            description=finding.description,
            severity=finding.severity,
            confidence=finding.confidence,
            evidence=dict(finding.evidence),
        )

    @staticmethod
    def _copy_kpi_prediction(
        prediction: ProcessKpiPrediction,
    ) -> ProcessKpiPrediction:
        return ProcessKpiPrediction(
            metric=prediction.metric,
            predicted_value=prediction.predicted_value,
            confidence=prediction.confidence,
            horizon=prediction.horizon,
        )

    @staticmethod
    def _copy_optimization_recommendation(
        recommendation: ProcessOptimizationRecommendation,
    ) -> ProcessOptimizationRecommendation:
        return ProcessOptimizationRecommendation(
            recommendation=recommendation.recommendation,
            rationale=recommendation.rationale,
            expected_impact=recommendation.expected_impact,
            confidence=recommendation.confidence,
        )

    @staticmethod
    def _copy_digital_twin_snapshot(
        snapshot: ProcessDigitalTwinSnapshot,
    ) -> ProcessDigitalTwinSnapshot:
        states = tuple(
            DigitalTwinState(
                state_name=state.state_name,
                observation_count=state.observation_count,
                active=state.active,
            )
            for state in snapshot.states
        )

        transitions = tuple(
            DigitalTwinTransition(
                source_state=transition.source_state,
                target_state=transition.target_state,
                occurrence_count=transition.occurrence_count,
            )
            for transition in snapshot.transitions
        )

        return ProcessDigitalTwinSnapshot(
            process_name=snapshot.process_name,
            states=states,
            transitions=transitions,
            total_observations=snapshot.total_observations,
            active_state_count=snapshot.active_state_count,
            transition_count=snapshot.transition_count,
            total_transition_occurrences=(
                snapshot.total_transition_occurrences
            ),
        )


# =============================================================================
# Convenience API
# =============================================================================


def integrate_process_intelligence(
    process_intelligence_result: ProcessIntelligenceResult,
    kpi_predictions: Iterable[ProcessKpiPrediction] = (),
    optimization_recommendations: Iterable[
        ProcessOptimizationRecommendation
    ] = (),
    digital_twin_snapshot: ProcessDigitalTwinSnapshot | None = None,
) -> ProcessIntelligenceOrchestrationResult:
    """
    Convenience API for deterministic Process Intelligence integration.

    No orchestration execution is performed.
    """
    return ProcessIntelligenceIntegration().integrate(
        process_intelligence_result=process_intelligence_result,
        kpi_predictions=kpi_predictions,
        optimization_recommendations=optimization_recommendations,
        digital_twin_snapshot=digital_twin_snapshot,
    )


# =============================================================================
# Public Module API
# =============================================================================


__all__ = [
    "ProcessIntelligenceOrchestrationError",
    "ProcessIntelligenceOrchestrationResult",
    "ProcessIntelligenceIntegration",
    "integrate_process_intelligence",
]