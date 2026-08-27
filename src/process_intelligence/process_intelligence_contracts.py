"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence_contracts.py

Purpose:
    Define the public contracts used by the Process Intelligence subsystem.

Milestone:
    Milestone 5 - Process Intelligence

Phase:
    Phase 5.1 - Define Process Intelligence Contracts

Responsibilities:
    - Define immutable Process Intelligence request contracts
    - Define process observation contracts
    - Define process finding contracts
    - Define Process Intelligence result contracts
    - Define KPI prediction contracts
    - Define optimization recommendation contracts
    - Define digital twin reference contracts
    - Provide deterministic validation
    - Provide serialization through to_dict()

Design principles:
    - Explicit contracts
    - Immutable public objects
    - Fail-fast validation
    - No dependency on implementation engines
    - Stable public API
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


# =============================================================================
# Exceptions
# =============================================================================


class ProcessIntelligenceContractError(ValueError):
    """
    Raised when a Process Intelligence contract violates its invariants.
    """


# =============================================================================
# Internal validation helpers
# =============================================================================


def _require_non_empty_string(value: Any, field_name: str) -> str:
    """
    Validate and return a non-empty string.
    """
    if not isinstance(value, str) or not value.strip():
        raise ProcessIntelligenceContractError(
            f"{field_name} must be a non-empty string."
        )

    return value


def _require_mapping(
    value: Any,
    field_name: str,
) -> Mapping[str, Any]:
    """
    Validate and return a mapping.
    """
    if not isinstance(value, Mapping):
        raise ProcessIntelligenceContractError(
            f"{field_name} must be a mapping."
        )

    return value


def _require_confidence(
    value: Any,
    field_name: str = "confidence",
) -> float:
    """
    Validate a confidence score.

    Confidence must be numeric and within the inclusive range [0, 1].
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProcessIntelligenceContractError(
            f"{field_name} must be a number between 0 and 1."
        )

    confidence = float(value)

    if not 0.0 <= confidence <= 1.0:
        raise ProcessIntelligenceContractError(
            f"{field_name} must be between 0 and 1."
        )

    return confidence


def _freeze_mapping(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Create a defensive copy of a mapping.

    The public dataclasses themselves are immutable. This helper also avoids
    retaining the caller's original mapping object.
    """
    return dict(value)


# =============================================================================
# Process Intelligence Request
# =============================================================================


@dataclass(frozen=True, slots=True)
class ProcessIntelligenceRequest:
    """
    Request submitted to the Process Intelligence subsystem.
    """

    operation: str
    process_id: str
    process_data: Mapping[str, Any]
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.operation,
            "operation",
        )

        _require_non_empty_string(
            self.process_id,
            "process_id",
        )

        process_data = _require_mapping(
            self.process_data,
            "process_data",
        )

        context = _require_mapping(
            self.context,
            "context",
        )

        object.__setattr__(
            self,
            "process_data",
            _freeze_mapping(process_data),
        )

        object.__setattr__(
            self,
            "context",
            _freeze_mapping(context),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the request into a plain dictionary.
        """
        return {
            "operation": self.operation,
            "process_id": self.process_id,
            "process_data": dict(self.process_data),
            "context": dict(self.context),
        }


# =============================================================================
# Process Observation
# =============================================================================


@dataclass(frozen=True, slots=True)
class ProcessObservation:
    """
    Observation of an activity occurring within a process case.
    """

    case_id: str
    activity: str
    timestamp: str
    resource: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.case_id,
            "case_id",
        )

        _require_non_empty_string(
            self.activity,
            "activity",
        )

        _require_non_empty_string(
            self.timestamp,
            "timestamp",
        )

        if self.resource is not None:
            _require_non_empty_string(
                self.resource,
                "resource",
            )

        attributes = _require_mapping(
            self.attributes,
            "attributes",
        )

        object.__setattr__(
            self,
            "attributes",
            _freeze_mapping(attributes),
        )


# =============================================================================
# Process Intelligence Finding
# =============================================================================


@dataclass(frozen=True, slots=True)
class ProcessIntelligenceFinding:
    """
    Finding produced by Process Intelligence analysis.
    """

    finding_type: str
    description: str
    severity: str = "info"
    confidence: float = 1.0
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.finding_type,
            "finding_type",
        )

        _require_non_empty_string(
            self.description,
            "description",
        )

        _require_non_empty_string(
            self.severity,
            "severity",
        )

        confidence = _require_confidence(
            self.confidence,
        )

        evidence = _require_mapping(
            self.evidence,
            "evidence",
        )

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "evidence",
            _freeze_mapping(evidence),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the finding into a plain dictionary.
        """
        return {
            "finding_type": self.finding_type,
            "description": self.description,
            "severity": self.severity,
            "confidence": self.confidence,
            "evidence": dict(self.evidence),
        }


# =============================================================================
# Process Intelligence Result
# =============================================================================


@dataclass(frozen=True, slots=True)
class ProcessIntelligenceResult:
    """
    Result returned by a Process Intelligence operation.
    """

    operation: str
    process_id: str
    status: str
    findings: tuple[ProcessIntelligenceFinding, ...] = ()
    metrics: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.operation,
            "operation",
        )

        _require_non_empty_string(
            self.process_id,
            "process_id",
        )

        _require_non_empty_string(
            self.status,
            "status",
        )

        if not isinstance(self.findings, tuple):
            raise ProcessIntelligenceContractError(
                "findings must be a tuple."
            )

        for finding in self.findings:
            if not isinstance(
                finding,
                ProcessIntelligenceFinding,
            ):
                raise ProcessIntelligenceContractError(
                    "findings must contain ProcessIntelligenceFinding objects."
                )

        metrics = _require_mapping(
            self.metrics,
            "metrics",
        )

        object.__setattr__(
            self,
            "metrics",
            _freeze_mapping(metrics),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the result into a plain dictionary.
        """
        return {
            "operation": self.operation,
            "process_id": self.process_id,
            "status": self.status,
            "findings": [
                finding.to_dict()
                for finding in self.findings
            ],
            "metrics": dict(self.metrics),
        }


# =============================================================================
# KPI Prediction
# =============================================================================


@dataclass(frozen=True, slots=True)
class ProcessKpiPrediction:
    """
    Predicted value for a Process Intelligence KPI.
    """

    metric: str
    predicted_value: float
    confidence: float
    horizon: str = "unknown"

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.metric,
            "metric",
        )

        if isinstance(self.predicted_value, bool) or not isinstance(
            self.predicted_value,
            (int, float),
        ):
            raise ProcessIntelligenceContractError(
                "predicted_value must be numeric."
            )

        _require_confidence(
            self.confidence,
        )

        _require_non_empty_string(
            self.horizon,
            "horizon",
        )

        object.__setattr__(
            self,
            "predicted_value",
            float(self.predicted_value),
        )

        object.__setattr__(
            self,
            "confidence",
            float(self.confidence),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the KPI prediction into a plain dictionary.
        """
        return {
            "metric": self.metric,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "horizon": self.horizon,
        }


# =============================================================================
# Process Optimization Recommendation
# =============================================================================


@dataclass(frozen=True, slots=True)
class ProcessOptimizationRecommendation:
    """
    Recommended process improvement produced by Process Intelligence.
    """

    recommendation: str
    rationale: str
    expected_impact: str = ""
    confidence: float = 1.0

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.recommendation,
            "recommendation",
        )

        _require_non_empty_string(
            self.rationale,
            "rationale",
        )

        if self.expected_impact:
            _require_non_empty_string(
                self.expected_impact,
                "expected_impact",
            )

        confidence = _require_confidence(
            self.confidence,
        )

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the recommendation into a plain dictionary.
        """
        return {
            "recommendation": self.recommendation,
            "rationale": self.rationale,
            "expected_impact": self.expected_impact,
            "confidence": self.confidence,
        }


# =============================================================================
# Digital Twin Reference
# =============================================================================


@dataclass(frozen=True, slots=True)
class DigitalTwinReference:
    """
    Reference to a Process Intelligence digital twin.
    """

    twin_id: str
    process_id: str
    version: str

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.twin_id,
            "twin_id",
        )

        _require_non_empty_string(
            self.process_id,
            "process_id",
        )

        _require_non_empty_string(
            self.version,
            "version",
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the digital twin reference.
        """
        return {
            "twin_id": self.twin_id,
            "process_id": self.process_id,
            "version": self.version,
        }